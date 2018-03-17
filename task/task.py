import threading
import os
import os.path
import signal
from utils.gen import gen_task_id
from decorator.deco import singleton
from utils.comm import *
from utils.error import *
from utils.log import log
import time

class TaskStatus(object):
    def __init__(self, task_id, errorcode=0, msg=""):
        self.INIT = {"ret":JOB_STATUS_INACTIVE, "msg":"task[%s] initiating" % task_id}
        self.RUNNING = {"ret":JOB_STATUS_RUNNING, "msg":"task[%s] running" % task_id}
        self.SUCC = {"ret":JOB_STATUS_SUCCESS, "errorCode":"%d" %errorcode, "msg": msg}
        self.FAIL = {"ret":JOB_STATUS_FAILED, "errorCode":"%d" %errorcode, "msg": msg}

class TaskProgress(object):
    def __init__(self, task_id):
        self.task_id = task_id
        self.pid = -1

class Task(threading.Thread):
    def __init__(self, dbus=False):
        super(Task, self).__init__()
        self.task_id = gen_task_id()
        self.status = TaskStatus(self.task_id).INIT
        self.start_time = time.time()
      
    def run(self):
        '''run real task steps.'''
        raise NotImplementedError
    
@singleton
class TaskManager(object):
    def __init__(self):
        self.tasks = dict()

    def add_task(self, task):
        print "add task",task.task_id
        if task.task_id not in self.tasks:
            self.tasks[task.task_id] = task
            log.debug("task not found, accept a new task")
            return (0, "%s[%s] accepted" % (task.__doc__, task.task_id))
        else:
            log.debug("task existed!!!!!!!!!!!")
            return (1, "%s[%s] already existed" % (task.__doc__, task.task_id))

    def del_task(self, x):
        if type(x) in (str, unicode):
            task_id = x
        elif type(x) is Task:
            task_id = x.task_id
        else:
            raise InvalidParamError("x must be a task or task id string")
        log.debug("del task: %s" % task_id)
        if task_id in self.tasks:
            self.tasks.pop(task_id)

    def find_task(self, type, kargs):
        ''' find the same task in all tasks with same type'''
        print 'kargs:', kargs
        for task in self.tasks.values():
            if task.__class__.__name__ == type and getattr(task, 'kargs', None) == kargs:
                log.debug("find existing task: %s" % task.task_id)
                return task.task_id
        else:
            log.debug("task not found...")
            return None
                

    def query_task(self, task_id):
        ''' no exception '''
        task = self.tasks.get(task_id, None)
        if not task:
            raise TaskNotfoundError("task[%s] not found"%task_id)
        if hasattr(task, "get_progress"):
            try:
                task.status["progress"] = task.get_progress()
            except Exception, e:
                msg = "get progress failed.detail: %s" % e
                task.status["progress"] = msg
                import traceback
                traceback.print_exc() 
        return task.status

    def cancel_task(self, task_id):
        task = self.tasks.get(task_id, None)
        if not task:
            raise InvalidParamError("task[%s] not found" % task_id)
        if hasattr(task, "private_obj") and hasattr(task.private_obj, "pid") and task.private_obj.pid > 0:
            print "will cancel task. pid to kill: %s" % task.private_obj.pid
            os.kill(task.private_obj.pid, signal.SIGKILL)
        else:
            raise CancelTaskError("A %s task[%s] cannot be canceled now, plz wait..." % (task.__doc__, task_id))
        return 0, "task[%s] canceled successfully." % task_id

    

