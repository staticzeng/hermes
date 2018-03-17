import os
import os.path
import libtorrent as lt
import json

from vhd.vhd import RBTreeVHD
from utils.comm import *
from utils.error import *
from utils.log import log

class TorrentMaker(object):
    def __init__(self, source_path, save_dir, tracker_url, type):
        self.progress = 0
        self.source_path = source_path
        self.save_dir = save_dir
        self.tracker_url = tracker_url
        self.type = type

    def do(self):
        """make a torrent file."""
        def file_filter(name):
            print "filter name:", name
            print "torrent type:", self.type
            if os.path.samefile(name ,os.path.dirname(self.source_path)):
                return True
            if self.type == 'vhd':
                chain = list()
                vhd = RBTreeVHD(self.source_path)
                chain = vhd.get_chain()
                log.debug("vhd-chain: %s" % chain)
                if name in chain:
                    return True
            else:
                if os.path.samefile(name, self.source_path):
                    return True

        if not os.path.exists(self.source_path):
            raise InvalidParamError("%s not exists." % self.source_path)
        source_path = os.path.abspath(self.source_path)
        torrent_file = "%s/%s.torrent" % (self.save_dir, os.path.basename(source_path))
        fs = lt.file_storage()
        lt.add_files(fs, os.path.dirname(source_path), file_filter)
        log.debug("add %s files to torrent." % fs.num_files())
        log.debug("total_size: %s" % fs.total_size())
        creator = lt.create_torrent(fs, 0, 4*1024*1024)
        #creator.add_tracker(str(self.tracker_url).strip())
        creator.set_creator("RBTree Vtrans %s" % VTRANS_VERSION)
        comment = dict()
        comment["type"] = self.type
        creator.set_comment(json.dumps(comment))
        #lt.set_piece_hashes(creator, os.path.split(source_path)[0], lambda x: sys.stderr.write('.'))
        #lt.set_piece_hashes(creator, "/home/xjc/vtrans-master/test", lambda x: sys.stderr.write('.'))
        #lt.set_piece_hashes(creator, os.path.dirname(os.path.dirname(source_path)), lambda x: sys.stderr.write('.'))
        num_pieces = creator.num_pieces()
        def piece_hash_process(x):
            self.progress = (x+1)*100/num_pieces
            print "\rall %s pieces, setting piece %s, porcess: %s%%" % (num_pieces, x+1, self.progress),
            sys.stdout.flush()
        #lt.set_piece_hashes(creator, os.path.dirname(os.path.dirname(source_path)), lambda x: sys.stderr.write("%s " % x/))
        lt.set_piece_hashes(creator, os.path.dirname(os.path.dirname(source_path)), piece_hash_process)
        sys.stderr.write('\n')
        with open(torrent_file, "wb") as f:
            f.write(lt.bencode(creator.generate()))
        return 0, "make torrent succesfully."

    def get_progress(self):
        return self.progress

