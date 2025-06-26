--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5 (Debian 17.5-1.pgdg120+1)
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

DROP TABLE public.legal_concepts CASCADE;

--
-- Name: legal_concepts; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.legal_concepts (
    id integer NOT NULL,
    law_id integer NOT NULL,
    code character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    data jsonb
);


ALTER TABLE public.legal_concepts OWNER TO root;

--
-- Name: TABLE legal_concepts; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON TABLE public.legal_concepts IS '儲存法律概念詞彙庫 (Legal Concept Meta Data)';


--
-- Name: COLUMN legal_concepts.id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.legal_concepts.id IS '自動生成的唯一識別碼';


--
-- Name: COLUMN legal_concepts.code; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.legal_concepts.code IS '法律概念代號，唯一識別';


--
-- Name: COLUMN legal_concepts.name; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.legal_concepts.name IS '詞彙名稱';


--
-- Name: COLUMN legal_concepts.data; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.legal_concepts.data IS '儲存完整的法律概念 Meta Data JSON 內容';


--
-- Name: legal_concepts_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.legal_concepts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.legal_concepts_id_seq OWNER TO root;

--
-- Name: legal_concepts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.legal_concepts_id_seq OWNED BY public.legal_concepts.id;


--
-- Name: legal_concepts id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.legal_concepts ALTER COLUMN id SET DEFAULT nextval('public.legal_concepts_id_seq'::regclass);


--
-- Name: legal_concepts legal_concepts_code_key; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.legal_concepts
    ADD CONSTRAINT legal_concepts_code_key UNIQUE (code);


--
-- Name: legal_concepts legal_concepts_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.legal_concepts
    ADD CONSTRAINT legal_concepts_pkey PRIMARY KEY (id);


--
-- Name: legal_concepts legal_concepts_unique; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.legal_concepts
    ADD CONSTRAINT legal_concepts_unique UNIQUE (law_id, code);


--
-- Name: idx_legal_concepts_code; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_legal_concepts_code ON public.legal_concepts USING btree (code);


--
-- Name: idx_legal_concepts_data_gin; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_legal_concepts_data_gin ON public.legal_concepts USING gin (data);


--
-- Name: idx_legal_concepts_law_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_legal_concepts_law_id ON public.legal_concepts USING btree (law_id);


--
-- Name: idx_legal_concepts_name; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_legal_concepts_name ON public.legal_concepts USING btree (name);


--
-- Name: legal_concepts legal_concepts_law_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.legal_concepts
    ADD CONSTRAINT legal_concepts_law_id_fkey FOREIGN KEY (law_id) REFERENCES public.laws(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

