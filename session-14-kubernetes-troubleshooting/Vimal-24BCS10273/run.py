import argparse
from lab import *

def waiting(name):
    statuses = data('pod',name).get('status',{}).get('containerStatuses',[])
    return statuses[0].get('state',{}).get('waiting',{}).get('reason') if statuses else None

def diagnose(name):
    k('get','pod',name,'-o','wide')
    k('describe','pod',name)
    k('events','--for','pod/'+name)

def replace(name, path):
    k('delete','pod',name,'--wait=true')
    k('apply','-f',path)
    k('wait','--for=condition=Ready','pod/'+name,'--timeout=120s')
    k('get','pod',name)

def setup():
    with record('00-commands'):
        run('kubectl','version')
        k('apply','-f','manifests/namespace.yaml')
        k('apply','-f','manifests/web.yaml')
        k('rollout','status','deployment/troubleshooting-app','--timeout=180s')
        k('wait','--for=condition=Ready','pod/client','--timeout=90s')
        k('get','pods','-o','wide')
        k('get','services')
        name = data('pods','-l','app=troubleshooting-app')['items'][0]['metadata']['name']
        k('describe','pod',name)
        k('exec',name,'--','wget','-q','-O','-','http://localhost')
        k('logs',name,'--tail=10')
        k('events')
        run('kubectl','explain','pod.spec.containers.resources')
        poll('metrics are available',lambda: k('top','pods',expect=None,quiet=True).returncode==0,timeout=180)
        k('top','pods')

def images():
    with record('01-image'):
        k('apply','-f','cases/image-broken.yaml')
        poll('ErrImagePull is observed',lambda: waiting('project-broken-pod')=='ErrImagePull',timeout=120,interval=1)
        k('get','pod','project-broken-pod')
        poll('image retries enter ImagePullBackOff',lambda: waiting('project-broken-pod')=='ImagePullBackOff',timeout=120,interval=1)
        diagnose('project-broken-pod')
        # Inspect the events before applying the repaired manifest.
        k('apply','-f','cases/image-fixed.yaml')
        k('wait','--for=condition=Ready','pod/project-broken-pod','--timeout=120s')
        k('get','pod','project-broken-pod')
        k('exec','project-broken-pod','--','wget','-q','-O','-','http://localhost')
        note('PASS: an unavailable image tag caused ErrImagePull and ImagePullBackOff; a valid tag recovered the Pod.')

def crash():
    with record('02-crash'):
        k('apply','-f','cases/crash-broken.yaml')
        poll('CrashLoopBackOff is observed',lambda: waiting('crash-demo')=='CrashLoopBackOff',timeout=180,interval=1)
        diagnose('crash-demo')
        k('logs','crash-demo','--previous')
        replace('crash-demo','cases/crash-fixed.yaml')
        k('logs','crash-demo')
        note('PASS: the process exited 7 due to an invalid start mode; the corrected mode keeps it running.')

def pending():
    with record('03-pending'):
        k('apply','-f','cases/pending-broken.yaml')
        poll('scheduler reports Unschedulable',lambda: any(c.get('reason')=='Unschedulable' for c in data('pod','pending-demo')['status'].get('conditions',[])))
        diagnose('pending-demo')
        run('kubectl','get','nodes','--show-labels')
        replace('pending-demo','cases/pending-fixed.yaml')
        note('PASS: no node matched the selector; removing the invalid constraint allowed scheduling.')

def mounting():
    with record('04-container-creating'):
        k('apply','-f','cases/mount-broken.yaml')
        poll('Pod waits in ContainerCreating',lambda: waiting('mount-demo')=='ContainerCreating')
        poll('FailedMount event identifies the missing ConfigMap',lambda: any(e.get('reason')=='FailedMount' for e in data('events','--field-selector','involvedObject.name=mount-demo')['items']))
        diagnose('mount-demo')
        k('apply','-f','cases/mount-fixed-config.yaml')
        k('wait','--for=condition=Ready','pod/mount-demo','--timeout=180s')
        k('get','pod','mount-demo')
        k('logs','mount-demo')
        assert 'Volume mounted successfully' in k('exec','mount-demo','--','cat','/config/message').stdout
        note('PASS: supplying the absent mounted ConfigMap allowed container creation.')

def config():
    with record('05-configuration'):
        k('apply','-f','cases/config-broken.yaml')
        poll('CreateContainerConfigError is observed',lambda: waiting('config-demo')=='CreateContainerConfigError')
        diagnose('config-demo')
        k('get','configmap','app-settings','-o','yaml')
        k('apply','-f','cases/config-fixed.yaml')
        k('wait','--for=condition=Ready','pod/config-demo','--timeout=120s')
        k('get','pod','config-demo')
        k('logs','config-demo')
        assert k('exec','config-demo','--','printenv','APP_MODE').stdout.strip() == 'development'
        note('PASS: adding the missing APP_MODE key fixed environment configuration.')

def service():
    with record('06-service'):
        poll('baseline Service is reachable',lambda: k('exec','client','--','wget','-q','-O','-','-T','3','http://troubleshooting-service',expect=None,quiet=True).returncode==0)
        k('exec','client','--','wget','-q','-O','-','-T','3','http://troubleshooting-service')
        k('apply','-f','cases/service-broken.yaml')
        poll('no ready endpoints match the wrong selector',lambda: not any(ep.get('conditions',{}).get('ready') for sl in data('endpointslices','-l','kubernetes.io/service-name=troubleshooting-service')['items'] for ep in (sl.get('endpoints') or [])))
        k('get','endpointslices','-l','kubernetes.io/service-name=troubleshooting-service','-o','yaml')
        poll('Service traffic fails after routing updates propagate',lambda: k('exec','client','--','wget','-q','-O','-','-T','3','http://troubleshooting-service',expect=None).returncode!=0,timeout=60,interval=2)
        k('get','pods','--show-labels')
        k('describe','service','troubleshooting-service')
        k('apply','-f','cases/service-fixed.yaml')
        poll('two ready backend endpoints return',lambda: sum(ep.get('conditions',{}).get('ready',False) for sl in data('endpointslices','-l','kubernetes.io/service-name=troubleshooting-service')['items'] for ep in (sl.get('endpoints') or []))==2)
        poll('Service HTTP recovers',lambda: k('exec','client','--','wget','-q','-O','-','-T','3','http://troubleshooting-service',expect=None,quiet=True).returncode==0)
        k('exec','client','--','wget','-q','-O','-','-T','3','http://troubleshooting-service')
        note('PASS: matching Service selectors and Pod labels restored traffic to two backends.')

def dns():
    with record('07-dns'):
        k('apply','-f','cases/dns-broken.yaml')
        k('wait','--for=condition=Ready','pod/dns-demo','--timeout=90s')
        k('exec','dns-demo','--','cat','/etc/resolv.conf')
        failed=k('exec','dns-demo','--','nslookup','troubleshooting-service.assignment-s14.svc.cluster.local.',expect=None)
        assert failed.returncode != 0
        k('get','pod','dns-demo','-o','yaml')
        # An unrelated client can resolve: the fault is confined to this Pod.
        k('exec','client','--','nslookup','troubleshooting-service.assignment-s14.svc.cluster.local.')
        replace('dns-demo','cases/dns-fixed.yaml')
        k('exec','dns-demo','--','cat','/etc/resolv.conf')
        k('exec','dns-demo','--','nslookup','troubleshooting-service.assignment-s14.svc.cluster.local.')
        k('exec','dns-demo','--','wget','-q','-O','-','http://troubleshooting-service')
        note('PASS: ClusterFirst replaced the invalid localhost DNS server with cluster DNS.')

def networking():
    with record('08-pod-networking'):
        k('apply','-f','cases/network-broken.yaml')
        k('wait','--for=condition=Ready','pod/network-demo','--timeout=90s')
        ip=data('pod','network-demo')['status']['podIP']
        k('get','pod','network-demo','-o','wide')
        k('exec','network-demo','--','wget','-q','-O','-','http://127.0.0.1:8080')
        failed=k('exec','client','--','wget','-q','-O','-','-T','3',f'http://{ip}:8080',expect=None)
        assert failed.returncode != 0
        k('exec','network-demo','--','netstat','-lnt')
        replace('network-demo','cases/network-fixed.yaml')
        ip=data('pod','network-demo')['status']['podIP']
        k('exec','network-demo','--','netstat','-lnt')
        k('exec','client','--','wget','-q','-O','-','-T','3',f'http://{ip}:8080')
        note('PASS: binding to all interfaces made the application reachable at the Pod IP.')

actions=[('setup',setup),('images',images),('crash',crash),('pending',pending),('mount',mounting),('config',config),('service',service),('dns',dns),('network',networking)]
parser=argparse.ArgumentParser()
parser.add_argument('--stage',choices=['all']+[name for name,_ in actions],default='all')
parser.add_argument('--start-at',choices=[name for name,_ in actions])
args=parser.parse_args()
started = args.start_at is None
for name, action in actions:
    started = started or name == args.start_at
    if started and args.stage in ('all',name): action()
