import threading
import libtorrent as lt
import time
import sys
import os
import os.path
import json

from decorator.deco import sync
from utils.gen import gen_task_id
from utils.log import log
from utils.comm import *

class Torrent(object):
    def __new__(cls, torrent_file, save_dir, seed_time=0):
        from vtrans import Vtrans
        cls.vtrans = Vtrans()
        torrent_id = cls.vtrans.find_torrent_by_file(torrent_file)
        if torrent_id:
            log.warning("torrent file exists. return torrent_id: %s, id: %s" % (torrent_id, id(cls.vtrans.torrent_dict[torrent_id])))
            return cls.vtrans.torrent_dict[torrent_id]
        else:
            log.warning("create a new torrent object!")
            return super(Torrent, cls).__new__(cls)

    def __init__(self, torrent_file, save_dir, seed_time=0):
        if hasattr(self, "torrent_id"):
            return
        self.torrent_id = gen_task_id()
        log.warning("Torrent Object init, torrent_id: %s, id: %s" % (self.torrent_id, id(self)))
        self.torrent_file = torrent_file
        self.save_dir = save_dir
        self.seed_time = seed_time
        self.lt_param = dict()
        self.lt_param['save_path'] = save_dir
        print "torrent_file:", torrent_file
        self.torrent_info = lt.torrent_info(torrent_file)
        self.lt_param['ti'] = self.torrent_info
        #if self.torrent_info.num_files() > 1:
        comment = self.torrent_info.comment()
        #if comment and json.loads(comment).get('type', 'file') == 'vhd':
        #    log.debug("this is a vhd torrent-file.")
        #    self.remap_files()
        self.remap_files()
        self.torrent_handler = None
        self.is_seed = False

    def add_tracker(self, tracker_url):
        self.torrent_info.add_tracker(str(tracker_url).strip(), 0)

    def remap_files(self):
        """change files to absolute path."""
        files = self.torrent_info.files()
        for i in range(self.torrent_info.num_files()):
            log.debug("rename %s to %s" % (files[i].path, os.path.basename(files[i].path)))
            self.torrent_info.rename_file(i, os.path.basename(files[i].path))

    def set_param(self, **args):
        optional = {'storage_mode': lt.storage_mode_t.storage_mode_sparse, 
                'paused': False,
                'auto_managed': True,
                }
        for key in optional:
            if key in args:
                self.lt_param[key] = args[key]
            else:
                self.lt_param[key] = optional[key]

    def set_torrent_handler(self, handler):
        """torrent handler setted when it added to session"""
        self.torrent_handler = handler

    def pause(self):
        """pause a torrent"""
        self.torrent_handler.auto_managed(False)
        self.torrent_handler.pause()
        self.vtrans.read_session_alerts()

    def resume(self):
        """resume a torrent"""
        self.torrent_handler.resume()
        self.torrent_handler.auto_managed(True)
        self.vtrans.read_session_alerts()

    def get_peer_info(self):
        for p in self.torrent_handler.get_peer_info():
            print 'peer ip:', p.ip, ' peer source:', p.source
        return [p.ip for p in self.torrent_handler.get_peer_info()]

    def query_status(self):
        s = self.torrent_handler.status()
        
        state_str = ('queued', 'checking', 'downloading metadata',\

                'downloading', 'finished', 'seeding', 'allocating',\
                        'checking fastresume')
        print '\ractive_time: %d, %.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d, seeds: %d) %s' % \
                (s.active_time, s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
                s.num_peers, s.num_seeds, state_str[s.state]),
        sys.stdout.flush()
        status = {
                "active_time": s.active_time,
                "complete_rate": "%.2f" % (s.progress * 100),
                "download_rate": "%.1f kB/s" % (s.download_rate / 1000),
                "upload_rate": "%.1f kB/s" % (s.upload_rate / 1000),
                "peers": "%s%s" % (s.num_peers, self.get_peer_info()),
                "seeds": s.num_seeds,
                "state": state_str[s.state],
                "is_finished": int(s.is_finished)
                }
        #log.debug("torrent status: %s" % status),
        return 0, status

