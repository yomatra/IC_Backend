kCREATE TABLE IF NOT EXISTS incidents (

    id TEXT PRIMARY KEY,

    name TEXT NOT NULL,

    description TEXT NOT NULL,

    category TEXT NOT NULL,

    severity TEXT NOT NULL,

    status TEXT NOT NULL,

    location TEXT,

    latitude DOUBLE PRECISION,

    longitude DOUBLE PRECISION,

    department TEXT,

    created_at TIMESTAMPTZ NOT NULL,

    updated_at TIMESTAMPTZ,

    raw_json JSONB NOT NULL
);
