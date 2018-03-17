#!/usr/bin/python
from utils.log import log
from utils.comm import *
from utils.error import *
from task import TaskStatus, TaskManager
from decorator.deco import taskstatus_return
from vtrans.vtrans import Vtrans
from vtrans.torrent import Torrent

#note: sync task function name must be according to the handler.py and task_dbus.py

"""
Note:
every function in this py is a sync task, which can be called by http API.
sync task function should follow the under rules.
1. param: recieve a dict param, named data, and should check it here.
2. return: return a tuple, for example. (err, msg) the msg can be a task result explain, or somthing UI want to get, like vm_path
3. exception: any exception can be raised here, but don't catch here, exceptions will be catched in the deco taskstatus_return
4. flow: the sync task function will be called in dbus or http frame, and some inner fuction in some objects.
"""

@taskstatus_return
def DownloadTorrent(data):
    torrent_file = data.get("torrent_file", None)
    if not torrent_file:
        raise InvalidParamError("torrent_file param is needed.")
    tracker_url = data.get("tracker_url", None)
    if not tracker_url:
        raise InvalidParamError("tracker_url param is needed.")
    vtrans = Vtrans()
    save_dir = data.get("save_dir", None)
    seed_time = data.get("seed_time", None)
    t = Torrent(torrent_file, save_dir, seed_time)
    t.add_tracker(tracker_url)
    vtrans.add_torrent(t)
    return 0, t.torrent_id

@taskstatus_return
def ListTorrents(data):
    vtrans = Vtrans()
    torrents_msg = dict()
    for t in vtrans.torrent_dict.values():
        tmsg = dict()
        ret, status = t.query_status()
        tmsg['torrent_file'] = t.torrent_file
        tmsg['files'] = [f.path for f in t.torrent_info.files()]
        tmsg['save_dir'] = t.save_dir
        tmsg['seed_time'] = t.seed_time
        tmsg['status'] = status
        torrents_msg[t.torrent_id] = tmsg
    return 0, torrents_msg

@taskstatus_return
def RemoveTorrent(data):
    torrent_file = data.get("torrent_file", None)
    if not torrent_file:
        raise InvalidParamError("torrent_file param is needed.")
    vtrans = Vtrans()
    torrent_id = vtrans.find_torrent_by_file(torrent_file)
    if not torrent_id:
        raise InvalidParamError("torrent %s not found" % torrent_file)
    t = vtrans.torrent_dict.get(torrent_id, None)
    vtrans.remove_torrent(t)
    return 0, "remove torrent successfully."

@taskstatus_return
def PauseTorrent(data):
    torrent_file = data.get("torrent_file", None)
    if not torrent_file:
        raise InvalidParamError("torrent_file param is needed.")
    vtrans = Vtrans()
    torrent_id = vtrans.find_torrent_by_file(torrent_file)
    if not torrent_id:
        raise InvalidParamError("torrent %s not found" % torrent_file)
    t = vtrans.torrent_dict.get(torrent_id, None)
    t.pause()
    return 0, "pause torrent successfully."

@taskstatus_return
def ResumeTorrent(data):
    torrent_file = data.get("torrent_file", None)
    if not torrent_file:
        raise InvalidParamError("torrent_file param is needed.")
    vtrans = Vtrans()
    torrent_id = vtrans.find_torrent_by_file(torrent_file)
    if not torrent_id:
        raise InvalidParamError("torrent %s not found" % torrent_file)
    t = vtrans.torrent_dict.get(torrent_id, None)
    t.resume()
    return 0, "resume torrent successfully."

@taskstatus_return
def CancelTask(data):
    task_id = data.get("task_id", None)
    if not task_id:
        raise InvalidParamError("task_id param is needed.")
    tmgr = TaskManager()
    return tmgr.cancel_task(task_id) 

sync_tasks = {
        }

for name,func in locals().items():
    if callable(func):
        sync_tasks[name] = func

