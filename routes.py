import db


def get_all_classes():
    sql = "SELECT id, title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for entry in result:
        if entry["title"] not in classes:
            classes[entry["title"]] = []
        classes[entry["title"]].append(entry)
    return classes


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
                    u.id user_id, u.username,
                    COUNT(tr.id) report_count,
                    ROUND(AVG(tr.rating), 1) average_rating
             FROM routes r JOIN users u ON r.user_id = u.id
                           LEFT JOIN trip_reports tr ON r.id = tr.route_id
             WHERE r.id = ?
             GROUP BY r.id"""
    result = db.query(sql, [route_id])
    return result[0] if result else None


def get_classes(route_id):
    sql = """SELECT c.id, c.title, c.value
             FROM classes c, route_classes rc
             WHERE c.id = rc.class_id AND rc.route_id = ?
             ORDER BY c.id"""
    return db.query(sql, [route_id])


def get_class_ids(route_id):
    sql = "SELECT class_id FROM route_classes WHERE route_id = ?"
    result = db.query(sql, [route_id])
    return [entry["class_id"] for entry in result]


def add_route(data, user_id, class_ids):
    sql = """INSERT INTO routes
             (name, area, start_point, length_km, description, user_id)
             VALUES (?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [data["name"], data["area"], data["start_point"],
                     data["length_km"], data["description"], user_id])
    route_id = db.last_insert_id()

    sql = """INSERT INTO route_classes (route_id, class_id)
             VALUES (?, ?)"""
    for class_id in class_ids:
        db.execute(sql, [route_id, class_id])
    return route_id


def update_route(route_id, data, class_ids):
    sql = """UPDATE routes SET name = ?,
                                area = ?,
                                start_point = ?,
                                length_km = ?,
                                description = ?
                            WHERE id = ?"""
    db.execute(sql, [data["name"], data["area"], data["start_point"],
                     data["length_km"], data["description"], route_id])

    sql = "DELETE FROM route_classes WHERE route_id = ?"
    db.execute(sql, [route_id])

    sql = """INSERT INTO route_classes (route_id, class_id)
             VALUES (?, ?)"""
    for class_id in class_ids:
        db.execute(sql, [route_id, class_id])


def remove_route(route_id):
    sql = "DELETE FROM trip_reports WHERE route_id = ?"
    db.execute(sql, [route_id])
    sql = "DELETE FROM route_classes WHERE route_id = ?"
    db.execute(sql, [route_id])
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
