#!/usr/bin/python

from utils.execute import execute
from utils.log import log
from decorator.deco import myexcept
from utils.error import VhdutilError
from utils.comm import *

class VhdUtil(object):
    vhdutil = VHD_UTIL_CMD + " "
    @classmethod
    @myexcept(VhdutilError)
    def create(cls, name, size):
        '''create a vhd ,size MB'''
        args = [ 
            "create",
            "-n %s",
            "-s %s",
        ]   
        cmd = cls.vhdutil + " ".join(args) % (name, size)
        try:
            execute(cmd)
            msg = "vhd-util create a new vhd succesfully"
            log.info(msg)
        except Exception, e:
            msg = "vhd-util create a new vhd failed, detail: %s" % e 
            raise Exception(msg)    

    @classmethod
    @myexcept(VhdutilError)
    def snapshot(cls, name, parent):
        '''create a vhd snapshot for parent, which name is name'''
        args = [
            "snapshot",
            "-n %s",
            "-p %s",
        ]
        cmd = cls.vhdutil + " ".join(args) % (name, parent)
        try:
            execute(cmd)
            msg = "vhd-util snapshot succesfully"
            log.info(msg)
            return 0, msg
        except Exception, e:
            msg = "vhd-util snapshot failed, detail: %s" % e
            raise Exception(msg)

    @classmethod
    @myexcept(VhdutilError)
    def query_parent(cls, path):
        """query vhd's parent"""
        args = [
            "query",
            "-n %s",
            "-p"
        ]
        cmd = cls.vhdutil + " ".join(args) % path
        log.debug(cmd)
        try:
            ret = execute(cmd)
            if ret and "no parent" in ret:
                return None
            print "parent is", ret
            return ret
        except Exception, e:
            msg = "vhd-util query parent failed, detail: %s" % e
            import traceback
            traceback.print_exc() 
            raise Exception(msg)

    @classmethod
    @myexcept(VhdutilError)
    def query_size(cls, path):
        """query vhd's size"""
        args = [
            "query",
            "-n %s",
            "-v"
        ]
        cmd = cls.vhdutil + " ".join(args) % path
        log.debug(cmd)
        try:
            ret = execute(cmd)
            return ret
        except Exception, e:
            msg = "vhd-util query size failed, detail: %s" % e
            import traceback
            traceback.print_exc() 
            raise Exception(msg)

    @classmethod
    @myexcept(VhdutilError)
    def empty(cls, path):
        """judge if a vhd is empty"""
        args = [
                    "query",
                    "-n %s",
                    "-a"
                ]
        cmd = cls.vhdutil + " ".join(args) % path
        log.debug(cmd)
        try:
            ret = execute(cmd)
            if ret == "0":
                return True
            else:
                return False
        except Exception, e:
            msg = "vhd-util read vhd BAT failed, detail: %s" % e
            raise Exception(msg)


if __name__ == "__main__":
    #print VhdUtil().snapshot("./snapshot1.vhd", "./test1.vhd")
#    print VhdUtil().query_parent("/storage/xjc/vhd/child.vhd")
    print VhdUtil.empty("/storage/xjc/vhd/child.vhd")
