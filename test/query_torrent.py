#!/usr/bin/python

from utils.post import post
from task.task import TaskStatus
from utils.comm import *
from comm import HOST, PORT
import time, sys

class QueryTorrentTest():
    def __init__(self, ip, torrent_id):
        self.ip = ip
        self.torrent_id = torrent_id
    def testQueryTorrent(self):
        url = "http://%s:%s/query_torrent?torrent_id=%s" \
                % (self.ip, PORT, self.torrent_id)
        #url = MC + "/query_torrent" + "?torrent_id=%s" % self.torrent_id
        code, status = post(url)
        return status

    def waitForOver(self):
        i = 1
        while True:
            status = self.testQueryTorrent()
            status = status["msg"]
            print '\ractive_time: %(active_time)s, %(complete_rate)s%% complete (down: %(download_rate)s kB/s up: %(upload_rate)s kB/s peers: %(peers)s, seeds: %(seeds)s) %(state)s' % status,
            sys.stdout.flush()
            if status['is_finished']:
                break
            time.sleep(i)
        return status
            



if __name__ == "__main__":
    import sys
    task_id = sys.argv[1]
    QueryTaskTest(task_id).testQueryTask()
