CREATE TABLE IF NOT EXISTS USER_RATING (
    etag TEXT NOT NULL,
    username TEXT NOT NULL,
    rating INTEGER NOT NULL,
    SelectedTiles TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (etag, username)
);