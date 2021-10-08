-- migrate:up
ALTER TABLE wh_guilds
ALTER COLUMN id TYPE BIGINT
USING id::bigint;

-- migrate:down
ALTER TABLE wh_guilds
ALTER COLUMN id TYPE TEXT NOT NULL;
