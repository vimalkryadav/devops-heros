import argparse
import os
from lab import *

for category in ('CONFIG','CACHE','DATA'):
    os.environ['HELM_'+category+'_HOME']=str(ROOT/'.helm'/category.lower())

def helm(*args, **kwargs):
    return run('helm',*args,'--namespace',NS,**kwargs)

def verify(replicas,environment):
    k('rollout','status','deployment/notes-dev-deploy','--timeout=180s')
    deployment=data('deployment','notes-dev-deploy')
    assert deployment['spec']['replicas']==replicas
    assert deployment['status']['readyReplicas']==replicas
    k('get','pods','-o','wide')
    k('get','service','notes-dev-svc')
    k('get','configmap','notes-dev-config')
    name=next(p['metadata']['name'] for p in data('pods','-l','app.kubernetes.io/instance=notes-dev')['items']
              if ready(p) and not p['metadata'].get('deletionTimestamp'))
    assert k('exec',name,'--','printenv','ENVIRONMENT').stdout.strip()==environment
    page=k('exec',name,'--','wget','-q','-O','-','http://notes-dev-svc').stdout
    assert '<strong>'+environment+'</strong>' in page
    note(f'PASS: {replicas} ready replicas serve the {environment} page.')

def commands():
    with record('01-chart-commands'):
        run('helm','version')
        (ROOT/'.scratch').mkdir(exist_ok=True)
        run('helm','create','.scratch/generated-demo')
        note('Generated chart files:')
        for path in sorted((ROOT/'.scratch/generated-demo').rglob('*')):
            if path.is_file(): note(str(path.relative_to(ROOT)))
        run('helm','repo','add','examples','https://helm.github.io/examples')
        run('helm','repo','update')
        run('helm','repo','list')
        run('helm','search','repo','examples')
        run('helm','lint','notes-chart')
        run('helm','lint','notes-chart','-f','notes-chart/values-prod.yaml')
        run('helm','template','notes-dev','notes-chart','--namespace',NS)

def lifecycle():
    with record('02-install-upgrade'):
        k('create','namespace',NS)
        helm('install','notes-dev','notes-chart','--wait','--timeout','180s')
        verify(1,'development')
        helm('list')
        helm('status','notes-dev')
        helm('get','values','notes-dev','--all')
        helm('get','manifest','notes-dev')
        helm('upgrade','notes-dev','notes-chart','-f','notes-chart/values-prod.yaml','--wait','--timeout','180s')
        verify(3,'production')
        helm('history','notes-dev')

def recovery():
    with record('03-failed-upgrade-rollback'):
        failed=helm('upgrade','notes-dev','notes-chart','-f','notes-chart/values-prod.yaml',
            '--set','image.tag=assignment-tag-does-not-exist','--wait','--timeout','60s',expect=None)
        assert failed.returncode != 0
        status=json.loads(helm('status','notes-dev','-o','json').stdout)
        assert status['info']['status']=='failed'
        k('get','pods','-o','wide')
        broken=next(p for p in data('pods','-l','app.kubernetes.io/instance=notes-dev')['items']
            if p['spec']['containers'][0]['image'].endswith('assignment-tag-does-not-exist'))
        k('describe','pod',broken['metadata']['name'])
        k('events','--for','pod/'+broken['metadata']['name'])
        helm('history','notes-dev')
        helm('rollback','notes-dev','2','--wait','--timeout','180s')
        verify(3,'production')
        helm('history','notes-dev')
        helm('status','notes-dev')
        helm('get','values','notes-dev')
        note('PASS: failed revision 3 recovered to revision 2 configuration as new revision 4.')

def cleanup():
    with record('04-cleanup'):
        helm('uninstall','notes-dev','--wait','--timeout','120s')
        helm('list')
        k('get','deployments,pods,services,configmaps','-l','app.kubernetes.io/instance=notes-dev')
        poll('release Pods finish terminating',lambda: not data('pods','-l','app.kubernetes.io/instance=notes-dev')['items'],timeout=120)
        k('get','deployments,pods,services,configmaps','-l','app.kubernetes.io/instance=notes-dev')
        k('delete','namespace',NS,'--wait=true')
        run('helm','repo','remove','examples')
        note('PASS: release objects and the assignment namespace were removed.')

parser=argparse.ArgumentParser()
parser.add_argument('--stage',choices=['all','commands','lifecycle','recovery','cleanup'],default='all')
args=parser.parse_args()
for name, action in [('commands',commands),('lifecycle',lifecycle),('recovery',recovery)]:
    if args.stage in ('all',name): action()
if args.stage=='cleanup': cleanup()
