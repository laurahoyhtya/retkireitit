from werkzeug.security import check_password_hash, generate_password_hash

import db


def get_user(user_id):
    sql = """SELECT u.id, u.username,
                    (SELECT COUNT(*)
                     FROM routes r
                     WHERE r.user_id = u.id) route_count,
                    (SELECT COUNT(*)
                     FROM trip_reports tr
                     WHERE tr.user_id = u.id) report_count
             FROM users u
             WHERE u.id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None


def get_routes(user_id):
    sql = """SELECT id, name, area, length_km
             FROM routes
             WHERE user_id = ?
             ORDER BY id DESC"""
    return db.query(sql, [user_id])


def get_reports(user_id):
    sql = """SELECT tr.id, tr.rating, tr.trail_condition,
                    tr.content, r.id route_id, r.name route_name
             FROM trip_reports tr, routes r
             WHERE tr.route_id = r.id AND tr.user_id = ?
             ORDER BY tr.id DESC"""
    return db.query(sql, [user_id])


def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])


def check_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return None

    user_id = result[0]["id"]
    password_hash = result[0]["password_hash"]
    if check_password_hash(password_hash, password):
        return user_id
    return None
