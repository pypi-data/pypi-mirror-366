from unittest.mock import patch

import pytest
from yarl import URL

from python_socks import ProxyType, ProxyError, ProxyTimeoutError, ProxyConnectionError
from tests.config import (
    PROXY_HOST_IPV4,
    SOCKS5_PROXY_PORT,
    LOGIN,
    PASSWORD,
    SKIP_IPV6_TESTS,
    SOCKS5_IPV4_URL,
    SOCKS5_IPV4_URL_WO_AUTH,
    SOCKS5_IPV6_URL,
    SOCKS4_URL,
    HTTP_PROXY_URL,
    TEST_URL_IPV4,
    SOCKS5_IPV4_HOSTNAME_URL,
    TEST_URL_IPV4_HTTPS,
    HTTPS_PROXY_URL,
)
from tests.mocks import getaddrinfo_async_mock

anyio = pytest.importorskip('anyio')

from python_socks.async_.anyio._resolver import Resolver  # noqa: E402
from python_socks.async_.anyio.v2 import Proxy  # noqa: E402
from python_socks.async_.anyio.v2 import ProxyChain  # noqa: E402
from python_socks.async_.anyio.v2._proxy import AnyioProxy  # noqa: E402


async def make_request(
    proxy: AnyioProxy,
    url: str,
    resolve_host=False,
    timeout=None,
    ssl_context=None,
):
    # import anyio
    with patch(
        'anyio._core._sockets.getaddrinfo',
        new=getaddrinfo_async_mock(anyio.getaddrinfo),
    ):
        url = URL(url)

        dest_host = url.host
        if resolve_host:
            resolver = Resolver()
            _, dest_host = await resolver.resolve(url.host)

        dest_ssl = None
        if url.scheme == 'https':
            dest_ssl = ssl_context

        stream = await proxy.connect(
            dest_host=dest_host,
            dest_port=url.port,
            dest_ssl=dest_ssl,
            timeout=timeout,
        )

        # fmt: off
        request = (
            'GET {rel_url} HTTP/1.1\r\n'
            'Host: {host}\r\n'
            'Connection: close\r\n\r\n'
        )
        # fmt: on

        request = request.format(rel_url=url.path_qs, host=url.host)
        request = request.encode('ascii')

        await stream.write_all(request)

        response = await stream.read(1024)

        status_line = response.split(b'\r\n', 1)[0]
        version, status_code, *reason = status_line.split()

        await stream.close()

        return int(status_code)


@pytest.mark.parametrize('url', (TEST_URL_IPV4, TEST_URL_IPV4_HTTPS))
@pytest.mark.parametrize('rdns', (True, False))
@pytest.mark.parametrize('resolve_host', (True, False))
@pytest.mark.anyio
async def test_socks5_proxy_ipv4(url, rdns, resolve_host, target_ssl_context):
    proxy = Proxy.from_url(SOCKS5_IPV4_URL, rdns=rdns)
    status_code = await make_request(
        proxy=proxy,
        url=url,
        resolve_host=resolve_host,
        ssl_context=target_ssl_context,
    )
    assert status_code == 200


@pytest.mark.parametrize('url', (TEST_URL_IPV4, TEST_URL_IPV4_HTTPS))
@pytest.mark.anyio
async def test_socks5_proxy_hostname_ipv4(url, target_ssl_context):
    proxy = Proxy.from_url(SOCKS5_IPV4_HOSTNAME_URL)
    status_code = await make_request(
        proxy=proxy,
        url=url,
        ssl_context=target_ssl_context,
    )
    assert status_code == 200


@pytest.mark.parametrize('url', (TEST_URL_IPV4, TEST_URL_IPV4_HTTPS))
@pytest.mark.parametrize('rdns', (None, True, False))
@pytest.mark.anyio
async def test_socks5_proxy_ipv4_with_auth_none(url, rdns, target_ssl_context):
    proxy = Proxy.from_url(SOCKS5_IPV4_URL_WO_AUTH, rdns=rdns)
    status_code = await make_request(
        proxy=proxy,
        url=url,
        ssl_context=target_ssl_context,
    )
    assert status_code == 200


@pytest.mark.anyio
async def test_socks5_proxy_with_invalid_credentials():
    proxy = Proxy.create(
        proxy_type=ProxyType.SOCKS5,
        host=PROXY_HOST_IPV4,
        port=SOCKS5_PROXY_PORT,
        username=LOGIN,
        password=PASSWORD + 'aaa',
    )
    with pytest.raises(ProxyError):
        await make_request(proxy=proxy, url=TEST_URL_IPV4)


@pytest.mark.anyio
async def test_socks5_proxy_with_connect_timeout():
    proxy = Proxy.create(
        proxy_type=ProxyType.SOCKS5,
        host=PROXY_HOST_IPV4,
        port=SOCKS5_PROXY_PORT,
        username=LOGIN,
        password=PASSWORD,
    )
    with pytest.raises(ProxyTimeoutError):
        await make_request(proxy=proxy, url=TEST_URL_IPV4, timeout=0.0001)


@pytest.mark.anyio
async def test_socks5_proxy_with_invalid_proxy_port(unused_tcp_port):
    proxy = Proxy.create(
        proxy_type=ProxyType.SOCKS5,
        host=PROXY_HOST_IPV4,
        port=unused_tcp_port,
        username=LOGIN,
        password=PASSWORD,
    )
    with pytest.raises(ProxyConnectionError):
        await make_request(proxy=proxy, url=TEST_URL_IPV4)


@pytest.mark.parametrize('url', (TEST_URL_IPV4, TEST_URL_IPV4_HTTPS))
@pytest.mark.skipif(SKIP_IPV6_TESTS, reason="TravisCI doesn't support ipv6")
@pytest.mark.anyio
async def test_socks5_proxy_ipv6(url, target_ssl_context):
    proxy = Proxy.from_url(SOCKS5_IPV6_URL)
    status_code = await make_request(
        proxy=proxy,
        url=url,
        ssl_context=target_ssl_context,
    )
    assert status_code == 200


@pytest.mark.parametrize('url', (TEST_URL_IPV4, TEST_URL_IPV4_HTTPS))
@pytest.mark.parametrize('rdns', (None, True, False))
@pytest.mark.parametrize('resolve_host', (True, False))
@pytest.mark.anyio
async def test_socks4_proxy(url, rdns, resolve_host, target_ssl_context):
    proxy = Proxy.from_url(SOCKS4_URL, rdns=rdns)
    status_code = await make_request(
        proxy=proxy,
        url=url,
        resolve_host=resolve_host,
        ssl_context=target_ssl_context,
    )
    assert status_code == 200


@pytest.mark.parametrize('url', (TEST_URL_IPV4, TEST_URL_IPV4_HTTPS))
@pytest.mark.anyio
async def test_http_proxy(url, target_ssl_context):
    proxy = Proxy.from_url(HTTP_PROXY_URL)
    status_code = await make_request(
        proxy=proxy,
        url=url,
        ssl_context=target_ssl_context,
    )
    assert status_code == 200


@pytest.mark.parametrize('url', (TEST_URL_IPV4, TEST_URL_IPV4_HTTPS))
@pytest.mark.anyio
async def test_secure_proxy(url, target_ssl_context, proxy_ssl_context):
    proxy = Proxy.from_url(HTTPS_PROXY_URL, proxy_ssl=proxy_ssl_context)
    status_code = await make_request(
        proxy=proxy,
        url=url,
        ssl_context=target_ssl_context,
    )
    assert status_code == 200


@pytest.mark.parametrize('url', (TEST_URL_IPV4, TEST_URL_IPV4_HTTPS))
@pytest.mark.anyio
async def test_proxy_chain(url, target_ssl_context):
    proxy = ProxyChain(
        [
            Proxy.from_url(SOCKS5_IPV4_URL),
            Proxy.from_url(SOCKS4_URL),
            Proxy.from_url(HTTP_PROXY_URL),
        ]
    )
    status_code = await make_request(
        proxy=proxy,  # type: ignore
        url=url,
        ssl_context=target_ssl_context,
    )
    assert status_code == 200
