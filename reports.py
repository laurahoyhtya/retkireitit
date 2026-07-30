import db


def add_report(route_id, user_id, rating, trail_condition, content):
    sql = """INSERT INTO trip_reports
             (route_id, user_id, rating, trail_condition, content)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [route_id, user_id, rating, trail_condition, content])


def get_reports(route_id):
    sql = """SELECT tr.id, tr.rating, tr.trail_condition, tr.content,
                    u.id user_id, u.username
             FROM trip_reports tr, users u
             WHERE tr.route_id = ? AND tr.user_id = u.id
             ORDER BY tr.id DESC"""
    return db.query(sql, [route_id])


def get_report(report_id):
    sql = """SELECT tr.id, tr.route_id, tr.user_id,
                    tr.rating, tr.trail_condition, tr.content,
                    r.name route_name
             FROM trip_reports tr, routes r
             WHERE tr.route_id = r.id AND tr.id = ?"""
    result = db.query(sql, [report_id])
    return result[0] if result else None


def remove_report(report_id):
    sql = "DELETE FROM trip_reports WHERE id = ?"
    db.execute(sql, [report_id])
