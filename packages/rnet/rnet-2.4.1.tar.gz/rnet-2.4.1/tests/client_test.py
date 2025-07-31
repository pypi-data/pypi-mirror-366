import pytest
import rnet
from rnet import Cookie, Impersonate, ImpersonateOS, ImpersonateOption, HeaderMap


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=1, reruns_delay=2)
async def test_inherit_client():
    class SubClient(rnet.Client):
        def __init__(self, **kwargs):
            self.test_var = "test"
            self.cookie_jar = None

    client = SubClient(impersonate=Impersonate.Chrome133)
    url = "https://google.com"
    response = await client.get(url)
    text = await response.text()
    assert text is not None
    assert client.cookie_jar is None
    assert client.test_var == "test"
    client.update(
        impersonate=ImpersonateOption(
            impersonate=Impersonate.Firefox135,
            impersonate_os=ImpersonateOS.Windows,
            skip_headers=False,
        )
    )
    assert (
        client.user_agent
        == "Mozilla/5.0 (Windows NT 10.0; rv:135.0) Gecko/20100101 Firefox/135.0"
    )
    assert client.test_var == "test"


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_update_headers():
    client = rnet.Client()
    headers = {"user-agent": "rnet"}
    client.update(headers=headers)
    assert client.headers["user-agent"] == b"rnet"

    client.update(headers=HeaderMap(headers))
    assert client.headers["user-agent"] == b"rnet"


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_set_cookie():
    url = "https://httpbin.org/cookies"
    client = rnet.Client(cookie_store=True)

    cookie = Cookie(name="foo", value="bar")
    client.set_cookie(url, cookie)
    assert client.get_cookies(url) == b"foo=bar"

    response = await client.get(url)
    json = await response.json()
    assert json["cookies"] == {"foo": "bar"}


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_update_impersonate():
    client = rnet.Client(impersonate=Impersonate.Firefox133)
    assert (
        client.user_agent
        == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0"
    )
    client.update(
        impersonate=ImpersonateOption(
            impersonate=Impersonate.Firefox135,
            impersonate_os=ImpersonateOS.Windows,
            skip_headers=False,
        )
    )
    assert (
        client.user_agent
        == "Mozilla/5.0 (Windows NT 10.0; rv:135.0) Gecko/20100101 Firefox/135.0"
    )


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=3, reruns_delay=2)
async def test_alps_new_endpoint():
    url = "https://google.com"
    client = rnet.Client(impersonate=Impersonate.Chrome133)
    response = await client.get(url)
    text = await response.text()
    assert text is not None
