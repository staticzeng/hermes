import urllib2, urllib
import base64
import os
import json
from error import *

def post(url, data=None):
    #print "@@@@POST URL:" + str(url)
    if data:
        data = json.dumps(data)
        #data = urllib.urlencode(data)
    try:
        code = 0
        f = urllib2.urlopen(url=url, data=data)
        content = f.read()
        msg = json.loads(content)
        f.close()
    except Exception, e:
        code = 1
        msg = str(e)
        print "Error:%s" % str(e)
    return code, msg


def add_post_data_to_request(url, data):
    if data is not None:
        post_data_encoded = urllib.urlencode(data)
        request = urllib2.Request(url, post_data_encoded)
    else:
        request = urllib2.Request(url)
    return request

def add_auth_data_to_request(request, user, passwd):
    base64string = base64.encodestring('%s:%s' % (user, passwd)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    request.add_header("CLIENT-API-VERSION", "5.2.0")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    return request

def get_request(user, passwd, url, data):
    request = None
    print url
    request = add_post_data_to_request(url, data)
    request = add_auth_data_to_request(request, user, passwd);
    return request

def send_request(user, passwd, url, data=None):
    request = get_request(user, passwd, url, data)
    try:
        f = urllib2.urlopen(request,timeout=10)
        content = f.read()
        msg = json.loads(content)
        f.close()
        return msg
    except Exception, e:
        msg = str(e)
        print "Error:%s" % str(e)
        raise PostError(msg)
