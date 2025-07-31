import httpx

from relyapi.transport import ForwardingTransport, AsyncForwardingTransport


class Client(httpx.Client):
    def __init__(self, *args, **kwargs):
        kwargs["transport"] = ForwardingTransport()
        super().__init__(*args, **kwargs)


class AsyncClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        kwargs["transport"] = AsyncForwardingTransport()
        super().__init__(*args, **kwargs)
