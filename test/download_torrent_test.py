#!/usr/bin/python
import comm
import unittest
from utils.post import post
from task.task import TaskStatus
from comm import HOST, PORT
from query_torrent import QueryTorrentTest
import json
from parser import parser
default = {
        #"torrent_file": "/home/xjc/vtrans-master/test/torrent/CentOS-7.0-1406-x86_64-DVD.iso.torrent",
        "torrent_file":"/home/xjc/vtrans-master/test/torrent/VG_XenStorage--b0299f8f--52c8--fb59--64a4--f7e498a14f4c-VHD--65ffcf00--de86--439e--8b90--4edf4bc7d5b6.torrent",
        #"torrent_file":"/home/xjc/vtrans-master/test/torrent/modified.torrent",
        #"torrent_file":"/home/xjc/vtrans-master/test/torrent/VG_XenStorage--b0299f8f--52c8--fb59--64a4--f7e498a14f4c-VHD--feff0ca5--26ff--49f1--b3fa--6849e9f5b00a.torrent",
        #"torrent_file":"/home/xjc/vtrans-master/test/torrent/8c554aac-2485-11e5-942e-1e55c4a0d2f9.vhd.torrent",
        "save_dir": "/home/xjc/vtrans-master/test/source",
        #"torrent_file": "./test/torrent/FreeBSD-9.1-RELEASE-amd64-disc1.iso.torrent",
        #"save_dir": "./test/source",
        "seed_time": 0,
        "tracker_url":"http://192.168.1.40:6969/announce"
}


class DownloadTorrent(object):
    def __init__(self, ip, data):
        self.ip = ip
        self.data = data

class DownloadTorrentTest(unittest.TestCase):
    def __init__(self, testname, ip, data):
        super(DownloadTorrentTest, self).__init__(testname)
        self.dt = DownloadTorrent(ip, data)

    def setUp(self):
        pass

    def tearDown(self):
        pass
    def testDownloadTorrent(self):
        ip = self.dt.ip
        url = "http://%s:%s/download_torrent" % (ip, PORT)
        #url = MC + "/download_torrent"
        #code, result = post(url, data)
        code, result = post(url, self.dt.data)
        print code, result
        self.assertEqual(result['ret'], 4)
        torrent_id = result['msg']
        print "torrent id: ", torrent_id
        status = QueryTorrentTest(ip, torrent_id).waitForOver()
        #ret = status["complete_rate"] == '100.00' or status['state'] == 'checking fastresume'
        ret = status["is_finished"] == 1
        self.assertTrue(ret)

if __name__ == "__main__":
    options, args = parser.parse_args()

    ip = options.ip if options.ip else HOST
    data = dict(torrent_file=options.torrent if options.torrent else default["torrent_file"],
            save_dir=options.save if options.save else default["save_dir"],
            seed_time=options.time if options.time else default["seed_time"],
            tracker_url=options.tracker if options.tracker else default["tracker_url"])

    print "ip:", ip
    print "data:", data

    suite = unittest.TestSuite()
    suite.addTest(DownloadTorrentTest("testDownloadTorrent", ip, data))

    unittest.TextTestRunner().run(suite)
    #unittest.main()
