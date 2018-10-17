import os, sys, daemon, tempfile
import RestHTTPRequestHandler as RH

# reload run method for daemon
class httpserverdemon(daemon.Daemon):
    def run(self):
        RH.runserver()



if __name__ == '__main__':
    pidFile = tempfile.gettempdir() + '/RestHTTPRequestHandler.pid'
    daemon = httpserverdemon(pidFile)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print("start daemon!")
            daemon.start()
        elif 'stop' == sys.argv[1]:
            print("stop daemon!")
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            print("restart daemon!")
            daemon.restart()
        else:
            sys.exit(2)
        sys.exit(0)
    else:
        print('usage: ' + sys.argv[0] + ' start|stop|restart')
        sys.exit(2)

