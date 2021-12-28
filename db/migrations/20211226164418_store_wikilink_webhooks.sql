-- migrate:up
CREATE TABLE wh_wikilink_webhooks (
    channel_id bigint PRIMARY KEY,
    webhook_url text
);

-- migrate:down
DROP TABLE wh_wikilink_webhooks;
