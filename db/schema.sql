SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying(255) NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    fandom_name text,
    discord_id bigint,
    guild_id bigint,
    trusted boolean,
    active boolean
);


--
-- Name: wh_guilds; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wh_guilds (
    id bigint NOT NULL,
    bound_wiki_url text DEFAULT 'https://community.fandom.com/ru'::text,
    prefix text DEFAULT '!'::text,
    bound_wiki_name text,
    flags bigint DEFAULT 0
);


--
-- Name: wh_wikilink_webhooks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wh_wikilink_webhooks (
    channel_id bigint NOT NULL,
    webhook_url text
);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: wh_guilds wh_guilds_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wh_guilds
    ADD CONSTRAINT wh_guilds_pkey PRIMARY KEY (id);


--
-- Name: wh_wikilink_webhooks wh_wikilink_webhooks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wh_wikilink_webhooks
    ADD CONSTRAINT wh_wikilink_webhooks_pkey PRIMARY KEY (channel_id);


--
-- Name: users_fandom_name_discord_id_guild_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_fandom_name_discord_id_guild_id_idx ON public.users USING btree (fandom_name, discord_id, guild_id);


--
-- PostgreSQL database dump complete
--


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('20210519201710'),
    ('20211006194734'),
    ('20211222113737'),
    ('20211226164418'),
    ('20220730054441'),
    ('20221023182737');
