#!/bin/bash

# Script to create a tmux dashboard to monitor uwsgi processes on all pods in dso-api namespace
set -e

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "tmux is not installed. Please install it first."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is not installed. Please install it first."
    exit 1
fi

# Get all pod names in dso-api namespace
echo "Fetching pods in the dso-api namespace..."
PODS=$(kubectl get pods -n dso-api --field-selector=status.phase=Running -o jsonpath='{.items[*].metadata.name}')
POD_COUNT=$(echo "$PODS" | wc -w)

if [ -z "$PODS" ]; then
    echo "No running pods found in the dso-api namespace."
    exit 1
fi

echo "Found $POD_COUNT running pods in the dso-api namespace."

# Check if we already have a tmux session named uwsgi-monitor
if tmux has-session -t uwsgi-monitor 2>/dev/null; then
    echo "Session 'uwsgi-monitor' already exists. Killing it."
    tmux kill-session -t uwsgi-monitor
fi

# Create a new tmux session but don't attach to it yet
echo "Creating tmux session 'uwsgi-monitor'..."
tmux new-session -d -s uwsgi-monitor -n "uwsgi-monitor"

# Calculate optimal layout based on pod count
calculate_layout() {
    local count=$1
    
    # For small numbers, use simple layouts
    if [ "$count" -eq 1 ]; then
        echo "even-horizontal"
    elif [ "$count" -le 4 ]; then
        echo "tiled"
    elif [ "$count" -le 9 ]; then
        echo "tiled"
    else
        echo "tiled"
    fi
}

LAYOUT=$(calculate_layout "$POD_COUNT")

# First, split the window into the required number of panes
# We'll create POD_COUNT-1 splits since the first pane already exists
for ((i=1; i<POD_COUNT; i++)); do
    tmux split-window -t uwsgi-monitor
    tmux select-layout -t uwsgi-monitor "$LAYOUT"
done

# Now set up each pane with a continuous command that won't exit
PANE=0
for POD in $PODS; do
    # Create a wrapper script to keep the pane alive even if uwsgitop fails
    WRAPPER_SCRIPT="while true; do
        clear
        echo 'Pod: $POD'
        echo '-------------------'
        echo 'Connecting to uwsgi stats...'
        kubectl exec -n dso-api $POD -it -- uwsgitop /tmp/uwsgi-stats.sock || {
            echo 'Connection failed or uwsgitop exited.'
            echo 'Retrying in 5 seconds...'
            sleep 5
            continue
        }
        # If we get here, it means uwsgitop exited normally
        echo 'uwsgitop disconnected. Reconnecting in 5 seconds...'
        sleep 5
    done"
    
    # Send the wrapper script to the pane
    tmux send-keys -t uwsgi-monitor.$PANE "$WRAPPER_SCRIPT" C-m
    
    PANE=$((PANE+1))
done

# Add a status bar at the bottom with helpful information
tmux set -g status-left "DSO-API uWSGI Monitor | #[fg=green]Pods: $POD_COUNT #[fg=white]|"
tmux set -g status-right "#[fg=yellow]%H:%M:%S #[fg=white]| #[fg=cyan]%d-%b-%Y #[fg=white]|"
tmux set -g status-interval 1

# Set some nice tmux options
tmux set -g pane-border-status top
tmux set -g pane-border-format "#{pane_index}: #{pane_current_command}"
tmux set -g mouse on

# Attach to the session
echo "Starting uwsgi-monitor. Press Ctrl+B then D to detach without killing the session."
tmux attach-session -t uwsgi-monitor

# When the script exits, print a helpful message
echo "Session 'uwsgi-monitor' detached. You can reattach with 'tmux attach-session -t uwsgi-monitor'"