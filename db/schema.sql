CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(80) NOT NULL UNIQUE,
  age INTEGER,
  created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE songs (
  song_id VARCHAR(64) PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  artist VARCHAR(255) NOT NULL,
  genre VARCHAR(80) NOT NULL,
  danceability REAL NOT NULL,
  energy REAL NOT NULL,
  tempo REAL NOT NULL,
  popularity REAL NOT NULL,
  acousticness REAL NOT NULL
);

CREATE TABLE user_interactions (
  interaction_id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(user_id),
  song_id VARCHAR(64) NOT NULL,
  action VARCHAR(16) NOT NULL CHECK (action IN ('like', 'dislike')),
  play_count INTEGER NOT NULL DEFAULT 0,
  liked BOOLEAN NOT NULL DEFAULT FALSE,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recommendation_history (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(user_id),
  song_id VARCHAR(64) NOT NULL,
  recommendation_score REAL NOT NULL,
  created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interactions_user ON user_interactions(user_id);
CREATE INDEX idx_history_user ON recommendation_history(user_id);
