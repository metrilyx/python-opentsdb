#!/usr/bin/env python

from pprint import pprint

from opentsdb.client import Client


client = Client("tsdwww.mon.toolsash1.cloudsys.tmcs", port=80)

rslt = client.query(**{
    "metric": "nginx.stubstatus.request",
    "tags": {"class": "met"},
    "start": "3m-ago",
    "aggr": "sum"
    })
pprint(rslt)
