import time
import random
import uuid

def gen_task_id():
    '''gen a taskid, time+3random for eg: 201504071014150327'''
    id = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time())) + str(random.randint(100,999))
    return id

def gen_uuid():
    return str(uuid.uuid1())
