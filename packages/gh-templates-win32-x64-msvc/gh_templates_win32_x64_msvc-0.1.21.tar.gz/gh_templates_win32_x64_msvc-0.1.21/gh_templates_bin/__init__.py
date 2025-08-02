import os, sys, subprocess
def main():
    binary = os.path.join(os.path.dirname(__file__), 'gh-templates.exe')
    if not os.path.exists(binary):
        print(f"Error: Binary not found at {binary}")
        sys.exit(1)
    sys.exit(subprocess.run([binary] + sys.argv[1:]).returncode)
