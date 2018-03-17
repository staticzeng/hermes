#!/usr/bin/python
import comm
import unittest
from utils.post import post
from task.task import TaskStatus
from comm import HOST, PORT
import json
from parser import parser

class ListTorrents(object):
    def __init__(self, ip, data):
        self.ip = ip
        self.data = data

class ListTorrentsTest(unittest.TestCase):
    def __init__(self, testname, ip, data):
        super(ListTorrentsTest, self).__init__(testname)
        self.lt = ListTorrents(ip, data)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testListTorrents(self):
        ip = self.lt.ip
        url = "http://%s:%s/list_torrents" % (ip, PORT)
        code, result = post(url, self.lt.data)
        #print code, result
        self.assertEqual(result['ret'], 4)
        print json.dumps(result['msg'], indent=4)
        #print json.loads(result['msg'], indents=4)

if __name__ == "__main__":
    options, args = parser.parse_args()
    ip = options.ip if options.ip else HOST
    data = None
    print "ip:", ip
    print "data:", data
    suite = unittest.TestSuite()
    suite.addTest(ListTorrentsTest("testListTorrents", ip, data))
    unittest.TextTestRunner().run(suite)

