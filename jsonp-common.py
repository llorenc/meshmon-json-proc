#!/usr/bin/env python
# -*- coding: utf-8 -*-
## Format data gathered from qMp nodes in GuifiSants
## http://dsg.ac.upc.edu/qmpsu/index.php
## jsonp-common.py
## (c) Llorenç Cerdà-Alabern, May 2020.
## debug: import pdb; pdb.set_trace()

import click   ## https://click.palletsprojects.com/en/7.x
import sys
import re
import datetime

verbose = False

def abort(msg):
    click.secho(msg, fg="red")
    sys.exit()

def error(msg):
    if not type(msg) is str:
        msg = str(msg)
    click.secho(msg, fg="red")

def say(msg):
    if not type(msg) is str:
        msg = str(msg)
    click.secho(msg, fg="green")

def get_date(f):
    re_pat = re.compile('(?P<date>\d\d-\d\d-\d\d_\d\d-\d\d-\d\d)', re.VERBOSE)
    match = re_pat.search(f)
    if match:
        return(match.group('date'))
    abort("get_date: date? "+f)

def get_date_ym(f):
    re_pat = re.compile('(?P<ym>\d\d-\d\d)-\d\d_', re.VERBOSE)
    match = re_pat.search(f)
    if match:
        return(match.group('ym'))
    abort("get_date_ym: year-month? "+f)

def get_epoch(f):
    re_pat = re.compile('(?P<Y>\d\d)-(?P<M>\d\d)-(?P<D>\d\d)_(?P<h>\d\d)-(?P<m>\d\d)-(?P<s>\d\d)', re.VERBOSE)
    match = re_pat.search(f)
    if match:
        return (datetime.datetime(int('20'+match.group('Y')), int(match.group('M')), int(match.group('D')), 
                                int(match.group('h')), int(match.group('m')), int(match.group('s')))
                -datetime.datetime(1970,1,1)).total_seconds()
    abort("get_date_ym: year-month? "+f)

# Local Variables:
# mode: python
# coding: utf-8
# python-indent-offset: 4
# python-indent-guess-indent-offset: t
# End:
