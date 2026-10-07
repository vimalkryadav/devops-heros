#!/usr/bin/env python3
"""Apply and verify the six-resource network lab, then always attempt teardown."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import subprocess

import boto3
from botocore.exceptions import ClientError

student = Path(__file__).resolve().parent.parent
project = student / 'terraform-cloud-demo'
evidence = student / 'evidence'
evidence.mkdir(exist_ok=True)
session = boto3.Session(region_name=os.environ.get('AWS_REGION', 'us-east-1'))
ec2 = session.client('ec2')
session.client('sts').get_caller_identity()
env = os.environ | {'TF_IN_AUTOMATION': '1', 'AWS_PAGER': ''}
started = datetime.now(timezone.utc).isoformat()
for name in ['01-validation', '02-plan', '03-apply', '04-verification', '05-destroy', '06-cleanup']:
    (evidence / f'{name}.txt').write_text(f'Run started: {started}\n')

def run(log, *command):
    line = '$ ' + shlex.join(command)
    print(line, flush=True)
    result = subprocess.run(command, cwd=project, env=env, capture_output=True, text=True, timeout=480)
    with (evidence / f'{log}.txt').open('a') as stream:
        stream.write('\n' + line + '\n' + result.stdout + result.stderr)
    print(result.stdout + result.stderr, end='', flush=True)
    if result.returncode:
        raise RuntimeError(f'{line}: exit {result.returncode}')
    return result.stdout

def tf(log, action, *args):
    return run(log, 'terraform', action, '-no-color', *args)

# Check before entering the cleanup block: never destroy a pre-existing state.
if (project / 'terraform.tfstate').exists():
    assert not run('01-validation', 'terraform', 'state', 'list').strip(), 'Use an empty dedicated state'
outputs = {}
try:
    tf('01-validation', 'init', '-input=false')
    run('01-validation', 'terraform', 'fmt', '-check')
    tf('01-validation', 'validate')
    tf('02-plan', 'plan', '-input=false', '-out=assignment.tfplan')
    plan = json.loads(subprocess.check_output(['terraform', 'show', '-json', 'assignment.tfplan'], cwd=project, env=env))
    additions = [r for r in plan['resource_changes'] if r['mode'] == 'managed' and r['change']['actions'] == ['create']]
    assert len(additions) == 6, 'Expected exactly six network resources'
    tf('03-apply', 'apply', '-input=false', 'assignment.tfplan')
    tf('04-verification', 'show')
    raw = json.loads(run('04-verification', 'terraform', 'output', '-json'))
    outputs = {key: value['value'] for key, value in raw.items()}
    (evidence / 'outputs.json').write_text(json.dumps(outputs, indent=2) + '\n')
    state = run('04-verification', 'terraform', 'state', 'list').splitlines()
    assert len([line for line in state if not line.startswith('data.')]) == 6
    vpc = ec2.describe_vpcs(VpcIds=[outputs['vpc_id']])['Vpcs'][0]
    subnet = ec2.describe_subnets(SubnetIds=[outputs['subnet_id']])['Subnets'][0]
    gateway = ec2.describe_internet_gateways(InternetGatewayIds=[outputs['internet_gateway_id']])['InternetGateways'][0]
    routes = ec2.describe_route_tables(RouteTableIds=[outputs['route_table_id']])['RouteTables'][0]
    group = ec2.describe_security_groups(GroupIds=[outputs['security_group_id']])['SecurityGroups'][0]
    assert vpc['State'] == 'available' and vpc['CidrBlock'] == outputs['vpc_cidr']
    assert subnet['VpcId'] == vpc['VpcId'] and subnet['MapPublicIpOnLaunch']
    assert any(a['VpcId'] == vpc['VpcId'] for a in gateway['Attachments'])
    assert any(r.get('DestinationCidrBlock') == '0.0.0.0/0' and r.get('GatewayId') == outputs['internet_gateway_id'] and r['State'] == 'active' for r in routes['Routes'])
    assert any(a.get('SubnetId') == outputs['subnet_id'] for a in routes['Associations'])
    assert {p['FromPort'] for p in group['IpPermissions']} == {80, 443}
    assert all(r['CidrIp'] == os.environ['TF_VAR_operator_cidr'] for p in group['IpPermissions'] for r in p['IpRanges'])
    for resource in [vpc, subnet, gateway, routes, group]:
        tags = {t['Key']: t['Value'] for t in resource['Tags']}
        assert tags['Project'] == 'devops-assignment' and tags['Session'] == '19'
    verification = {'result': 'PASS', 'checked_at': datetime.now(timezone.utc).isoformat(), 'managed_resources': 6,
                    'outputs': outputs, 'checks': ['VPC available', 'public subnet in lab VPC', 'gateway attached',
                    'active default route', 'subnet route association', 'HTTP/HTTPS restricted to operator', 'assignment tags'],
                    'ec2_instances_created': 0, 's3_buckets_created': 0}
    (evidence / 'verification.json').write_text(json.dumps(verification, indent=2) + '\n')
    print(json.dumps(verification, indent=2), flush=True)
finally:
    if (project / '.terraform').exists():
        tf('05-destroy', 'plan', '-destroy', '-input=false', '-out=destroy.tfplan')
        tf('05-destroy', 'destroy', '-auto-approve', '-input=false')
        assert not run('06-cleanup', 'terraform', 'state', 'list').strip(), 'State is not empty'
        cleanup = {'terraform_state_empty': True, 'finished_at': datetime.now(timezone.utc).isoformat()}
        for output, method, parameter, absent_code in [
            ('vpc_id', 'describe_vpcs', 'VpcIds', 'InvalidVpcID.NotFound'),
            ('subnet_id', 'describe_subnets', 'SubnetIds', 'InvalidSubnetID.NotFound'),
            ('internet_gateway_id', 'describe_internet_gateways', 'InternetGatewayIds', 'InvalidInternetGatewayID.NotFound'),
            ('route_table_id', 'describe_route_tables', 'RouteTableIds', 'InvalidRouteTableID.NotFound'),
            ('security_group_id', 'describe_security_groups', 'GroupIds', 'InvalidGroup.NotFound')
        ]:
            if output not in outputs:
                continue
            try:
                getattr(ec2, method)(**{parameter: [outputs[output]]})
                raise AssertionError(f'{output} still exists')
            except ClientError as error:
                assert error.response['Error']['Code'] == absent_code, error
                cleanup[output.replace('_id', '_deleted')] = True
        assert not ec2.describe_vpcs(Filters=[{'Name': 'tag:Project', 'Values': ['devops-assignment']}, {'Name': 'tag:Session', 'Values': ['19']}])['Vpcs']
        cleanup['no_session19_vpcs'] = True
        cleanup['result'] = 'PASS'
        (evidence / 'cleanup.json').write_text(json.dumps(cleanup, indent=2) + '\n')
        with (evidence / '06-cleanup.txt').open('a') as stream:
            stream.write(json.dumps(cleanup, indent=2) + '\n')
        print(json.dumps(cleanup, indent=2), flush=True)
