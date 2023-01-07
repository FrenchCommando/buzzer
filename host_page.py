from aiohttp import web
import aiohttp_jinja2
import jinja2
from pathlib import Path
import aiohttp_session
from typing import Callable, Awaitable, Dict, Any
from gattlib import GATTRequester


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
    if require_login_variable:
        if not username:
            raise web.HTTPSeeOther(location="/login")
    return await handler(request)


@router.get("/login")
@aiohttp_jinja2.template("login.html")
async def login(request: web.Request) -> Dict[str, Any]:
    return {}


@router.post("/login")
async def login_apply(request: web.Request) -> None:
    session = await aiohttp_session.get_session(request)
    form = await request.post()
    session["username"] = form.get("login", "LoggedInUser")
    raise web.HTTPSeeOther(location="/")


@router.post("/logout")
async def logout(request: web.Request) -> None:
    session = await aiohttp_session.get_session(request)
    session["username"] = None
    raise web.HTTPSeeOther(location="/")


async def username_ctx_processor(request: web.Request) -> Dict[str, Any]:
    session = await aiohttp_session.get_session(request)
    username = session.get("username")
    return {"username": username}


@router.get('/')
@aiohttp_jinja2.template("base.html")
async def greet_user(request: web.Request) -> Dict[str, Any]:
    return {}


@router.get('/open')
@require_login
@aiohttp_jinja2.template("target.html")
async def show_present(request: web.Request) -> Dict[str, Any]:
    with open(str(Path(__file__).parent / "devices.txt")) as f:
        devices = f.readlines()
    for device in devices:
        req = GATTRequester(device)
        req.write_by_handle(0x16, b'\x57\x01\x00')
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
    web.run_app(init_app(), port=8888)
