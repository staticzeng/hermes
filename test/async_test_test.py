#!/usr/bin/python

import unittest
from utils.post import post
from task.task import TaskStatus
from query_task import QueryTaskTest
from comm import HOST

data = {
        "source_path":"/path/to/abc.vhd",
        }

class AsyncTestTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
    def testAsyncTest(self):
        url = HOST + "/async_test"
        code, msg = post(url, data)
        print code, msg
        self.assertEqual(code, 0)
        task_id = msg['task_id']
        status = QueryTaskTest(task_id).waitForOver()
        self.assertEqual(status["ret"], TaskStatus(task_id).SUCC["ret"])

if __name__ == "__main__":
    unittest.main()
