from flask import Flask, request, render_template, redirect, session
from flask_session import Session

from dotenv import load_dotenv
import os, requests
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
Session(app)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = " ".join(["gist"])
API_BASE = "https://api.github.com"

@app.route("/")
def index():
    if session.get("user"):
        return redirect("/home")
    
    return render_template("index.html")

@app.route("/home")
def home():
    if not session.get("user"):
        return redirect("/login")
    
    r = requests.get("https://api.github.com/gists?per_page=100", headers={
        "Authorization": f"token {session['user']['access_token']}"
    }).json()

    gists = []
    for gist in r:
        name = list(gist['files'].keys())[0]
        if not name.startswith("quickwrite--"): continue
        content = requests.get(gist['files'][name]['raw_url']).text
        gists.append({
            "name": name.replace("quickwrite--", "").replace(".md", ""),
            "content": content,
            "id": gist['id'],
            "created": datetime.strptime(gist['created_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%m-%d %Y")
        })

    username = session["user"]["username"]

    return render_template("home.html", gists=gists, username=username)

@app.route("/login")
def login():
    return redirect(f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&prompt=true")

@app.route("/callback")
def callback():
    code = request.args.get('code')
    if code is None:
        return redirect('/login')
    
    r = requests.post("https://github.com/login/oauth/access_token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }, headers={
        "Accept": "application/json"
    })

    if r.status_code != 200:
        return redirect('/login')

    data = r.json()
    token = data['access_token']

    r = requests.get(f"{API_BASE}/user", headers={
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + token
    })

    if r.status_code != 200: return redirect('/login')

    username = r.json()['login']
    session['user'] = {
        "username": username,
        "access_token": token
    }

    return redirect('/home')

@app.post("/write")
def write():
    content = request.form.get('content')
    name = request.form.get('name')
    username = session['user']['username']
    access_token = session['user']['access_token']

    r = requests.post(f"{API_BASE}/gists", json={
        "files": {
            f"quickwrite--{name}.md": {
                "content": content
            }
        }
    }, headers={
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github+json"
    }).json()

    gId = r['id']

    return redirect(f"/{username}/{gId}")


@app.route("/<username>/<gistId>")
def viewGist(username, gistId):
    r = requests.get(f"{API_BASE}/gists/{gistId}").json()
    name = list(r['files'].keys())[0]
    content = requests.get(r['files'][name]['raw_url']).text
    created = datetime.strptime(r['created_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%m-%d %Y")

    return render_template("gist.html", content=content, name=name.replace("quickwrite--", "").replace(".md", ""), created=created, username=username)


@app.route("/<username>")
def viewUser(username):
    if "." in username: return redirect("/home")
    r = requests.get(f"{API_BASE}/users/{username}/gists").json()

    gists = []
    for gist in r:
        name = list(gist['files'].keys())[0]
        if not name.startswith("quickwrite--"): continue
        content = requests.get(gist['files'][name]['raw_url']).text
        gists.append({
            "name": name.replace("quickwrite--", "").replace(".md", ""),
            "content": content,
            "id": gist['id'],
            "created": datetime.strptime(gist['created_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%m-%d %Y")
        })

    return render_template("user.html", gists=gists, username=username)

app.run(host="0.0.0.0", port=6294, debug=True)