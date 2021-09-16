from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    send_from_directory,
)
import os
import codecs
from flask.helpers import send_file
import random
import requests

app = Flask(__name__)
UPLOAD_FOLDER = "./data"
ALLOWED_EXTENSIONS = {"nfo"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
secret_key = "Super Random Secret Key"
app.config["SECRET_KEY"] = secret_key


def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[])
    try:
        lst = os.listdir(path)
    except OSError:
        pass  # ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree["children"].append(make_tree(fn))
            else:
                tree["children"].append(dict(name=name))
    return tree


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def upload_file():
    try:
        if request.method == "POST":
            if "file" not in request.files:
                flash("No file part")
                return redirect(request.url)
            file = request.files["file"]
            rls_name = request.form["rls"]
            if file.filename == "":
                return ()
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                os.rename(f"./data/{filename}", f"./data/{rls_name}.nfo")
                return render_template("complete.html", rls_name=rls_name)
            else:
                error_msg = "Only NFO Files Are Allowed To Be Uploaded!"
                error_code = 403
                return render_template(
                    "error.html", error_msg=error_msg, error_code=error_code
                )
        random_nfos = []
        for i in range(0, 10):
            rand = random.choice(os.listdir("./data")).strip(".nfo")
            random_nfos.append(rand)
        return render_template("index.html", random_nfos=random_nfos)
    except FileExistsError:
        os.remove(f"./data/{filename}")
        error_msg = "NFO Already Exists!"
        error_code = 403
        return render_template("error.html", error_msg=error_msg, error_code=error_code)


@app.route("/api/upload", methods=["GET", "POST"])
def api_upload():
    try:
        if request.method == "POST":
            if "file" not in request.files:
                return "No file part"
            file = request.files["file"]
            rls_name = request.form["rls"]
            if file.filename == "":
                return redirect("No selected file")
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                os.rename(f"./data/{filename}", f"./data/{rls_name}.nfo")
                response = {
                    "nfo_dlpath": "/nfo/dl/" + rls_name,
                    "nfo_path": "/nfo/" + rls_name,
                    "success": "True",
                }
                return response
            else:
                error_msg = "Only NFO Files Are Allowed To Be Uploaded!"
                error_code = 403
                response = {
                    "message": str(error_msg),
                    "error_code": error_code,
                    "success": "False",
                }
                return response
        return 'NFO API, go to <a href="/api">here</a> for docs'
    except FileExistsError:
        os.remove(f"./data/{filename}")
        error_msg = "NFO Already Exists!"
        error_code = 409
        response = {
            "message": str(error_msg),
            "error_code": error_code,
            "success": "False",
        }
        return response


@app.route("/api")
def api():
    return render_template("api.html")


@app.route("/nfo/<rls>")
def nfo(rls):
    try:
        nfo_path = f"./data/{rls}.nfo"
        nfo_title = f"{rls}.nfo"
        nfo = codecs.open(f"{nfo_path}", "r", "cp437").read()
        return render_template("nfo.html", nfo=nfo, nfo_title=nfo_title, rls=rls)
    except FileNotFoundError:
        error_msg = "NFO Not Found, be the First to add it!"
        error_code = 404
        return render_template("error.html", error_msg=error_msg, error_code=error_code)


@app.route("/nfo/dl/<rls>")
def dl(rls):
    nfo_name = f"{rls}.nfo"
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], nfo_name, as_attachment=True
    )


@app.route("/api/nfo/dl/<nfo>")
def api_dl(nfo):
    nfo_name = f"{nfo}"
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], nfo_name, as_attachment=True
    )


@app.route("/data")
def dirtree():
    path = os.path.expanduser("./data")
    return render_template("dirtree.html", tree=make_tree(path))


if __name__ == "__main__":
    app.run(debug=True)
