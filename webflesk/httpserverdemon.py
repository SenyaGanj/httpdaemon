import os, sys, daemon, tempfile, webhttpserver

# reload run method for daemon
class httpserverdemon(daemon.Daemon):
    def run(self):
        webhttpserver.runhttpserver()


if __name__ == '__main__':
    pidFile = tempfile.gettempdir() + '/httpserverdemon.pid'
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

