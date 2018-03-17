import libtorrent as lt
import time
import sys
import os
import os.path
import json

from decorator.deco import singleton
from utils.gen import gen_task_id
from utils.log import log
from utils.comm import *
from torrent import Torrent

class TorrentService(object):
    def __init__(self, torrent_dict):
        print "torrent service init..."
        super(TorrentService, self).__init__()
        self.torrent_dict = torrent_dict
   
    def _loop_torrent_dict(self):
        #print "torrent service thread running......"
        from vtrans import Vtrans
        vtrans = Vtrans()
        vtrans.read_session_alerts()
        torrent_dict = self.torrent_dict
        #print "torrent_dict: ", torrent_dict, id(torrent_dict)
        for torrent in torrent_dict.values():
            #print "serving torrent:", torrent.torrent_file
            if not torrent.torrent_handler:
                continue
            s = torrent.torrent_handler.status()
            state_str = ('queued', 'checking', 'downloading metadata',\

                'downloading', 'finished', 'seeding', 'allocating',\
                        'checking fastresume')
            print '\ractive_time: %d, %.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d, seeds: %d) %s' % \
                (s.active_time, s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
                s.num_peers, s.num_seeds, state_str[s.state]),
            sys.stdout.flush()
            #print "s.active_time:", s.active_time, type(s.active_time)
            #print "torrent.is_seed:", torrent.is_seed
            #print "handler.is_seed():", torrent.torrent_handler.is_seed()
            if not torrent.is_seed and torrent.torrent_handler.is_seed():
#                log.debug("%s will super seed!" % torrent.torrent_file)
                torrent.torrent_handler.super_seeding()
                torrent.is_seed = True

            if s.state == 3 and s.num_seeds == 0 and s.active_time > 0 and s.active_time % 10 == 0:
                #log.warning("\n %s find no seeds for 10s, let's re-announce!!!!!!" % torrent.torrent_file)
                #torrent.torrent_handler.force_reannounce()
                #torrent.torrent_handler.scrape_tracker()
                #torrent.torrent_handler.force_recheck()
                pass

            if torrent.seed_time == 0:
                #log.debug("%s seed for ever..." % torrent.torrent_file)
                continue
            #if torrent.torrent_handler.is_seed() and s.active_time >  torrent.seed_time:
            if torrent.torrent_handler.is_seed() and s.seeding_time >  torrent.seed_time:
                log.warning("%s seeding timeout! will remove it!!!" % torrent.torrent_file)
                Vtrans().remove_torrent(torrent)

    def _load_torrents(self):
        """load torrents in default dir, seeding in default period"""
        log.debug("load torrents from %s..." % TORRENT_DIR)
        from vtrans import Vtrans
        vtrans = Vtrans()
        for file in os.listdir(TORRENT_DIR):
            if file.endswith(".torrent"):
                log.debug("loading %s" % file)
                file_path = os.path.join(TORRENT_DIR, file)
                torrent = Torrent(file_path, SAVE_DIR, SEED_TIME)
                vtrans.add_torrent(torrent)
        log.debug("load torrents end.")

    def run(self):
        print "torrent service running..."
        try:
            #self._load_torrents()
            pass
        except Exception, e:
            log.error("load torrents error.detail: %s" % e)
        while True:
            try:
                self._loop_torrent_dict()
                time.sleep(1)
            except Exeption, e:
                log.error("loop torrents thread error. detail: %s" % e)


