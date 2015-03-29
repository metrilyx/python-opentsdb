
from twisted.internet import reactor

from twisted.internet.defer import Deferred

from twisted_httpclient import AsyncHttpClient
from client import BaseClient

from opentsdb_pandas.response import OpenTSDBResponse

from pprint import pprint

class AsyncClient(BaseClient):

    def __callback(self, respData, respObj, dfd):
        dfd.callback([OpenTSDBResponse(respData), respObj])

    def __errback(self, respData, respObj, dfd):
        dfd.errback([respData, respObj])

    def query(self, **kwargs):
        c = AsyncHttpClient(url=self.queryUrl(**kwargs))
        
        dfd = Deferred()
        c.addResponseErrback(self.__errback, dfd)
        c.addResponseCallback(self.__callback, dfd)
        return dfd


