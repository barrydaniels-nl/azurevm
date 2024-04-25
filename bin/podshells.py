#!/usr/bin/env python3
# coding: utf-8

from os import system
import subprocess
import json 

def get_pods(namespace: str) -> list[str]:
    result = subprocess.run(['kubectl', 'get', 'pods', '-n', f'{namespace}', '-o', 'json'], stdout=subprocess.PIPE)
    pods_json = result.stdout.decode('utf-8')
    pods = [pod['metadata']['name'] for pod in json.loads(pods_json)['items']]
    return pods


pods = get_pods('dso-api')
for pod in pods:
    print(f"kubectl exec -it pod/{pod} -n dso-api -- uwsgitop /tmp/uwsgi-stats.sock")
