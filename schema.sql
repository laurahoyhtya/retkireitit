CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE routes (
    id INTEGER PRIMARY KEY,
    name TEXT,
    area TEXT,
    start_point TEXT,
    length_km REAL,
    description TEXT,
    user_id INTEGER REFERENCES users
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT,
    UNIQUE (title, value)
);

CREATE TABLE route_classes (
    id INTEGER PRIMARY KEY,
    route_id INTEGER REFERENCES routes,
    class_id INTEGER REFERENCES classes,
    UNIQUE (route_id, class_id)
);

CREATE TABLE trip_reports (
    id INTEGER PRIMARY KEY,
    route_id INTEGER REFERENCES routes,
    user_id INTEGER REFERENCES users,
    rating INTEGER,
    trail_condition TEXT,
    content TEXT
);
