#!/usr/bin/env python

from twisted.internet import reactor

from pprint import pprint

from opentsdb.async_client import AsyncClient


def rErrback(*args):
    pprint(args)
    reactor.stop()

def rCallback(args):
    #pprint(otsdbResp)
    #pprint(respObj)
    pprint(args)
    reactor.stop()


client = AsyncClient("tsdwww.mon.toolsash1.cloudsys.tmcs", port=80)

d = client.query(**{
    "metric": "nginx.stubstatus.request",
    "tags": {"class": "met"},
    "start": "3m-ago",
    "aggr": "sum"
    })

d.addErrback(rErrback)
d.addCallback(rCallback)

reactor.run()