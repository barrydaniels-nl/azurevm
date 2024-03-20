#!/usr/bin/env python
# coding: utf-8
from os import system
import subprocess
import json 

PROJECT_PATH = '/Users/barrydaniels/code/gmadam/uwsgi-locust'
ACTIVATE_VENV = '. /Users/barrydaniels/code/gmadam/uwsgi-locust/venv/bin/activate'
ENVIRONMENT = 'o'

# Set Environment
if ENVIRONMENT == 'o':
    kubeenv = 'dev-bbn1-blue-aks'
elif ENVIRONMENT == 'p':
    kubeenv = 'prd-bbn1-blue-aks'
elif ENVIRONMENT == 't':
    kubeenv = 'test-bbn1-blue-aks'
else:
    raise ValueError('Environment must be one of o, p or q')

system(f'kubectl config use-context {kubeenv}')


def tmux(command):
    system('tmux %s' % command)


def get_pods() -> list[str]:
    result = subprocess.run(['/opt/homebrew/bin/kubectl', 'get', 'pods', '-n', 'dso-api', '-o', 'json'], stdout=subprocess.PIPE)
    pods_json = result.stdout.decode('utf-8')
    pods = [pod['metadata']['name'] for pod in json.loads(pods_json)['items']]
    return pods


def tmux_shell(command):
    tmux('send-keys "%s" "C-m"' % command)


pods = get_pods()
print(pods)

# example: one tab with vim, other tab with two consoles (vertical split)
# with virtualenvs on the project, and a third tab with the server running

# vim in project
# tmux('select-window -t 0')
# tmux_shell('cd %s' % PROJECT_PATH)
# tmux_shell('azvm %s' % ENVIRONMENT)
# tmux_shell('su - barry')
# tmux('rename-window "vim"')

# # console in project
# tmux('new-window')
# tmux('select-window -t 1')
# tmux_shell('cd %s' % PROJECT_PATH)
# tmux_shell(ACTIVATE_VENV)
# tmux('rename-window "consola"')
# # second console as split
# tmux('split-window -v')
# tmux('select-pane -t 1')
# tmux_shell('cd %s' % PROJECT_PATH)
# tmux_shell(ACTIVATE_VENV)
# tmux('rename-window "consola"')

# # local server
# tmux('new-window')
# tmux('select-window -t 2')
# tmux_shell('cd %s' % PROJECT_PATH)
# tmux_shell(ACTIVATE_VENV)
# tmux_shell('python manage.py runserver')
# tmux('rename-window "server"')

# # go back to the first window
# tmux('select-window -t 0')