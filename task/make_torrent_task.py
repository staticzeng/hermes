from task import Task, TaskProgress, TaskManager
from utils.log import log
from decorator.deco import status
from utils.comm import *
from utils.error import *
from vtrans.torrent_maker import TorrentMaker

class MakeTorrentTask(Task):
    '''make a torrent file'''
    def __new__(cls, **kargs):
        task_id = TaskManager().find_task(cls.__name__, kargs)
        if task_id:
            log.warning("make-torrent task exists.task_id: %s" % task_id)
            return TaskManager().tasks[task_id]
        else:
            log.warning("create a new make-torrent task!")
            return super(MakeTorrentTask, cls).__new__(cls)
    
    def __init__(self, **kargs):
        if hasattr(self, "task_id"):
            return
        super(MakeTorrentTask, self).__init__()
        self.kargs = kargs
        self.source_path = kargs.get("source_path", None)
        self.save_dir = kargs.get("save_dir", None)
        self.tracker_url = kargs.get("tracker_url", None)
        self.type = kargs.get("type", "file")
 
    @status
    def run(self):
        '''make a torrent file by source file, save it to save_dir'''
        log.debug("make torrent task start... sourcefile: %s" % self.source_path)
        try:
            if not self.source_path:
                raise InvalidParamError("param source_path needed.")
            if not self.save_dir:
                raise InvalidParamError("param save_dir needed.")
            #if not self.tracker_url:
            #    raise InvalidParamError("param tracker_url needed.")
            #err, msg = Vtrans().make_torrent(self.source_path, self.save_dir, self.tracker_url, self.type)
            self.private_obj = TorrentMaker(self.source_path, self.save_dir, self.tracker_url, self.type)
            err, msg = self.private_obj.do()
            return err, msg
        except VtransError, e:
            errmsg = "make torrent task failed. detail: %s" % e
            log.error(errmsg)
            import traceback
            traceback.print_exc()
            return e.code(), errmsg
        except Exception, e:
            errmsg = "make torrent task failed. detail: %s" % e
            log.error(errmsg)
            import traceback
            traceback.print_exc()
            return OtherError.code(), errmsg
    def get_progress(self):
        if not self.private_obj:
            raise VtransError("cannot find vtrans-maker object in task")
        return self.private_obj.get_progress()
        
