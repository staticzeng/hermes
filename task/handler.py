import tornado.web
import json
import os, sys
import traceback

from utils.log import log
from utils.error import *
from utils.comm import *
from task import TaskManager
from async_test_task import AsyncTestTask
from make_torrent_task import MakeTorrentTask
from rsync_task import RsyncTask
from sync_task import sync_tasks
from vtrans.vtrans import Vtrans

class SyncTaskHandler(tornado.web.RequestHandler):
    def set_cross_domain(self):
        self.set_header('Access-Control-Allow-Origin', "*")
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    
    def get_param(self,request_data=None):
        raise NotImplementedError
    
    def do(self):
        return sync_tasks[self.__class__.__name__.split("Handler")[0]](self.data)

    def post(self):
        print "get a sync task request...."
        request_data = json.loads(self.request.body)
        self.data = request_data
        log.debug("============%s Task=============" % self.__class__.__name__.split("Handler")[0])
        log.debug("task param: %s" % request_data)
        ret = self.do()
        self.set_cross_domain()
        self.write(json.dumps(ret))
        log.debug("============Task ret: %s==========" % ret)

    def get(self):
        result = dict()
        try:
            self.get_param()
            result = self.do()
        except VtransError, e:
            msg = "Get a SyncTask Error. detail: %s" % e
            log.error(msg)
            result['ret'], result['msg'] = e.code(), str(e)
        except Exception, e:
            msg = "Get a SyncTask Error. detail: %s" % e
            import traceback
            traceback.print_exc() 
            log.error(msg)
            result['ret'], result['msg'] = OtherError.code(), str(e)
        finally:
            self.set_cross_domain()
            self.write(json.dumps(result))


class GetTaskStatusHandler(SyncTaskHandler):
    def get_param(self):
        self.data = dict()
        self.data["task_id"] = self.get_argument("task_id", "-1")
        if self.data["task_id"] == -1:
            raise InvalidParamError("must has a task_id param!")
    def do(self):
        task_id = self.data.get("task_id", "-1") 
        #log.debug("get a task status query request: %s" % task_id)
        ret = TaskManager().query_task(task_id)
        #log.debug("task status query end.")
        if ret["ret"] in (JOB_STATUS_SUCCESS, JOB_STATUS_FAILED):
            print "task_id:", task_id, type(task_id)
            TaskManager().del_task(task_id)
        return ret


class QueryTorrentHandler(SyncTaskHandler):
    def get_param(self):
        self.data = dict()
        self.data["torrent_id"] = self.get_argument("torrent_id", "-1")
        if self.data["torrent_id"] == "-1":
            raise InvalidParamError("must has a task_id param!")

    def do(self):
        result = dict()
        torrent_id = self.data.get("torrent_id", -1) 
        #log.debug("get a torrent status query request: %s" % torrent_id)
        result["ret"], result["msg"] = Vtrans().query_torrent(torrent_id)
        #log.debug("torrent status query end.")
        return result

class DownloadTorrentHandler(SyncTaskHandler):
    pass

class ListTorrentsHandler(SyncTaskHandler):
    def get_param(self):
        self.data = None

class RemoveTorrentHandler(SyncTaskHandler):
    pass

class PauseTorrentHandler(SyncTaskHandler):
    pass

class ResumeTorrentHandler(SyncTaskHandler):
    pass

class CancelTaskHandler(SyncTaskHandler):
    pass

class AsyncTaskHandler(tornado.web.RequestHandler):
    def set_cross_domain(self):
        self.set_header('Access-Control-Allow-Origin', "*")
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    
    @classmethod
    def do(cls, **data):
        result = dict()
        try:
            d = cls.task_cls(**data)
            ret = TaskManager().add_task(d)
            log.debug("==============Task %s start=============" % cls.__name__)
            log.debug("Task param: %s" % data)
            if ret[0] == 0:
                log.debug("task start...")
                d.start()
            result["ret"], result["msg"] = ret
            result["task_id"] = d.task_id
        except VtransError, e:
            msg = "%s request failed. detail: %s" % (cls.__name__, e)
            result['ret'], result['msg'] = e.code(), msg
            log.error(msg)
            traceback.print_exc()
        except Exception, e:
            msg = "%s request failed. detail: %s" % (cls.__name__, e)
            log.error(msg)
            result['ret'], result['msg'] = OtherError.code(), str(e)
        finally:
            log.debug("Task accepted? %s" % result)
            return result

    def post(self):
        log.debug("get %s request" % self.__class__.__name__)
        data = json.loads(self.request.body)
        ret = self.do(**data)
        log.debug("%s request end." % self.__class__.__name__)
        self.set_cross_domain()
        self.write(json.dumps(ret))

class AsyncTestHandler(AsyncTaskHandler):
    task_cls = AsyncTestTask

class MakeTorrentHandler(AsyncTaskHandler):
    task_cls = MakeTorrentTask

class RsyncHandler(AsyncTaskHandler):
    task_cls = RsyncTask


