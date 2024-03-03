CREATE TABLE IF NOT EXISTS contact (
  id serial PRIMARY KEY,
  phone_number text,
  email text,
  linked_id integer,
  link_precedence text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT (NOW () AT TIME ZONE 'UTC'),
  updated_at timestamptz NOT NULL DEFAULT (NOW () AT TIME ZONE 'UTC'),
  deleted_at timestamptz
);
