import argparse
import time
from lab import *

def storage():
    with record('01-storage'):
        run('kubectl','version')
        run('kubectl','config','current-context')
        k('apply','-f','mini-project/namespace.yaml')
        k('apply','-f','mini-project/')
        k('rollout','status','deployment/web-app','--timeout=180s')
        k('get','pvc')
        run('kubectl','get','storageclass','standard','-o','yaml')
        pv = data('pvc','web-data')['spec']['volumeName']
        run('kubectl','get','pv',pv)
        pods = data('pods','-l','app=web-app')['items']
        before = {p['metadata']['name'] for p in pods}
        old = pods[0]
        oldname = old['metadata']['name']
        note('Original Pod UID: ' + old['metadata']['uid'])
        k('exec',oldname,'--','sh','-c','printf "Vimal Kumar Yadav | 24BCS10273\n" > /data/student.txt')
        k('exec',oldname,'--','cat','/data/student.txt')
        k('delete','pod',oldname)
        def replacement():
            return next((p for p in data('pods','-l','app=web-app')['items']
                if p['metadata']['name'] not in before and ready(p)),None)
        new = poll('a new Pod becomes Ready',replacement)
        assert new['metadata']['uid'] != old['metadata']['uid']
        note('Replacement Pod UID: ' + new['metadata']['uid'])
        result = k('exec',new['metadata']['name'],'--','cat','/data/student.txt')
        assert 'Vimal Kumar Yadav | 24BCS10273' in result.stdout
        k('exec',new['metadata']['name'],'--','python','-c',
          'import urllib.request; print(urllib.request.urlopen("http://web-service/").read().decode())')
        k('apply','-f','01-kubernetes-volumes/emptydir.yaml','-f','01-kubernetes-volumes/hostpath.yaml')
        k('wait','--for=condition=Ready','pod/emptydir-demo','pod/hostpath-demo','--timeout=90s')
        k('logs','emptydir-demo','-c','reader')
        k('logs','hostpath-demo')
        note('PASS: dynamically provisioned PVC retained the record across Pod replacement.')

def probes():
    with record('02-probes'):
        name = data('pods','-l','app=web-app')['items'][0]['metadata']['name']
        pod = data('pod',name)
        restarts = pod['status']['containerStatuses'][0]['restartCount']
        k('get','pod',name,'-o','wide')
        k('exec',name,'--','touch','/tmp/unready')
        poll('readiness failure removes the selected Pod from ready traffic',lambda: not ready(data('pod',name)))
        k('get','pod',name)
        k('get','endpointslices','-l','kubernetes.io/service-name=web-service','-o','yaml')
        assert data('pod',name)['status']['containerStatuses'][0]['restartCount'] == restarts
        k('exec',name,'--','rm','/tmp/unready')
        k('wait','--for=condition=Ready','pod/'+name,'--timeout=60s')
        k('exec',name,'--','touch','/tmp/unhealthy')
        poll('liveness failure restarts the container',lambda: data('pod',name)['status']['containerStatuses'][0]['restartCount'] > restarts,timeout=120)
        k('wait','--for=condition=Ready','pod/'+name,'--timeout=90s')
        k('get','pod',name)
        k('describe','pod',name)
        k('logs',name)
        note('PASS: readiness changed traffic eligibility without a restart; liveness caused a restart and recovery.')

def autoscale():
    with record('03-hpa'):
        poll('CPU metrics are available',lambda: bool(data('hpa','web-app-hpa').get('status',{}).get('currentMetrics')),timeout=180)
        k('get','hpa')
        k('top','pods')
        k('apply','-f','load-generator.yaml')
        k('rollout','status','deployment/load-generator','--timeout=120s')
        def observe():
            k('get','hpa')
            k('top','pods','-l','app=web-app')
            return data('deployment','web-app').get('status',{}).get('readyReplicas',0) == 5
        poll('load scales the web Deployment from 2 to 5 ready replicas',observe,timeout=420,interval=15)
        k('get','pods','-o','wide')
        k('describe','hpa','web-app-hpa')
        k('delete','-f','load-generator.yaml')
        def down():
            k('get','hpa')
            dep = data('deployment','web-app')
            return dep['spec']['replicas']==2 and dep.get('status',{}).get('replicas')==2 and dep.get('status',{}).get('readyReplicas')==2
        poll('removing load scales the Deployment back to 2 replicas',down,timeout=420,interval=15)
        poll('surplus Pods finish terminating',lambda: len(data('pods','-l','app=web-app')['items'])==2,timeout=120)
        k('get','hpa')
        k('top','pods','-l','app=web-app')
        k('get','pods','-o','wide')
        note('PASS: observed 2 -> 5 -> 2 replicas; CPU target 50%, scale-down window 60 seconds for this lab.')

parser = argparse.ArgumentParser()
parser.add_argument('--stage',choices=['all','storage','probes','hpa'],default='all')
args = parser.parse_args()
for name, action in [('storage',storage),('probes',probes),('hpa',autoscale)]:
    if args.stage in ('all',name): action()
