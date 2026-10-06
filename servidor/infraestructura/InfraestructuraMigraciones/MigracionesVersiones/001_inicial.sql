CREATE TABLE IF NOT EXISTS usuarios (
    email TEXT PRIMARY KEY,
    nick TEXT NOT NULL,
    contrasena_hash TEXT NOT NULL,
    rol TEXT NOT NULL,
    estado TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sesiones (
    token TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    expira_en TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS sesiones_email ON sesiones (email);

CREATE TABLE IF NOT EXISTS recuperaciones (
    token TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    expira_en TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS recuperaciones_email ON recuperaciones (email);
