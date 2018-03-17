#!/usr/bin/python

from utils.post import post
from task.task import TaskStatus
from utils.comm import *
from comm import HOST, PORT
import time

class QueryTaskTest():
    def __init__(self, ip, task_id):
        self.ip = ip
        self.task_id = task_id
    def testQueryTask(self):
        #url = HOST + "/query_task" + "?task_id=%s" % self.task_id
        url = "http://%s:%s/query_task?task_id=%s" \
                % (self.ip, PORT, self.task_id)
        code, status = post(url)
        return status

    def waitForOver(self):
        i = 1
        while True:
            status = self.testQueryTask()
            print status
            if status["ret"] > JOB_STATUS_PENDING:
                break
            
            if status["ret"] < 0:
                break
            #i *= 2
            #if i > 16:
            #    i = 16
            time.sleep(i)
        return status
            



if __name__ == "__main__":
    import sys
    task_id = sys.argv[1]
    QueryTaskTest(task_id).testQueryTask()
