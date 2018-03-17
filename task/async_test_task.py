from task import Task
from decorator.deco import status
from utils.log import log
from utils.comm import *
from utils.error import *

class AsyncTestTask(Task):
    '''test case'''
    def __init__(self, **kargs):
        super(AsyncTestTask, self).__init__()
        self.kargs = kargs

    @status
    def run(self):
        '''it is just a test case'''
        log.debug("test task start...")
        import time
        print "run befor try",time.time()
        try:
            import time
            time.sleep(5)
            print "run in run",time.time()
            return 0, "test success"
        except AgentError, e:
            msg = "test failed. detail: %s" % e
            log.error(msg)
            import traceback
            traceback.print_exc()
            return e.code(), msg
        except Exception, e:
            msg = "test failed. detail: %s" % e
            log.error(msg)
            import traceback
            traceback.print_exc()
            return OtherError.code(), msg

        
