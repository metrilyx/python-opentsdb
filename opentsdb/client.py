import requests

from opentsdb_pandas.response import OpenTSDBResponse

class BaseClient(object):

    def __init__(self, host, port=4242, ssl=False):
        if ssl:
            self.url = "https://%s:%d" % (host, port)
        else:
            self.url = "http://%s:%d" % (host, port)

    def queryUrl(self, **kwargs):
        return "%s/api/query?%s" % (self.url, self.__urlEncodedParams(**kwargs))

    def __urlEncodedParams(self, aggr="sum", rate=False, end=None, **kwargs):

        timeStr = "start=%s" % (kwargs["start"])
        if end != None:
            timeStr += "&end=" + end

        if rate:
            prefix = "%s:rate:%s" % (aggr, kwargs["metric"])
        else:
            prefix = "%s:%s" % (aggr, kwargs["metric"])

        # TODO: check
        tagsStr = ",".join([ "%s=%s" % (k, kwargs["tags"][k]) for k in sorted(kwargs["tags"].keys()) ])
        
        if tagsStr != "":
            return "%s&m=%s{%s}" % (timeStr, prefix, tagsStr)
        else:
            return "%s&m=%s" % (timeStr, prefix)


class Client(BaseClient):

    def query(self, **kwargs):
        resp = requests.get(self.queryUrl(**kwargs))
        if resp.status_code >= 200 and resp.status_code < 400:
            return OpenTSDBResponse(resp.text)
        # error
        return resp.text



