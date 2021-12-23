-- migrate:up
ALTER TABLE wh_guilds
ADD COLUMN bound_wiki_name text;

-- migrate:down
ALTER TABLE wh_guilds
DROP COLUMN bound_wiki_name;
