#!/usr/bin/env python

import tornado.httpserver
import tornado.ioloop
import os
import os.path

from vtrans.vtrans import Vtrans
from vtrans.torrent_service import TorrentService
from utils.daemon import Daemon
from utils.comm import *
from task.handler import AsyncTestHandler,\
        GetTaskStatusHandler,\
        MakeTorrentHandler,\
        DownloadTorrentHandler,\
        ListTorrentsHandler,\
        RemoveTorrentHandler,\
        PauseTorrentHandler,\
        ResumeTorrentHandler,\
        QueryTorrentHandler,\
        RsyncHandler,\
        CancelTaskHandler

def http_server_start():
    application = tornado.web.Application([
        (r"/async_test", AsyncTestHandler),
        (r"/query_task", GetTaskStatusHandler),
        (r"/make_torrent", MakeTorrentHandler),
        (r"/download_torrent", DownloadTorrentHandler),
        (r"/list_torrents", ListTorrentsHandler),
        (r"/remove_torrent", RemoveTorrentHandler),
        (r"/pause_torrent", PauseTorrentHandler),
        (r"/resume_torrent", ResumeTorrentHandler),
        (r"/query_torrent", QueryTorrentHandler),
        (r"/rsync", RsyncHandler),
        (r"/cancel_task", CancelTaskHandler),
        ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(HTTP_PORT, address="0.0.0.0")
    vtrans = Vtrans()
    torrent_service = TorrentService(vtrans.torrent_dict)
    #torrent_service._load_torrents()
    tornado.ioloop.PeriodicCallback(torrent_service._loop_torrent_dict, TORRENT_SERVICE_INTERVAL*1000).start()
    tornado.ioloop.IOLoop.instance().start()

class VtransServer(Daemon):
    def __init__(self, pidfile="/var/run/vtransd.pid"):
        super(VtransServer, self).__init__(pidfile)

    def run(self):
        vtrans = Vtrans()
        http_server_start()

def main():
    from optparse import OptionParser
    usage = '''usage: %prog [options]
        %prog --daemon
        %prog --debug
        '''
    parser = OptionParser(usage=usage)
    parser.add_option("-v", "--version", dest="version",
            help="show vtrans version", action="store_true",default=False)
    parser.add_option("", "--daemon", dest="daemon",
            help="start the vtrans server by daemon mode", action="store_true",default=False)
    parser.add_option("-d", "--debug", dest="debug",
            help="start the vtrans server by debug mode", action="store_true",default=False)
    parser.add_option("-s", "--stop", dest="stop",
            help="stop the vtrans server", action="store_true",default=False)
    options, args = parser.parse_args()
    if options.daemon:
        VtransServer().start()
    elif options.debug:
        vtrans = Vtrans()
        http_server_start()
    elif options.stop:
        VtransServer().stop()
    elif options.version:
        print VTRANS_VERSION
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
