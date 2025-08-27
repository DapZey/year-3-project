from network import recv
from TEST import predictclientimage
import signal

shouldRun = True

# Signal handler to stop server gracefully
def handle_exit(signum, frame):
    global shouldRun
    print("Server shutdown signal received. Stopping...")
    shouldRun = False

# Catch termination signals (Docker stop sends SIGTERM)
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)  # optional, for local Ctrl+C

# Main server loop
while shouldRun:
    recv()

print("Server has stopped.")
