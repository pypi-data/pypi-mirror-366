import os, sys, subprocess
def main():
    binary = os.path.join(os.path.dirname(__file__), '$BINARY')
    sys.exit(subprocess.run([binary] + sys.argv[1:]).returncode)
