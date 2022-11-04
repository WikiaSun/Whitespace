-- migrate:up
ALTER TABLE wh_guilds
ADD COLUMN flags bigint DEFAULT 0;

-- migrate:down
ALTER TABLE wh_guilds
DROP COLUMN flags;
