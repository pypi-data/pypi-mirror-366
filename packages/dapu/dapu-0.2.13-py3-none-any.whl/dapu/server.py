r"""
HTTP teenus lokaalse Confluence litsentside probleemi lahendamiseks

Käivitamiseks (Windows)
cd C:\Users\indrek\Dev\tuvi\src\pigeon
uvicorn main:app --port 17005 --host 192.168.0.235 

API DOC: http://192.168.0.235:17005/openapi.json

Kuula välist IP-d, siis saab Windows Firewall inbounding rule abil lubada juurdepääsu (ei ole lubatud hetkel)
http://192.168.0.235:17005/api/letter/prepare POST
http://192.168.0.235:17005/api/letter/send/{letter_id} 

Käivitamiseks (docker linux)
cd /srv/dapu
uvicorn server:app --port 18902 --host 0.0.0.0 --forwarded-allow-ips='192.168.0.4'

"""

__version__ = '0.1.3' # peab olema enne import => saab olla ainult static/hardcoded

import os
import signal
import sys
# välised komponendid
from loguru import logger
from fastapi import FastAPI, Response, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse, FileResponse, HTMLResponse
# omad
#from prepare import prepare_context, AppContext
#from router_letter import router as router_letter # huvitav, kas selline dot-notation tegelikult ka toimib?
from versops import version_from_pyproject_file

name = "Dapu API"
version = version_from_pyproject_file("../../pyproject.toml") # 2 taset üles 
if version == "":
    version = version_from_pyproject_file("./pyproject.toml") # siitsamast
if version == "":
    version = __version__
    #print("probleem versiooniga")
    #sys.exit(2)

# context: AppContext | None = prepare_context()
# if context is None:
#     sys.exit(1)

logger.info(f"{name} {version} is starting...")
app = FastAPI(title=name, version=version)

#app.state.app_context = context # tüüpi AppContext (olemas ka pöörduste vahel, seal on nt AB ühendus) (mitte panna sinna pöörduse infot!)

@app.get("/status", include_in_schema=False, response_class=PlainTextResponse)
def read_root_status():
    return Response("server is running indeed")

@app.get("/favicon.ico", include_in_schema=False, response_class=FileResponse) 
def read_favicon(request: Request):
    """
    favicon is app.png in /static/
    """
    #context: AppContext = request.app.state.app_context  # app context teab kaustadest
    #path = os.path.join(context.dir_root, "static", "app.png")
    dir_root = "/srv/dapu"
    home = dir_root if dir_root is not None else "."
    dir_root = os.path.realpath(home)
    path = os.path.join(dir_root, "static", "app.png")
    return FileResponse(path, media_type='image/png')

@app.get("/info", include_in_schema=False, response_class=HTMLResponse)
def read_root_info():
    html = f"""
    <h1>Resources</h1>
    <div>Just status: <a href="/status">status</a></div>
    <div>Definition (JSON): <a href="{app.openapi_url}">OpenAPI</a></div>
    <div>Services are mostly /api/letter </div>
    """
    return HTMLResponse(html)


# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     context: AppContext = request.app.state.app_context
#     context.send_outside(f"consumation of {request.url}")
#     return await call_next(request)



# context.send_outside(f"API is starting for {context.my_shift}")
