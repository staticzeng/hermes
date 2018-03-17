#!/usr/bin/python

import unittest
from utils.post import post
from task.task import TaskStatus
from query_task import QueryTaskTest
from comm import HOST, PORT
from parser import parser

default = {
        #"source_path":"./test/source/CentOS-7.0-1406-x86_64-DVD.iso",
        "source_path":"/home/xjc/vtrans-master/test/source/VG_XenStorage--b0299f8f--52c8--fb59--64a4--f7e498a14f4c-VHD--65ffcf00--de86--439e--8b90--4edf4bc7d5b6",
        #"source_path":"./test/source",
        "save_dir":"/home/xjc/vtrans-master/test/torrent",
#        "tracker_url":"http://192.168.1.29:6969/announce",
        "type":"vhd"
        }

class MakeTorrent(object):
    def __init__(self, ip, data):
        self.ip = ip
        self.data = data

class MakeTorrentTest(unittest.TestCase):
    def __init__(self, testname, ip, data):
        super(MakeTorrentTest, self).__init__(testname)
        self.mt = MakeTorrent(ip, data)

    def setUp(self):
        pass

    def tearDown(self):
        pass
    def testMakeTorrent(self):
        ip = self.mt.ip
        #url = HOST + "/make_torrent"
        url = "http://%s:%s/make_torrent" % (ip, PORT)
        code, msg = post(url, self.mt.data)
        print code, msg
        self.assertEqual(code, 0)
        task_id = msg['task_id']
        status = QueryTaskTest(ip, task_id).waitForOver()
        #self.assertEqual(status["ret"], TaskStatus(task_id).SUCC["ret"])
        #self.assertIn(status["ret"], (TaskStatus(task_id).SUCC["ret"], -1))
        self.assertTrue(status["ret"] in (TaskStatus(task_id).SUCC["ret"], -1))

if __name__ == "__main__":
    options, args = parser.parse_args()

    ip = options.ip if options.ip else HOST
    data = dict(source_path=options.file if options.file else default["source_path"],
            save_dir=options.save if options.save else default["save_dir"],
            #tracker_url=options.tracker if options.tracker else default["tracker_url"],
            type=options.type if options.type else default["type"])

    print "ip:", ip
    print "data:", data

    suite = unittest.TestSuite()
    suite.addTest(MakeTorrentTest("testMakeTorrent", ip, data))

    unittest.TextTestRunner().run(suite)
    


    #unittest.main()
