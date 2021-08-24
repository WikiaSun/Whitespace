-- migrate:up
CREATE TABLE wh_guilds (
    id TEXT PRIMARY KEY,
    bound_wiki_url TEXT DEFAULT 'https://community.fandom.com/ru',
    prefix TEXT DEFAULT '!'
);

-- migrate:down
DROP TABLE wh_guilds;
