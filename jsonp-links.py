# -*- coding: utf-8 -*-
## process 
## http://dsg.ac.upc.edu/qmpsu/index.php
## jsonp-links.py
## (c) Llorenç Cerdà-Alabern, May 2020.
## debug: import pdb; pdb.set_trace()

import csv # https://docs.python.org/3/library/csv.html
import json
import importlib
import os
import sys
import re, gzip

cmn = importlib.import_module("jsonp-common")

def dic_has_key(dic, ks):
    for k in ks:
        if k not in dic:
            return False
    return True

##
## link data
##
def get_wifi_links(d):
    wifi = []
    ifces = d['interfaces']
    for l in d['links']:
        if 'viaDev' in l:
            via = l['viaDev']
            if via in ifces:
                if ifces[via] == 'wireless' and 'id' in l and 'iwdump' in l:
                    wifi.append({'dst.id': l['id'], 'dst.name': l['name'], 
                                 'ltxb': l['iwdump']['tx bytes'],
                                 'lrxb': l['iwdump']['rx bytes'],
                                 'ltxp': l['iwdump']['tx packets'],
                                 'lrxp': l['iwdump']['rx packets'],
                                 'rtx': l['iwdump']['tx retries'],
                                 'ftx': l['iwdump']['tx failed'],
                                 'Mbps': l['iwdump']['tx bitrate'],
                                 'dBm': l['iwdump']['signal'],
                                 'txRate': l['txRate'],
                                 'rxRate': l['rxRate'],
                                 'routes': l['routes'],
                                 'iface': via})
                    # wifi[-1].update(d['net_dev'][via])
    return wifi

def get_eth_links(d):
    eth = []
    ifces = d['interfaces']
    for l in d['links']:
        if 'viaDev' in l:
            via = l['viaDev']
            if via in ifces:
                if ifces[via] == 'ethernet' and 'id' in l:
                    eth.append({'dst.id': l['id'], 'dst.name': l['name'], 
                                 'txRate': l['txRate'],
                                 'rxRate': l['rxRate'],
                                 'routes': l['routes'],
                                 'iface': via})
                    # eth[-1].update(d['net_dev'][via])
    return eth

def build_link_data(f, js, get_links, fw):
    wtimes = True
    date = cmn.get_date(f)
    uid = get_uid(js)
    if uid == None: return
    for d in js:
        if 'interfaces' in d and 'links' in d:
            src = uid[d['id']]
            for wl in get_links(d):
                try:
                    if wl['dst.id'] < len(uid):
                        if wtimes:
                            wl.update({'date': date, 'src.uid': src, 'dst.uid': uid[wl['dst.id']], 
                                       'src.name': d['hostname'], 'src.id': d['id']})
                            wtimes = False
                        else:
                            wl.update({'date': '', 'src.uid': src, 'dst.uid': uid[wl['dst.id']], 
                                       'src.name': d['hostname'], 'src.id': d['id']})
                        fw.writerow(wl)
                except:
                    cmn.error("build_link_data?")

def build_csv_links(file_list, dir, type, fn=None):
    fieldnames = {
        "wifi": ["date", "src.uid", "dst.uid", "src.name", "src.id", "dst.id", "dst.name", 
                 "ltxb", "lrxb", "ltxp", "lrxp", "rtx", "ftx", "Mbps", "dBm", 
                 "txRate", "rxRate", "routes", "iface", 
                 # "txe", "rxb", "rxe", "txb", "rxp", "txp"
        ],
        "eth": ["date", "src.uid", "dst.uid", "src.name", "src.id", "dst.id", "dst.name", 
                "txRate", "rxRate", "routes", "iface"
        ]
    }[type]
    get_links = {
        "wifi": get_wifi_links,
        "eth":  get_eth_links
    }[type]
    build_csv(file_list, dir, fieldnames, build_link_data, get_links, fn)

##
## ifaces data
##
def build_ifaces_data(f, js, get_ifaces, fw):
    wtimes = True
    date = cmn.get_date(f)
    uid = get_uid(js)
    if uid == None: return
    for d in js:
        if 'interfaces' in d and 'net_dev' in d:
            src = uid[d['id']]
            for ifce,itype in d['interfaces'].items():
                if ifce in d['net_dev']:
                    data = d['net_dev'][ifce]
                    try:
                        if wtimes:
                            data.update({'date': date, 'uid': src, 'name': d['hostname'], 'id': d['id'],
                                         'if.type': itype, 'if.name': ifce})
                            wtimes = False
                        else:
                            data.update({'date': '', 'uid': src, 'name': d['hostname'], 'id': d['id'],
                                         'if.type': itype, 'if.name': ifce})
                        fw.writerow(data)
                    except:
                        cmn.error("build_ifaces_data?")

def build_csv_ifaces(file_list, dir, fn=None):
    fieldnames = ["date", "uid", "name", "id", "if.type", "if.name",
                  "txe", "rxe", "txb", "rxb", "txp", "rxp"]
    build_csv(file_list, dir, fieldnames, build_ifaces_data, None, fn)

##
## state data
##
def build_state_data(f, js, get_state, fw):
    wtimes = True
    date = cmn.get_date(f)
    uid = get_uid(js)
    if uid == None: return
    for d in js:
        if dic_has_key(d, ['cpu_stat', 'cpu_meminfo', 'vmstat', 'processes', 'loadavg']):
            src = uid[d['id']]
            data = {}
            if wtimes:
                data.update({'date': date})
                wtimes = False
            else:
                data.update({'date': ''})
            data.update({'uid': src, 'name': d['hostname'], 'id': d['id'],
                        "processes": d["processes"], "loadavg-m1": d['loadavg']["m1"],
                         "nr_slab_unreclaimable": d['vmstat']["nr_slab_unreclaimable"],
                         "workingset_refault": d['vmstat']["workingset_refault"],
                         "nr_anon_pages": d['vmstat']["nr_anon_pages"]})
            data.update(d["cpu_stat"])
            data.update(d['cpu_meminfo'])
            try:
                fw.writerow(data)
            except:
                cmn.error("build_state_data?")

def build_csv_state(file_list, dir, fn=None):
    fieldnames = ["date", "uid", "name", "id", 
                  "processes", "loadavg-m1",
                  "softirq", "iowait", "intr", "system", "btime", "idle", "user", "irq", "ctxt", "nice",
                  "nr_slab_unreclaimable", "workingset_refault", "nr_anon_pages",
                  "active_file", "cached", "apps", "mapped", "active_anon", "free", "swap_cache",
                  "page_tables", "inactive", "shmem", "committed", "active", "vmalloc_used","slab_cache",
                  "buffers", "swap",
                  # "workingset_activate", "nr_free_pages"
    ]
    build_csv(file_list, dir, fieldnames, build_state_data, None, fn)

##
## helping functions
##
def get_uid(js):
    # check uid
    for d in js:
        if not 'uid' in d:
            cmn.error('skipping ' + f)
            cmn.error(d['hostname'] + ' uid? id: ' + str(d['id']))
            return None
    return [d['uid'] for d in js]

def build_csv(file_list, dir, fnames, build_data, get_fields, fn):
    if(fn):
        cmn.say("writing cvs to "+fn)
        csvfile = open(fn, 'w')
    else:
        csvfile = sys.stdout
    fw = csv.DictWriter(csvfile, delimiter=';', fieldnames=fnames)
    fw.writeheader()
    for f in file_list:
        if(dir): f = dir + '/' + f
        if os.path.exists(f):
            try:
                if(re.search(r'gz$', f)):
                    ds = json.load(gzip.open(f))
                else:
                    ds = json.load(open(f))
            except:
                cmn.error("Cannot read json file. Malformed json? " + f)
            try:
                build_data(f, ds, get_fields, fw)
            except:
                cmn.error("Cannot process json? " + f)
        else:
            cmn.erro("json file? " + f)
   # print(json.dumps(ds, indent=2))
   # csvwriter.writerows(rows)

# Local Variables:
# mode: python
# coding: utf-8
# python-indent-offset: 4
# python-indent-guess-indent-offset: t
# End:
