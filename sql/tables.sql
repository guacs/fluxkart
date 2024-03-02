CREATE TABLE IF NOT EXISTS contact (
  id integer PRIMARY KEY,
  phone_number text,
  email text,
  linked_id integer,
  link_precedence text NOT NULL,
  created_at datetime NOT NULL DEFAULT (datetime('now')),
  updated_at datetime NOT NULL DEFAULT (datetime('now')),
  deleted_at datetime
);
