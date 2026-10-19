#!/usr/bin/env python3
"""Run the complete temporary Terraform lab and always attempt teardown."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
import urllib.request

import boto3
from botocore.exceptions import ClientError

parser=argparse.ArgumentParser()
parser.add_argument('--project',default='terraform-s3-demo')
args=parser.parse_args()
student=Path(__file__).resolve().parent.parent
project=(student/args.project).resolve()
evidence=student/'evidence'
evidence.mkdir(exist_ok=True)
region=os.environ.get('AWS_REGION','us-east-1')
session=boto3.Session(region_name=region)
session.client('sts').get_caller_identity()
env=os.environ|{'TF_IN_AUTOMATION':'1','AWS_PAGER':''}
output=None

def run(log,*command,check=True,timeout=480):
    line='$ '+shlex.join(command)
    print(line,flush=True)
    with log.open('a') as stream:
        stream.write('\n'+line+'\n');stream.flush()
        result=subprocess.run(command,cwd=project,env=env,stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,text=True,timeout=timeout)
        stream.write(result.stdout);stream.flush()
    print(result.stdout,end='',flush=True)
    if check and result.returncode:raise RuntimeError(f'Command exited {result.returncode}: {line}')
    return result

def tf(log,*arguments,**kwargs):return run(log,'terraform',*arguments,'-no-color',**kwargs)

started=datetime.now(timezone.utc).isoformat()
for name in ['01-validation.txt','02-plan.txt','03-apply.txt','04-verification.txt','05-destroy.txt','06-cleanup.txt']:
    (evidence/name).write_text('Run started: '+started+'\n')
try:
    tf(evidence/'01-validation.txt','init','-input=false')
    run(evidence/'01-validation.txt','terraform','fmt','-check')
    tf(evidence/'01-validation.txt','validate')
    tf(evidence/'02-plan.txt','plan','-input=false','-out=assignment.tfplan')
    tf(evidence/'03-apply.txt','apply','-input=false','assignment.tfplan')
    tf(evidence/'04-verification.txt','show')
    # The output and state subcommands accept global formatting flags before their arguments.
    result=run(evidence/'04-verification.txt','terraform','output','-json')
    output={name:value['value'] for name,value in json.loads(result.stdout).items()}
    (evidence/'outputs.json').write_text(json.dumps(output,indent=2)+'\n')
    run(evidence/'04-verification.txt','terraform','state','list')
    verification={'region':region,'bucket':output['bucket_name']}
    s3=session.client('s3')
    s3.head_bucket(Bucket=output['bucket_name'])
    verification['public_access_block']=s3.get_public_access_block(Bucket=output['bucket_name'])['PublicAccessBlockConfiguration']
    verification['encryption']=s3.get_bucket_encryption(Bucket=output['bucket_name'])['ServerSideEncryptionConfiguration']
    assert all(verification['public_access_block'].values())
    assert verification['encryption']['Rules'][0]['ApplyServerSideEncryptionByDefault']['SSEAlgorithm']=='AES256'
    if 'instance_id' in output:
        deadline=time.monotonic()+300
        while True:
            try:
                with urllib.request.urlopen(output['http_url'],timeout=8) as response:
                    html=response.read().decode()
                    assert response.status==200 and '24BCS10273' in html
                verification['http_status']=200;verification['http_response']=html
                break
            except (OSError,AssertionError):
                if time.monotonic()>deadline:raise
                time.sleep(5)
        body=s3.get_object(Bucket=output['bucket_name'],Key='assignment.txt')['Body'].read().decode()
        assert '24BCS10273' in body
        verification['s3_object']=body
        ec2=session.client('ec2')
        info=ec2.describe_instances(InstanceIds=[output['instance_id']])['Reservations'][0]['Instances'][0]
        verification['instance']={key:info[key] for key in ['InstanceId','InstanceType','State','ImageId','SubnetId','VpcId']}
        assert info['State']['Name']=='running'
    (evidence/'verification.json').write_text(json.dumps(verification,indent=2,default=str)+'\n')
    print(json.dumps(verification,indent=2,default=str),flush=True)
    print('PASS: AWS resources and required behavior verified.',flush=True)
finally:
    # This directory owns only this lab. Never import or destroy pre-existing resources.
    if (project/'.terraform').exists():
        try:
            tf(evidence/'05-destroy.txt','plan','-destroy','-input=false','-out=destroy.tfplan')
            tf(evidence/'05-destroy.txt','apply','-input=false','destroy.tfplan')
            # Explicit destroy command demonstrates that cleanup is idempotent.
            tf(evidence/'05-destroy.txt','destroy','-auto-approve','-input=false')
            state=run(evidence/'06-cleanup.txt','terraform','state','list')
            assert not state.stdout.strip(),'Managed resources remain in state'
            cleanup={'terraform_state_empty':True,'finished_at':datetime.now(timezone.utc).isoformat()}
            if output:
                try:
                    session.client('s3').head_bucket(Bucket=output['bucket_name'])
                    raise AssertionError('S3 bucket still exists')
                except ClientError as error:
                    assert error.response['Error']['Code'] in ['404','NoSuchBucket'],error
                    cleanup['bucket_deleted']=True
                if 'instance_id' in output:
                    ec2=session.client('ec2')
                    ec2.get_waiter('instance_terminated').wait(InstanceIds=[output['instance_id']],WaiterConfig={'Delay':5,'MaxAttempts':30})
                    cleanup['instance_terminated']=True
                    try:
                        ec2.describe_vpcs(VpcIds=[output['vpc_id']])
                        raise AssertionError('VPC still exists')
                    except ClientError as error:
                        assert error.response['Error']['Code']=='InvalidVpcID.NotFound',error
                        cleanup['vpc_deleted']=True
            (evidence/'cleanup.json').write_text(json.dumps(cleanup,indent=2)+'\n')
            with (evidence/'06-cleanup.txt').open('a') as stream:stream.write(json.dumps(cleanup,indent=2)+'\n')
            print(json.dumps(cleanup,indent=2),flush=True)
        except Exception:
            print('Cleanup failed. Preserve the private state and run terraform destroy in this exact project directory.',file=sys.stderr)
            raise
