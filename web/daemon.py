import sys, os, time, atexit
from signal import SIGTERM

class Daemon:

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):

        try:
            if os.fork():
                # exit first parent
                sys.exit(0)
        except OSError:
            sys.stderr.write("fork #1 failed")
            sys.exit(1)

        # decouple from parent environment
        os.setsid()

        # do second fork
        try:
            if os.fork():
                # exit from second parent
                sys.exit(0)
        except OSError:
            sys.stderr.write("fork #2 failed")
            sys.exit(1)

        # clear buffers
        sys.stdout.flush()
        sys.stderr.flush()
        # open new files for redirect standard file descriptors
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'a+')


        # register function after end script
        atexit.register(self.delpid)
        # write pidfile
        pid = str(os.getpid())
        open(self.pidfile, 'w+').write(pid + "\n")

        # redirect standard file descriptors
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            sys.stderr.write("pidfile " + self.pidfile + " already exist.\n")
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):

        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            sys.stderr.write("pidfile " + self.pidfile + " does not exist.\n")
            return

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError:
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)


    def restart(self):
        self.stop()
        self.start()


    def run(self):
       '''method for task daemon'''