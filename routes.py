import db


def get_routes():
    sql = """SELECT r.id, r.name, r.area, r.length_km,
                    u.id user_id, u.username
             FROM routes r, users u
             WHERE r.user_id = u.id
             ORDER BY r.id DESC"""
    return db.query(sql)


def get_route(route_id):
    sql = """SELECT r.id, r.name, r.area, r.start_point,
                    r.length_km, r.description,
                    u.id user_id, u.username
             FROM routes r, users u
             WHERE r.user_id = u.id AND r.id = ?"""
    result = db.query(sql, [route_id])
    return result[0] if result else None


def add_route(data, user_id):
    sql = """INSERT INTO routes
             (name, area, start_point, length_km, description, user_id)
             VALUES (?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [data["name"], data["area"], data["start_point"],
                     data["length_km"], data["description"], user_id])
    return db.last_insert_id()


def update_route(route_id, data):
    sql = """UPDATE routes SET name = ?,
                                area = ?,
                                start_point = ?,
                                length_km = ?,
                                description = ?
                            WHERE id = ?"""
    db.execute(sql, [data["name"], data["area"], data["start_point"],
                     data["length_km"], data["description"], route_id])


def remove_route(route_id):
    sql = "DELETE FROM routes WHERE id = ?"
    db.execute(sql, [route_id])


def find_routes(query):
    sql = """SELECT r.id, r.name, r.area, r.length_km,
                    u.id user_id, u.username
             FROM routes r, users u
             WHERE r.user_id = u.id AND
                   (r.name LIKE ? OR r.area LIKE ?)
             ORDER BY r.id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])
