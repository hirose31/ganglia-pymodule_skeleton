#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

descriptors = list()
Desc_Skel   = {}
Debug = False

def dprint(f, *v):
    if Debug:
        print >>sys.stderr, "DEBUG: "+f % v

# ここで値を作って返す
def metric_of(name):
    dprint("%s", name)
    if name == "foo":
        return 1
    elif name == "bar":
        return 2
    else:
        return 9

def metric_init(params):
    global descriptors, Desc_Skel, Debug

    print '[skel_simple] fixme'
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

def metric_cleanup():
    pass

if __name__ == '__main__':
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

    for d in descriptors:
        v = d['call_back'](d['name'])
        print ('value for %s is '+d['format']) % (d['name'],  v)

