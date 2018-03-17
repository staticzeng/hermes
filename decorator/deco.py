import json
import types
import threading
from utils.log import log
from utils.comm import *
from utils.error import *

def sync(lock):
    def sync_with_lock(fn):
        def new_fn(*args, **kargs):
            lock.acquire()
#            print fn.func_name, "get lock!"
            try:
                return fn(*args, **kargs)
            finally:
                lock.release()
#                print fn.func_name, "release lock!"
        new_fn.func_name = fn.func_name
        new_fn.__doc__ = fn.__doc__
        return new_fn
    return sync_with_lock

def singleton(cls):
    instances = dict()
    def _sigleton(*args, **kargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kargs)
        return instances[cls]
    return _sigleton

def status(run):
    def wrapper(self, *args, **kargs):
        from task.task import TaskStatus, TaskManager
        self.status = TaskStatus(self.task_id).RUNNING
        import time
        self.start_time = int(time.time())
        errcode, msg = run(self)
        self.end_time = int(time.time())

        if errcode == 0:
            self.status = TaskStatus(self.task_id, errcode, msg).SUCC
        else:
            self.status = TaskStatus(self.task_id, errcode, msg).FAIL
        log.debug("==============Task End==============")
        #TaskManager().del_task(self)
    return wrapper

def myexcept(etype):
    def _except(f):
        def wrapper(*args, **kargs):
            try:
                return f(*args, **kargs)
            except Exception, e:
                if isinstance(e, etype):
                    raise e
                else:
                    raise etype(e.message)
        return wrapper
    return _except

def taskstatus_return(sync_task):
    def wrapper(data):
        from task.task import TaskStatus
        try:
            err,msg = sync_task(data)
            return TaskStatus(task_id=0, errorcode=err, msg=msg).SUCC
        except VtransError, e:
            import traceback
            traceback.print_exc()
            return TaskStatus(task_id=0, errorcode=e.code(), msg=str(e)).FAIL
        except Exception, e:
            import traceback
            traceback.print_exc()
            return TaskStatus(task_id=0, errorcode=OtherError.code(), msg=str(e)).FAIL
    return wrapper

