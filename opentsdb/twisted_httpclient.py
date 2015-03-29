
import StringIO
import gzip

import ujson as json

from zope.interface import implements

from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from twisted.internet.defer import Deferred, succeed
from twisted.internet.protocol import Protocol

from pprint import pprint

class BodyProducer(object):
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(self.body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


class JsonBodyProducer(BodyProducer):

    def __init__(self, body):
        """ Converts request body to a json string """
        self.body = json.dumps(body)
        self.length = len(self.body)


class AsyncHttpResponseProtocol(Protocol):
    def __init__(self, finished_deferred, headers):
        self.headers = headers
        self.finished = finished_deferred
        self.data = ""

    def dataReceived(self, bytes):
        self.data += bytes

    def __ungzip_(self):
        try:
            compressedstream = StringIO.StringIO(self.data)
            gzipper = gzip.GzipFile(fileobj=compressedstream)
            return gzipper.read()
        except Exception,e:
            return json.dumps({"error": str(e)})

    def connectionLost(self, reason):
        if self.headers.hasHeader('content-encoding') and \
                ('gzip' in self.headers.getRawHeaders('content-encoding')):
            self.finished.callback(self.__ungzip_())
        else:
            self.finished.callback(self.data)



class AsyncHttpClient(object):
    """
        Supports json request payload on both HTTP GET and POST

        Args:
            uri            : e.g. http://localhost/api/data
            body           :
            method         : GET or POST
            headers        : (optional)
            connectTimeout : (optional)
    """
    def __init__(self, **kwargs):
        self.headers = {}
        # uri, method, body
        for k,v in kwargs.items():
            setattr(self, k, v)
        
        # Set default method to GET
        if not kwargs.has_key('method'):
            self.method = 'GET'
        # Set default connectTimeout to 3
        if not kwargs.has_key('connectTimeout'):
            self.connectTimeout = 3.0

        # Set default headers
        self.headers['User-Agent'] =  ['AsyncHttpRequest']
        self.headers['Accept-Encoding'] = ['gzip']

        self.body = None

        self.agent = Agent(reactor, connectTimeout=self.connectTimeout)

        self.__deferredResponse = Deferred()

        if kwargs.has_key('body'):
            if self.headers.has_key('Content-Type'):
                for ctype in self.headers['Content-Type']:
                    # json request
                    if ctype.startswith('application/json'):
                        self.body = JsonBodyProducer(kwargs['body'])
                        break
            # generic request
            if self.body == None:
                self.body = BodyProducer(kwargs['body'])
            

        # Make the http request
        self.__d_agent = self.agent.request(
                self.method, self.url,
                Headers(self.headers), self.body)


    def __readResponseCallback(self, response, userCb, *cbargs):
        response.deliverBody(AsyncHttpResponseProtocol(self.__deferredResponse, response.headers))
        self.__deferredResponse.addCallback(userCb, *([response]+list(cbargs)))
        return self.__deferredResponse

    def __readErrorCallback(self, error, userCb, *cbargs):
        self.__deferredResponse.addErrback(userCb, *cbargs)

    def addResponseCallback(self, callback, *cbargs):
        self.__d_agent.addCallback(self.__readResponseCallback, callback, *cbargs)
        return self.__deferredResponse

    def addResponseErrback(self, callback, *cbargs):
        self.__d_agent.addErrback(self.__readErrorCallback, callback, *cbargs)

    def cancelRequest(self):
        try:
            self.__deferredResponse.cancel()
            self.__d_agent.cancel()
        except Exception,e:
            logger.debug(str(e))
