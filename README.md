python-opentsdb
===============
OpenTSDB client library with pandas support.

This module provides 2 types of clients:

* **client.Client**: A client using the requests module

* **async_client.AsyncClient**: Async client using twisted. 

Examples:

**Regular client**:

    from opentsdb.client import Client

    if __name__ == "__main__":
        
        client = Client("my.opentsdb.org", port=80)

        rslt = client.query(**{
            "metric": "nginx.stubstatus.request",
            "tags": {"type": "foo"},
            "start": "3m-ago",
            "aggr": "sum"
            })
        
        # OpenTSDBResponse object (opentsdb-pandas)
        print rslt


**Async client**:

    from twisted.internet import reactor
    from twisted.python.failure import Failure

    from opentsdb.async_client import AsyncClient
    
    def rErrback(*args):
        print "OpenTSDB error:", args[0]
        print "HTTP response:", args[1]
        reactor.stop()
        # If you do not return the Failure() you may experience a subsequent run of CallBack() with errored data
        # use http://twistedmatrix.com/documents/12.0.0/core/howto/defer.html for reference
        return Failure() # See note on Return Failure for this.

    def rCallback(args):
        print "OpenTSDB response:", args[0]
        print "HTTP response:", args[1]
        reactor.stop()


    if __name__ == "__main__":

        client = AsyncClient("my.opentsdb.org", port=80)

        d = client.query(**{
            "metric": "nginx.stubstatus.request",
            "tags": {"type": "foo"},
            "start": "3m-ago",
            "aggr": "sum"
            })

        d.addErrback(rErrback)
        d.addCallback(rCallback)

        reactor.run()
