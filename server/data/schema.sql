CREATE TABLE projects (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL UNIQUE,
    code         TEXT,
    dir          TEXT NOT NULL
);

CREATE TABLE episodes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name       TEXT,
    code       TEXT NOT NULL,
    dir        TEXT NOT NULL,
    UNIQUE (project_id, code)
);

CREATE TABLE sequences (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_id INTEGER REFERENCES episodes(id) ON DELETE SET NULL,
    name       TEXT,
    code       TEXT NOT NULL,
    dir        TEXT NOT NULL,
    UNIQUE (project_id, code)
);

CREATE TABLE shots (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id   INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_id   INTEGER NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    sequence_id  INTEGER NOT NULL REFERENCES sequences(id) ON DELETE CASCADE,
    name         TEXT,
    code         TEXT NOT NULL,
    frame_start  INTEGER,
    frame_end    INTEGER,
    dir          TEXT NOT NULL,
    UNIQUE (sequence_id, code)
);

CREATE TABLE assets (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id   INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name         TEXT NOT NULL,
    asset_type   TEXT
);