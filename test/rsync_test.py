#!/usr/bin/python

import unittest
from utils.post import post
from task.task import TaskStatus
from query_task import QueryTaskTest
from comm import HOST, PORT
from parser import parser

default = {
        #"source":"root@192.168.1.23::root/test/torrent/CentOS-7.0-1406-x86_64-DVD.iso.torrent",
        "source":"root@192.168.1.40::root/test/torrent/VG_XenStorage--b0299f8f--52c8--fb59--64a4--f7e498a14f4c-VHD--65ffcf00--de86--439e--8b90--4edf4bc7d5b6.torrent",
        #"source":"/home/xjc/vtrans-master/test/source/test.db",
        #"password":"qwer1234",
        #"dest":"root@192.168.1.40::root/test/torrent/",
        "dest":"/home/xjc/vtrans-master/test/torrent/",
        "password":"qwer1234",
        }

class Rsync(object):
    def __init__(self, ip, data):
        self.ip = ip
        self.data = data

class RsyncTest(unittest.TestCase):
    def __init__(self, testname, ip, data):
        super(RsyncTest, self).__init__(testname)
        self.rs = Rsync(ip, data)

    def setUp(self):
        pass

    def tearDown(self):
        pass
    def testRsync(self):
        ip = self.rs.ip
        #url = HOST + "/rsync"
        url = "http://%s:%s/rsync" % (ip, PORT)
        code, msg = post(url, self.rs.data)
        print code, msg
        self.assertEqual(code, 0)
        task_id = msg['task_id']
        status = QueryTaskTest(ip, task_id).waitForOver()
        self.assertEqual(status["ret"], TaskStatus(task_id).SUCC["ret"])

if __name__ == "__main__":
    options, args = parser.parse_args()

    ip = options.ip if options.ip else HOST
    data = dict(source=options.file if options.file else default["source"],
            dest=options.save if options.save else default["dest"],
            password=options.password if options.password else default["password"])

    print "data:", data

    suite = unittest.TestSuite()
    suite.addTest(RsyncTest("testRsync", ip, data))

    unittest.TextTestRunner().run(suite)
    
