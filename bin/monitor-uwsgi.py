#!/usr/bin/env python3
# coding: utf-8
from os import system
import subprocess
import json 
import libtmux

ENVIRONMENT = 'test'

# Set Environment
if ENVIRONMENT == 'o':
    kubeenv = 'dev-bbn1-blue-aks'
elif ENVIRONMENT == 'p':
    kubeenv = 'prd-bbn1-blue-aks'
elif ENVIRONMENT == 't':
    kubeenv = 'test-bbn1-blue-aks'
elif ENVIRONMENT == 'test':
    kubeenv = 'docker-desktop'
else:
    raise ValueError('Environment must be one of o, p, q or test')


system(f'kubectl config use-context {kubeenv}')


import libtmux

# Connect to the tmux server
server = libtmux.Server()

# Create a new tmux session
if not server.has_session("MySession"):
    session = server.new_session(session_name="MySession")
else:
    session = server.find_where({"session_name": "MySession"})
# Create a new window within the session

window = session.new_window(window_name="MyWindow")

# Split the first pane horizontally to create two full-width panes at the top
top_pane = window.attached_pane
top_pane.split_window(vertical=False)

# Select the first pane to split it vertically for the bottom panes
window.select_pane('-t', '0')
bottom_pane = window.attached_pane
bottom_pane.split_window(vertical=True)

# We now have three panes. Resize the bottom pane to make room for two more vertical splits.
# Adjust the resize amount according to your preference or terminal size.
window.panes[2].cmd('resize-pane', '-y', '10')

# Split the bottom pane twice to create three vertically split panes at the bottom
bottom_pane.split_window(vertical=True)
window.panes[3].split_window(vertical=True)

# Optionally, you can resize the panes or perform other operations here

print("Session, window, and panes have been created successfully.")

quit()




def tmux(command):
    system('tmux %s' % command)


def get_pods(namespace: str) -> list[str]:
    result = subprocess.run(['/opt/homebrew/bin/kubectl', 'get', 'pods', '-n', f'{namespace}', '-o', 'json'], stdout=subprocess.PIPE)
    pods_json = result.stdout.decode('utf-8')
    pods = [pod['metadata']['name'] for pod in json.loads(pods_json)['items']]
    return pods


def tmux_shell(command):
    tmux('send-keys "%s" "C-m"' % command)


pods = get_pods('default')
x=0
for pod in pods:
    
    
    tmux('new-window -t %s' % pod)
    
    tmux('select-window -t %s' % pod)
    tmux_shell('azvm %s' % ENVIRONMENT)
    tmux_shell('su - barry')
    tmux_shell('uwsgitop /tmp/uwsgi-stats.sock')
    tmux('rename-window "shell"')
    
    x+=1 
    

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