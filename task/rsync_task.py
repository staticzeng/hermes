from task import Task
from utils.log import log
from decorator.deco import status
from utils.comm import *
from utils.error import *
from utils.rsync import Rsync

class RsyncTask(Task):
    '''rysnc task ,e.g. downloading torrentfile and uploading vhd'''
    def __init__(self, **kargs):
        super(RsyncTask, self).__init__()
        self.source = kargs.get("source", None)
        self.dest = kargs.get("dest", None)
        self.password = kargs.get("password", None)
        self.private_obj = None
 
    @status
    def run(self):
        '''transport source to dest, by rsync train '''
        try:
            if not self.source:
                raise InvalidParamError("param source needed.")
            if not self.dest:
                raise InvalidParamError("param dest needed.")
            if not self.password:
                raise InvalidParamError("param password needed.")
            param_dict = dict(source=self.source, dest=self.dest, password=self.password, task_id=self.task_id)
            rsync = Rsync(**param_dict)
            self.private_obj = rsync
            rsync.do()
            print "rsync task done syccesfully..."
            return 0, "rsync task done succesuflly."
        except VtransError, e:
            errmsg = "rsync task failed. detail: %s" % e
            log.error(errmsg)
            import traceback
            traceback.print_exc()
            return e.code(), errmsg
        except Exception, e:
            errmsg = "rsync task failed. detail: %s" % e
            log.error(errmsg)
            import traceback
            traceback.print_exc()
            return OtherError.code(), errmsg

    def get_progress(self):
        if not self.private_obj:
            return 0
#            raise RsyncError("cannot find rsync object in task")
        return self.private_obj.get_progress()

