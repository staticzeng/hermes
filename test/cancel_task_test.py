#!/usr/bin/python
import comm
import unittest
from utils.post import post
from task.task import TaskStatus
from comm import HOST, PORT
import json
from parser import parser
default = {
        "task_id":"",
        }

class CancelTask(object):
    def __init__(self, ip, data):
        self.ip = ip
        self.data = data

class CancelTaskTest(unittest.TestCase):
    def __init__(self, testname, ip, data):
        super(CancelTaskTest, self).__init__(testname)
        self.ct = CancelTask(ip, data)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testCancelTask(self):
        ip = self.ct.ip
        url = "http://%s:%s/cancel_task" % (ip, PORT)
        code, result = post(url, self.ct.data)
        print code, result
        self.assertEqual(result['ret'], 4)

if __name__ == "__main__":
    options, args = parser.parse_args()
    ip = options.ip if options.ip else HOST
    data = dict(task_id = options.taskid if options.taskid else default["task_id"])
    print "ip:", ip
    print "data:", data
    suite = unittest.TestSuite()
    suite.addTest(CancelTaskTest("testCancelTask", ip, data))
    unittest.TextTestRunner().run(suite)

