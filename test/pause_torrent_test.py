#!/usr/bin/python
import comm
import unittest
from utils.post import post
from task.task import TaskStatus
from comm import HOST, PORT
import json
from parser import parser
default = {
        "torrent_file":"/home/xjc/vtrans-master/test/torrent/VG_XenStorage--b0299f8f--52c8--fb59--64a4--f7e498a14f4c-VHD--65ffcf00--de86--439e--8b90--4edf4bc7d5b6.torrent",
        }

class PauseTorrent(object):
    def __init__(self, ip, data):
        self.ip = ip
        self.data = data

class PauseTorrentTest(unittest.TestCase):
    def __init__(self, testname, ip, data):
        super(PauseTorrentTest, self).__init__(testname)
        self.pt = PauseTorrent(ip, data)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testPauseTorrent(self):
        ip = self.pt.ip
        url = "http://%s:%s/pause_torrent" % (ip, PORT)
        code, result = post(url, self.pt.data)
        print code, result
        self.assertEqual(result['ret'], 4)

if __name__ == "__main__":
    options, args = parser.parse_args()
    ip = options.ip if options.ip else HOST
    data = dict(torrent_file = options.torrent if options.torrent else default["torrent_file"])
    print "ip:", ip
    print "data:", data
    suite = unittest.TestSuite()
    suite.addTest(PauseTorrentTest("testPauseTorrent", ip, data))
    unittest.TextTestRunner().run(suite)

