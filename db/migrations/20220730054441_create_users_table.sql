-- migrate:up
CREATE TABLE users (
    fandom_name text,
    discord_id bigint,
    guild_id bigint,
    trusted boolean,
    active boolean
);

CREATE INDEX ON users (fandom_name, discord_id, guild_id);

-- migrate:down
DROP TABLE users;

