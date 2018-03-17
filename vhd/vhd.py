#!/usr/bin/python

import os
import os.path

from vhd_util import VhdUtil

class RBTreeVHD(object):
    def __init__(self, path, virtual_size=None):
        self.parent = None
        self.virtual_size = virtual_size               #MB
        self.path =  path
        self.uuid = os.path.splitext(os.path.basename(path))[0]
        self._init_disk_info(path)
        self.flush_parent()

    def _init_disk_info(self, path):
        import os
        if os.path.exists(path):
            self.virtual_size = VhdUtil.query_size(path)
        else:
            VhdUtil.create(path, self.virtual_size)

    def _get_parent(self):
        """query the vhd's parent"""
        parent_path = VhdUtil.query_parent(self.path)
        if parent_path:
            return RBTreeVHD(parent_path, self.virtual_size)
        else:
            return None

    def flush_parent(self):
        self.parent = self._get_parent()

    def empty(self):
        return VhdUtil.empty(self.path)

    def get_chain(self):
        chain = list()
        chain.append(os.path.abspath(self.path))
        vhd = self
        while vhd.parent:
            chain.append(os.path.abspath(vhd.parent.path))
            vhd = vhd.parent
        return chain
        

if __name__ == "__main__":
    child = RBTreeVHD("../test/source/test.vhd")
    print child
    print child.parent
    print child.parent.parent
