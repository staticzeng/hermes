#!/usr/bin/env python

import libtorrent as lt
import sys
import os
import time
import json
from optparse import OptionParser
import socket
import struct
import fcntl
import shutil

from decorator.deco import singleton
from utils.comm import *
from utils.error import *
from utils.log import log
from vhd.vhd import RBTreeVHD

@singleton
class Vtrans(object):
    def __init__(self):
        print "vtrans init..."
        try:
            self.session = lt.session()
            self._init_session()
        except Exception, e:
            log.error("Get a Exception while init libtorrent session: %s" % e)
            self.read_session_alerts()
        self.torrent_dict = dict()

    def _init_session(self):
        sts = lt.session_settings()
        sts.ssl_listen = False
        sts.user_agent = "vtrans system"
        sts.tracker_completion_timeout = 5
        sts.tracker_receive_timeout = 5
        sts.stop_tracker_timeout = 5
        sts.active_downloads = -1
        sts.active_seeds = -1
        sts.active_limit = -1
        sts.auto_scrape_min_interval = 5
        sts.udp_tracker_token_expiry = 120
        sts.min_announce_interval = 1
        sts.inactivity_timeout = 60
        sts.connection_speed = 10
        sts.allow_multiple_connections_per_ip = True
        sts.max_out_request_queue = 128
        sts.request_queue_size = 3
        #sts.use_read_cache = False
        ##############test#####################
        sts.use_read_cache = True
        #sts.disable_hash_cache = True
        #sts.no_recheck_incomplete_resume = True             #broken-resume switch
        #######################################
        self.session.set_settings(sts)
        self.session.set_alert_mask(lt.alert.category_t.tracker_notification | lt.alert.category_t.status_notification)
        self.session.set_alert_mask(lt.alert.category_t.status_notification)
        print "libtorrent session listen on %s to %s" % (TORRENT_BEGIN_PORT, TORRENT_END_PORT)
        self.session.listen_on(TORRENT_BEGIN_PORT, TORRENT_END_PORT)
        upload_rate_limit = 0
        if int(upload_rate_limit) >= 100:
            self.session.set_upload_rate_limit(upload_rate_limit*1024)
            self.session.set_local_upload_rate_limit(upload_rate_limit*1024)

    def find_torrent_by_file(self, torrent_file):
        for torrent_id, torrent in self.torrent_dict.items():
            if torrent_file == torrent.torrent_file:
                return torrent_id
        else:
            return None

    def add_torrent(self, torrent):
        """torrent is a bt task handler, add it to torrent dict"""
        self.torrent_dict[torrent.torrent_id] = torrent
        torrent_handler = self.session.add_torrent(torrent.lt_param)
        torrent.set_torrent_handler(torrent_handler)
        log.info("***********add a new torrent task****************")
        log.debug("***********torrent hash: %s**********************" % torrent_handler.info_hash())
        print "after add, torrent_dict:", self.torrent_dict, id(self.torrent_dict)
        print "vtrans in add_torrent:", self
        self.read_session_alerts()
        return 0, "add torrent task to session succesfully."

    def remove_torrent(self, torrent):
        if torrent.torrent_handler:
            self.session.remove_torrent(torrent.torrent_handler)
            self.read_session_alerts()
            if torrent.torrent_id in self.torrent_dict:
                self.torrent_dict.pop(torrent.torrent_id)
                print "after remove, torrent_dict:", self.torrent_dict

    def query_torrent(self, torrent_id):
        """query a torrent task status"""
        if torrent_id not in self.torrent_dict:
            raise InvalidParamError("%s not in torrent tasks." % torrent_id)
        return self.torrent_dict[torrent_id].query_status()


    def read_session_alerts(self):
        alert = self.session.pop_alert()
        while alert:
            print "alert:", alert, alert.message()
            log.debug("libtorrent alert: %s" % alert.message())
            alert = self.session.pop_alert()

    @classmethod
    def make_torrent(cls, path, save_dir, tracker_url, _type='file'):
        """make a torrent file."""
        chain = list()
        if _type == 'vhd':
            vhd = RBTreeVHD(path)
            chain = vhd.get_chain()
            log.debug("vhd-chain: %s" % chain)

        def file_filter(name):
            print "filter name:", name
            print "torrent type:", _type
            if os.path.samefile(name ,os.path.dirname(path)):
                return True
            #if _type == 'vhd':
            #    vhd = RBTreeVHD(path)
            #    chain = vhd.get_chain()
            #    log.debug("vhd-chain: %s" % chain)
            if _type == 'vhd':
                if name in chain:
                    return True
            else:
                if os.path.samefile(name, path):
                    return True
            #return False

        if not os.path.exists(path):
            raise InvalidParamError("%s not exists." % path)
        source_path = os.path.abspath(path)
        torrent_file = "%s/%s.torrent" % (save_dir, os.path.basename(source_path))
        fs = lt.file_storage()
#        lt.add_files(fs, source_path)
#        add_files(fs, source_path, _type)
        lt.add_files(fs, os.path.dirname(source_path), file_filter)
        log.debug("add %s files to torrent." % fs.num_files())
        log.debug("total_size: %s" % fs.total_size())
        creator = lt.create_torrent(fs, 0, 4*1024*1024)
        print "tracker_url:", tracker_url, "type:", type(tracker_url), "len:", len(tracker_url)
        creator.add_tracker(str(tracker_url).strip())
        creator.set_creator("RBTree Vtrans %s" % VTRANS_VERSION)
        comment = dict()
        comment["type"] = _type
        creator.set_comment(json.dumps(comment))
        #lt.set_piece_hashes(creator, os.path.split(source_path)[0], lambda x: sys.stderr.write('.'))
        #lt.set_piece_hashes(creator, "/home/xjc/vtrans-master/test", lambda x: sys.stderr.write('.'))
        #lt.set_piece_hashes(creator, os.path.dirname(os.path.dirname(source_path)), lambda x: sys.stderr.write('.'))
        num_pieces = creator.num_pieces()
        def piece_hash_process(x):
            print "\rall %s pieces, setting piece %s, porcess: %s%%" % (num_pieces, x+1, (x+1)*100/num_pieces),
            sys.stdout.flush()
        #lt.set_piece_hashes(creator, os.path.dirname(os.path.dirname(source_path)), lambda x: sys.stderr.write("%s " % x/))
        lt.set_piece_hashes(creator, os.path.dirname(os.path.dirname(source_path)), piece_hash_process)
        sys.stderr.write('\n')
        with open(torrent_file, "wb") as f:
            f.write(lt.bencode(creator.generate()))
        return 0, "make torrent succesfully."

if __name__ == "__main__":
    vtrans = Vtrans()
    Vtrans.make_torrent()


