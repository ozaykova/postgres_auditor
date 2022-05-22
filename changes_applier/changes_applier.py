import subprocess
import time
import sys
import os

class ChangesApplier:
    def __init__(self, sleep_hrs, path, conf_path):
        self.sleep_hrs = sleep_hrs
        self.path = path
        self.conf_path = conf_path

    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except Exception as e:
            sys.stderr.write("fork #1 failed: \n")
            sys.exit(1)

        os.chdir(".")
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
            print('Daemon started')
        except Exception as e:
            sys.stderr.write("fork #2 failed: \n")
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()

    def perform_apply(self):
        self.daemonize()
        time.sleep(self.sleep_hrs * 60 * 60)
        PIPE = subprocess.PIPE
        subprocess.Popen(f"mv {self.conf_path} {self.path}", shell=True, stdin=PIPE, stdout=PIPE,
                             stderr=subprocess.STDOUT, close_fds=True)
        subprocess.Popen(f"sudo service postgresql restart", shell=True, stdin=PIPE, stdout=PIPE,
                             stderr=subprocess.STDOUT, close_fds=True)