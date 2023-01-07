# Buzzer

## Webpage part

Here is where I found the tutorial for `aiohttp` with html templates:
`https://us-pycon-2019-tutorial.readthedocs.io/aiohttp_templates_full.html`
and aiohttp-session `https://us-pycon-2019-tutorial.readthedocs.io/aiohttp_session.html`


- put whatever port number you want the page to be hosted on - gunicorn uses its own port
```python
web.run_app(init_app(), port=8888)
```

- run `host_page.py`

Personnaly I use `nginx` to manage the domains and load-balancing. (I guess that's what most people do)

## Docker

Pulled from there
`https://github.com/FrenchCommando/uscis-status`
`https://github.com/RendijsSmukulis/docker-aiohttp-gunicorn`

```cmd
docker build -t buzzerbuild .
docker run -p 1339:1339 buzzerbuild
```

Because I don't want to setup a venv in python in my server - I'll just `docker up --build`.

# Acknowledgement

- this is a nice cheatsheet: `https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet`
- google authentication `https://github.com/vastevenson/flask-google-hosted-authn-demo`
