import aiohttp
import logging
import os
import pathlib
import requests
import time
from aiohttp import web
import aiohttp_jinja2
import aiohttp_session
import jinja2
from pathlib import Path
from typing import Callable, Awaitable, Dict, Any
import google.oauth2.credentials
import google_auth_oauthlib.flow
import google.auth.transport.requests
from google.oauth2 import id_token
from pip._vendor import cachecontrol
from gattlib import GATTRequester


logging.basicConfig(filename=str(Path(__file__).parent / 'buzzer-log.txt'), filemode='a', level=logging.DEBUG)


with open(str(Path(__file__).parent / "devices.txt")) as f:
    devices = f.readlines()
with open(str(Path(__file__).parent / "authorized_emails.txt")) as f:
    authorized_emails = [s.strip() for s in f.readlines()]


client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
    redirect_uri="http://localhost/callback",
)

authorization_url, state = flow.authorization_url(
    # Enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.
    access_type='offline',
    # Enable incremental authorization. Recommended as a best practice.
    include_granted_scopes='true',
)

router = web.RouteTableDef()
_WebHandler = Callable[[web.Request], Awaitable[web.StreamResponse]]


def require_login(func: _WebHandler) -> _WebHandler:
    func.__require_login__ = True  # type: ignore
    return func


@web.middleware
async def check_login(
        request: web.Request,
        handler: _WebHandler
) -> web.StreamResponse:
    require_login_variable = getattr(handler, "__require_login__", False)
    session = await aiohttp_session.get_session(request)
    username = session.get("username")
    email = session.get("email")
    if require_login_variable:
        if not username:
            raise web.HTTPSeeOther(location="/login")
        else:
            if email in authorized_emails:
                return await handler(request)
            else:
                raise aiohttp.web.HTTPUnauthorized()
    return await handler(request)


@router.get("/login")
@aiohttp_jinja2.template("login.html")
async def login(request: web.Request) -> Dict[str, Any]:
    return {}


@router.post("/login")
async def login_apply(request: web.Request):
    session = await aiohttp_session.get_session(request)
    authorization_url_value, state = flow.authorization_url()
    session["state"] = state
    raise web.HTTPFound(authorization_url_value)


@router.get("/callback")
async def callback(request: web.Request):
    flow.fetch_token(code=request.rel_url.query.get("code", ''))
    session = await aiohttp_session.get_session(request)
    if not session["state"] == request.rel_url.query.get("state", ''):
        raise aiohttp.web.HTTPUnauthorized()

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=credentials.client_id,
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["username"] = session["name"]
    session["email"] = id_info.get("email")

    raise web.HTTPSeeOther(location="/")


@router.post("/logout")
async def logout(request: web.Request) -> None:
    session = await aiohttp_session.get_session(request)
    session["username"] = None
    session["google_id"] = None
    session["name"] = None
    session["username"] = None
    session["email"] = None
    raise web.HTTPSeeOther(location="/")


async def username_ctx_processor(request: web.Request) -> Dict[str, Any]:
    session = await aiohttp_session.get_session(request)
    username = session.get("username")
    return {"username": username}


@router.get('/')
@aiohttp_jinja2.template("base.html")
async def greet_user(request: web.Request) -> Dict[str, Any]:
    print("Home")
    return {}


@router.get('/open')
@require_login
@aiohttp_jinja2.template("target.html")
async def show_present(request: web.Request) -> Dict[str, Any]:
    for device in devices:
        print(device)
        req = GATTRequester(device, False)
        print("Pre-Connect")
        req.connect(False, 'random')
        n_remaining = 10
        while n_remaining > 0:
            print("Pre-sleep")
            time.sleep(1)
            if req.is_connected():
                req.write_by_handle(0x16, b'\x57\x01\x00')
                print("Message Sent")
                req.disconnect()
                break
            n_remaining -= 1
    print('Command execution successful')
    return {}


async def init_app() -> web.Application:
    app = web.Application()
    app.add_routes(router)
    aiohttp_session.setup(app, aiohttp_session.SimpleCookieStorage())
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(str(Path(__file__).parent / "templates")),
        context_processors=[username_ctx_processor],
    )
    app.middlewares.append(check_login)
    return app


if __name__ == '__main__':
    web.run_app(init_app(), port=1337)
