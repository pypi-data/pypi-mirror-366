import os, sys, subprocess
sys.exit(subprocess.call([
    os.path.join(os.path.dirname(__file__), "deterministic-zip"),
    *sys.argv[1:]
]))
