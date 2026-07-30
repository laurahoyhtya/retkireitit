import re
import secrets
import sqlite3

from flask import Flask
from flask import abort, flash, redirect, render_template, request, session
import markupsafe

import config
import reports
import routes
import users


app = Flask(__name__)
app.secret_key = config.SECRET_KEY

REPORT_CONDITIONS = ("Hyvä", "Tyydyttävä", "Huono")


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


def get_selected_class_ids():
    return [int(entry) for entry in request.form.getlist("classes")
            if entry.isdigit()]


def get_route_form_data(all_classes):
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

    selected_classes = request.form.getlist("classes")
    class_ids = None
    if not error_message and len(selected_classes) != len(all_classes):
        error_message = "Valitse yksi vaihtoehto jokaisesta luokittelusta"
    elif not error_message:
        valid_classes = {}
        for class_title, options in all_classes.items():
            for option in options:
                valid_classes[str(option["id"])] = class_title

        if any(entry not in valid_classes for entry in selected_classes):
            abort(403)

        selected_titles = [valid_classes[entry]
                           for entry in selected_classes]
        if (len(set(selected_classes)) != len(selected_classes) or
                len(set(selected_titles)) != len(selected_titles)):
            abort(403)
        class_ids = [int(entry) for entry in selected_classes]

    if error_message:
        flash("VIRHE: " + error_message)
        return None

    data = {
        "name": name,
        "area": area,
        "start_point": start_point,
        "length_km": length_km,
        "description": description
    }
    return data, class_ids


def render_route_page(route, filled_report=None):
    route_classes = routes.get_classes(route["id"])
    route_reports = reports.get_reports(route["id"])
    return render_template("show_route.html", route=route,
                           classes=route_classes,
                           reports=route_reports,
                           conditions=REPORT_CONDITIONS,
                           filled_report=filled_report or {})


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


@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    user_routes = users.get_routes(user_id)
    user_reports = users.get_reports(user_id)
    return render_template("show_user.html", user=user,
                           routes=user_routes, reports=user_reports)


@app.route("/route/<int:route_id>")
def show_route(route_id):
    route = routes.get_route(route_id)
    if not route:
        abort(404)
    return render_route_page(route)


@app.route("/new_route")
def new_route():
    require_login()
    all_classes = routes.get_all_classes()
    return render_template("new_route.html", filled={},
                           classes=all_classes, selected_class_ids=[])


@app.route("/create_route", methods=["POST"])
def create_route():
    require_login()
    check_csrf()

    all_classes = routes.get_all_classes()
    form_data = get_route_form_data(all_classes)
    if not form_data:
        return render_template(
            "new_route.html",
            filled=request.form,
            classes=all_classes,
            selected_class_ids=get_selected_class_ids()
        )

    data, class_ids = form_data
    route_id = routes.add_route(data, session["user_id"], class_ids)
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

    all_classes = routes.get_all_classes()
    selected_class_ids = routes.get_class_ids(route_id)
    return render_template("edit_route.html", route_id=route_id,
                           filled=route, classes=all_classes,
                           selected_class_ids=selected_class_ids)


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

    all_classes = routes.get_all_classes()
    form_data = get_route_form_data(all_classes)
    if not form_data:
        return render_template(
            "edit_route.html",
            route_id=route_id,
            filled=request.form,
            classes=all_classes,
            selected_class_ids=get_selected_class_ids()
        )

    data, class_ids = form_data
    routes.update_route(route_id, data, class_ids)
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


@app.route("/create_report", methods=["POST"])
def create_report():
    require_login()
    check_csrf()

    route_id = request.form.get("route_id")
    route = routes.get_route(route_id)
    if not route:
        abort(404)

    rating_text = request.form["rating"]
    trail_condition = request.form["trail_condition"]
    content = request.form["content"].strip()

    error_message = None
    if not re.fullmatch(r"[1-5]", rating_text):
        error_message = "Anna arvosana väliltä 1–5"
    elif trail_condition not in REPORT_CONDITIONS:
        error_message = "Valitse reitin kunto annetuista vaihtoehdoista"
    elif not content or len(content) > 2000:
        error_message = "Raportin tulee olla 1–2000 merkkiä pitkä"

    if error_message:
        flash("VIRHE: " + error_message)
        return render_route_page(route, request.form)

    reports.add_report(route_id, session["user_id"], int(rating_text),
                       trail_condition, content)
    flash("Retkiraportti lisättiin")
    return redirect("/route/" + str(route_id) + "#reports")


@app.route("/remove_report/<int:report_id>", methods=["GET", "POST"])
def remove_report(report_id):
    require_login()

    report = reports.get_report(report_id)
    if not report:
        abort(404)
    if report["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_report.html", report=report)

    check_csrf()
    if "remove" in request.form:
        reports.remove_report(report_id)
        flash("Retkiraportti poistettiin")
    return redirect("/route/" + str(report["route_id"]) + "#reports")


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
