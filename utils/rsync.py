import os, stat
import re

from execute import execute
from utils.log import log
from utils.error import *
from decorator.deco import myexcept
from utils.comm import *

class Rsync(object):
    rsync = RSYNC_CMD + " "
    def __init__(self, **kargs):
        self.kargs = kargs
        self._param_check()
        self.secret_file = "/tmp/%s.secret" % self.kargs["task_id"]
        self.progress_file = "/tmp/%s.progress" % self.kargs["task_id"]
        with open(self.secret_file, 'w') as f:
            f.write(self.kargs["password"])
        os.chmod(self.secret_file, stat.S_IRUSR|stat.S_IWUSR)
        self.pid = 0

    def _param_check(self):
        for param in ("task_id", "password", "source", "dest"):
            if param not in self.kargs:
                raise InvalidParamError("[%s] is a must param in rsync!" % param)

    @myexcept(RsyncError)
    def version(self):
        cmd = " ".join([self.rsync, "--version"])
        ret = execute(cmd)
        print ret
        return ret

    @myexcept(RsyncError)
    def do(self):
        cmd = self.rsync \
                + " -r " \
                + "--password-file=%s" % self.secret_file \
                + " %s" % self.kargs["source"] \
                + " %s" % self.kargs["dest"] \
                + " --log-file=%s" % RSYNC_LOG \
                + " --port %s" % RSYNC_PORT \
                + " --progress" \
                #+ " >%s" % self.progress_file
        print cmd
        with open(self.progress_file, 'w') as f:
            execute(cmd, progress_obj=self, _output=f)
    
    def get_progress(self):
        '''get progress from progress-file'''
        #e.g.   394002432   4%   28.97MB/s    0:04:27
        progress = "0"
        cmd = "tail -n 1 %s" % self.progress_file
        mass = execute(cmd)
        line = mass.split('\r  ')[-1]
        print "get progress line:", line
        if "%" not in line:
            return progress
        progress = re.split(r'\s+', line.strip())[1][:-1]
        return progress

