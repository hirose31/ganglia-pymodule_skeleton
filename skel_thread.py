#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 複数の metric を扱いたいんだけど、データ源へのアクセスは 1 度で済む
# ようなときは、データ採取用の別スレッドを立てる。

import sys
import traceback
import os
import threading
import time

descriptors = list()
Desc_Skel   = {}
_Worker_Thread = None
_Lock = threading.Lock() # synchronization lock
Debug = False

def dprint(f, *v):
    if Debug:
        print >>sys.stderr, "DEBUG: "+f % v

class UpdateMetricThread(threading.Thread):

    def __init__(self, params):
        threading.Thread.__init__(self)
        self.running      = False
        self.shuttingdown = False
        self.refresh_rate = 10
        if "refresh_rate" in params:
            self.refresh_rate = int(params["refresh_rate"])
        self.metric       = {}

        self.device       = params["device"] # fixme
        self.host         = "" # fixme
        if "host" in params: # fixme
            self.host         = params["host"]

    def shutdown(self):
        self.shuttingdown = True
        if not self.running:
            return
        self.join()

    def run(self):
        self.running = True

        while not self.shuttingdown:
            _Lock.acquire()
            self.update_metric()
            _Lock.release()
            time.sleep(self.refresh_rate)

        self.running = False

    def update_metric(self):
        self.metric["foo"] = 8
        self.metric["bar"] = 9

    def metric_of(self, name):
        val = 0
        if name in self.metric:
            _Lock.acquire()
            val = self.metric[name]
            _Lock.release()
        return val

def metric_init(params):
    global descriptors, Desc_Skel, _Worker_Thread, Debug

    print '[skel_thread] fixme'
    print params

    # initialize skeleton of descriptors
    # uint は unsigned int にキャストされるので、4294967295(4G) が上限になる?
    # gmond/modules/python/mod_python.c
    Desc_Skel = {
        'name'        : 'fixme TBD',
        'call_back'   : metric_of,
        'time_max'    : 60,
        # value_typeとformatは型を合わせること
        'value_type'  : 'uint', # string | uint | float | double
        'format'      : '%d',   # %s     | %d   | %f    | %f
        'units'       : 'fixme',
        'slope'       : 'fixme zero|positive|negative|both',
        'description' : 'fixme TBD',
        'groups'      : 'fixme network',
        }

    if "refresh_rate" not in params:
        params["refresh_rate"] = 10
    if "debug" in params:
        Debug = params["debug"]
    dprint("%s", "Debug mode on")

    _Worker_Thread = UpdateMetricThread(params)
    _Worker_Thread.start()

    # IP:HOSTNAME
    if "spoof_host" in params:
        Desc_Skel["spoof_host"] = params["spoof_host"]

    descriptors.append(create_desc(Desc_Skel, {
                "name"       : "foo",
                "value_type" : "float",
                "format"     : "%.3f",
                "units"      : "req/sec",
                "description": "request per second",
                }))
    descriptors.append(create_desc(Desc_Skel, {
                "name"       : "bar",
                "value_type" : "uint",
                "format"     : "%d",
                "units"      : "bytes/sec",
                "description": "byte per sec",
                }))

    return descriptors

def create_desc(skel, prop):
    d = skel.copy()
    for k,v in prop.iteritems():
        d[k] = v
    return d

def metric_of(name):
    return _Worker_Thread.metric_of(name)

def metric_cleanup():
    _Worker_Thread.shutdown()

if __name__ == '__main__':
    try:
        params = {
            "device": "eth0",
            "host"  : "localhost",
            "debug" : True,
            }
        metric_init(params)

  #       for d in descriptors:
  #           print '''  metric {
  #   name  = "%s"
  #   title = "%s"
  #   value_threshold = 0
  # }''' % (d["name"], d["description"])

        while True:
            for d in descriptors:
                v = d['call_back'](d['name'])
                print ('value for %s is '+d['format']) % (d['name'],  v)
            time.sleep(5)
    except KeyboardInterrupt:
        time.sleep(0.2)
        os._exit(1)
    except StandardError:
        traceback.print_exc()
        os._exit(1)
