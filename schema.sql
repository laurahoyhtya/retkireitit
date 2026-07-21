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

