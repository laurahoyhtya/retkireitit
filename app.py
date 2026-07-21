import re
import secrets
import sqlite3

from flask import Flask
from flask import abort, flash, redirect, render_template, request, session
import markupsafe

import config
import routes
import users


app = Flask(__name__)
app.secret_key = config.SECRET_KEY


def require_login():
    if "user_id" not in session:
        abort(403)


def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if "csrf_token" not in session:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)


def get_route_form_data():
    name = request.form["name"].strip()
    area = request.form["area"].strip()
    start_point = request.form["start_point"].strip()
    length_text = request.form["length_km"].strip()
    description = request.form["description"].strip()

    error_message = None
    length_km = None
    if not name or len(name) > 100:
        error_message = "Reitin nimen tulee olla 1–100 merkkiä pitkä"
    elif not area or len(area) > 100:
        error_message = "Alueen tulee olla 1–100 merkkiä pitkä"
    elif not start_point or len(start_point) > 100:
        error_message = "Lähtöpaikan tulee olla 1–100 merkkiä pitkä"
    elif not re.fullmatch(r"[0-9]{1,4}([.][0-9]{1,2})?", length_text):
        error_message = "Anna pituus kilometreinä, esimerkiksi 5.5"
    else:
        length_km = float(length_text)
        if length_km <= 0 or length_km > 1000:
            error_message = "Pituuden tulee olla yli 0 ja enintään 1000 kilometriä"

    if not error_message and (not description or len(description) > 5000):
        error_message = "Kuvauksen tulee olla 1–5000 merkkiä pitkä"

    if error_message:
        flash("VIRHE: " + error_message)
        return None

    return {
        "name": name,
        "area": area,
        "start_point": start_point,
        "length_km": length_km,
        "description": description
    }


@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)


@app.route("/")
def index():
    all_routes = routes.get_routes()
    return render_template("index.html", routes=all_routes)


@app.route("/find_route")
def find_route():
    query = request.args.get("query", "").strip()
    if len(query) > 100:
        abort(403)
    results = routes.find_routes(query) if query else []
    return render_template("find_route.html", query=query, results=results)


@app.route("/route/<int:route_id>")
def show_route(route_id):
    route = routes.get_route(route_id)
    if not route:
        abort(404)
    return render_template("show_route.html", route=route)


@app.route("/new_route")
def new_route():
    require_login()
    return render_template("new_route.html", filled={})


@app.route("/create_route", methods=["POST"])
def create_route():
    require_login()
    check_csrf()

    data = get_route_form_data()
    if not data:
        return render_template("new_route.html", filled=request.form)

    route_id = routes.add_route(data, session["user_id"])
    flash("Reitti lisättiin")
    return redirect("/route/" + str(route_id))


@app.route("/edit_route/<int:route_id>")
def edit_route(route_id):
    require_login()
    route = routes.get_route(route_id)
    if not route:
        abort(404)
    if route["user_id"] != session["user_id"]:
        abort(403)

    return render_template("edit_route.html", route_id=route_id,
                           filled=route)


@app.route("/update_route", methods=["POST"])
def update_route():
    require_login()
    check_csrf()

    route_id = request.form["route_id"]
    route = routes.get_route(route_id)
    if not route:
        abort(404)
    if route["user_id"] != session["user_id"]:
        abort(403)

    data = get_route_form_data()
    if not data:
        return render_template("edit_route.html", route_id=route_id,
                               filled=request.form)

    routes.update_route(route_id, data)
    flash("Reitin tiedot päivitettiin")
    return redirect("/route/" + str(route_id))


@app.route("/remove_route/<int:route_id>", methods=["GET", "POST"])
def remove_route(route_id):
    require_login()

    route = routes.get_route(route_id)
    if not route:
        abort(404)
    if route["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_route.html", route=route)

    check_csrf()
    if "remove" in request.form:
        routes.remove_route(route_id)
        flash("Reitti poistettiin")
        return redirect("/")
    return redirect("/route/" + str(route_id))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", filled={})

    username = request.form["username"].strip()
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    username_chars = username.replace("_", "")
    if not 3 <= len(username) <= 16 or not username_chars.isalnum():
        flash("VIRHE: Tunnuksessa tulee olla 3–16 kirjainta, numeroa tai alaviivaa")
        return render_template("register.html",
                               filled={"username": username})
    if not 8 <= len(password1) <= 100:
        flash("VIRHE: Salasanan tulee olla 8–100 merkkiä pitkä")
        return render_template("register.html",
                               filled={"username": username})
    if password1 != password2:
        flash("VIRHE: Salasanat eivät ole samat")
        return render_template("register.html",
                               filled={"username": username})

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("VIRHE: Tunnus on jo varattu")
        return render_template("register.html",
                               filled={"username": username})

    flash("Tunnus luotiin. Voit nyt kirjautua sisään")
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", filled={})

    username = request.form["username"].strip()
    password = request.form["password"]
    if len(username) > 16 or len(password) > 100:
        user_id = None
    else:
        user_id = users.check_login(username, password)

    if not user_id:
        flash("VIRHE: Väärä tunnus tai salasana")
        return render_template("login.html", filled={"username": username})

    session.clear()
    session["user_id"] = user_id
    session["username"] = username
    session["csrf_token"] = secrets.token_hex(16)
    flash("Kirjautuminen onnistui")
    return redirect("/")


@app.route("/logout", methods=["POST"])
def logout():
    require_login()
    check_csrf()
    session.clear()
    return redirect("/")
