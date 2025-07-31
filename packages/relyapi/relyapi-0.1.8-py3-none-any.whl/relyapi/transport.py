import os

import httpx

RELY_API_ADDRESS = os.environ.get("RELY_API_ADDRESS", 'https://forwrad.relyapi.com')


class ForwardingTransport(httpx.BaseTransport):
    def __init__(self):
        self._client = httpx.Client(base_url=RELY_API_ADDRESS)

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        payload = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "body": request.read().decode("utf-8") if request.content else None
        }

        forward_resp = self._client.post("/rely/worker/bypass/forward", json=payload)

        return httpx.Response(
            status_code=forward_resp.status_code,
            headers=forward_resp.headers,
            content=forward_resp.content,
            request=request
        )

    def aclose(self):
        self._client.close()


class AsyncForwardingTransport(httpx.AsyncBaseTransport):
    def __init__(self):
        self._client = httpx.AsyncClient(base_url=RELY_API_ADDRESS)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        payload = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "body": await request.aread()
        }

        forward_resp = await self._client.post(
            "/rely/worker/bypass/forward", json=payload
        )
        return httpx.Response(
            status_code=forward_resp.status_code,
            headers=forward_resp.headers,
            content=forward_resp.content,
            request=request
        )

    async def aclose(self):
        await self._client.aclose()
