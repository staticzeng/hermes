#!/usr/bin/python

import sys, os, time, atexit, fcntl, inspect
import os.path
from signal import SIGTERM 

def pid_running(pid):
    procfile = os.path.join("/proc", str(pid), "cmdline")
    try:
        with open(procfile, 'r') as f:
            name = f.read().strip()
        process = os.path.basename(inspect.getfile(sys.modules["__main__"]))
        #if name == process:
        if process in name or name in process:
            return True
    except Exception, e:
        return False

def ansi(color, msg):
    return "\x1b[%sm%s\x1b[m" % (color, msg)

def read_pid(pidfile):
    line = None
    with open(pidfile, 'r') as f:
        line = f.readline().strip()
    if line:
        return int(line)

class Daemon(object):
    """
    A generic daemon class. 
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError, e: 
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
    
        # decouple from parent environment
        os.chdir("/") 
        os.setsid() 
        os.umask(0) 
    
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit from second parent
                sys.exit(0) 
        except OSError, e: 
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1) 

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)
    
    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if pid and pid_running(pid):
            message = ansi(31, "%s pid[%s] already running?\n" % (self.__class__.__name__, pid))
            sys.stderr.write(message)
            sys.exit(1)
        
        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
    
        if not pid:
            message = ansi(31, "pidfile %s does not exist. Daemon not running?\n")
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart
        if not pid_running(pid):
            message = ansi(31, "pid[%s] is not running. Daemon not running?\n" % pid)
            sys.stderr.write(message)
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process    
        try:
            while 1:
                gpid = os.getpgid(pid)
                os.killpg(gpid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)
        finally:
            self.show()

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def show(self):
        """
        show the daemon status
        """
        color = 31
        name = self.__class__.__name__
        status = "[Not running]"
        if os.path.exists(self.pidfile):
            pid = read_pid(self.pidfile)
            if pid_running(pid):
                status = "[Running]"
                color = 32
            else:
                os.remove(self.pidfile)
        msg = ansi(color, "  %-16s   %s\n" % (name, status))
        sys.stdout.write(msg)
        

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """
        #raise NotImplementedError
        pass
