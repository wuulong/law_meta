--
-- PostgreSQL database dump
-- lawdb v0.2 , db: lawdb, user:lawdb with permission grant, dump by system

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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: lawdb
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO lawdb;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: article_legal_concept; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.article_legal_concept (
    article_id integer NOT NULL,
    legal_concept_id integer NOT NULL
);


ALTER TABLE public.article_legal_concept OWNER TO root;

--
-- Name: TABLE article_legal_concept; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON TABLE public.article_legal_concept IS '連接法條與法律概念的資料表，記錄法條使用了哪些法律概念 (多對多)';


--
-- Name: COLUMN article_legal_concept.article_id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.article_legal_concept.article_id IS '指向法條的外部鍵';


--
-- Name: COLUMN article_legal_concept.legal_concept_id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.article_legal_concept.legal_concept_id IS '指向法律概念的外部鍵';


--
-- Name: articles; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.articles (
    id integer NOT NULL,
    law_id integer NOT NULL,
    xml_chapter_section character varying(255),
    xml_article_number character varying(50) NOT NULL,
    xml_article_content text,
    article_metadata jsonb
);


ALTER TABLE public.articles OWNER TO root;

--
-- Name: TABLE articles; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON TABLE public.articles IS '儲存法條核心資訊(來自XML)以及豐富的JSON元數據 (Article Meta Data)';


--
-- Name: COLUMN articles.id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.articles.id IS '自動生成的唯一識別碼';


--
-- Name: COLUMN articles.law_id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.articles.law_id IS '指向所屬法規的外部鍵';


--
-- Name: COLUMN articles.xml_chapter_section; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.articles.xml_chapter_section IS 'XML來源: 編章節';


--
-- Name: COLUMN articles.xml_article_number; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.articles.xml_article_number IS 'XML來源: 條號';


--
-- Name: COLUMN articles.xml_article_content; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.articles.xml_article_content IS 'XML來源: 條文內容';


--
-- Name: COLUMN articles.article_metadata; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.articles.article_metadata IS '儲存完整的法條元數據JSON內容 (依法律語法形式化.md)';


--
-- Name: articles_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.articles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.articles_id_seq OWNER TO root;

--
-- Name: articles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.articles_id_seq OWNED BY public.articles.id;


--
-- Name: law_hierarchy_relationships; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.law_hierarchy_relationships (
    id integer NOT NULL,
    relationship_code character varying(255) NOT NULL,
    main_law_id integer NOT NULL,
    main_law_name character varying(255),
    related_law_id integer NOT NULL,
    related_law_name character varying(255),
    hierarchy_type character varying(100) NOT NULL,
    data jsonb
);


ALTER TABLE public.law_hierarchy_relationships OWNER TO root;

--
-- Name: TABLE law_hierarchy_relationships; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON TABLE public.law_hierarchy_relationships IS '描述法規之間的階層關係 (Law Hierarchy Relationship Meta Data)';


--
-- Name: COLUMN law_hierarchy_relationships.id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.law_hierarchy_relationships.id IS '自動生成的唯一識別碼';


--
-- Name: COLUMN law_hierarchy_relationships.relationship_code; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.law_hierarchy_relationships.relationship_code IS '關係代號，唯一識別';


--
-- Name: COLUMN law_hierarchy_relationships.main_law_id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.law_hierarchy_relationships.main_law_id IS '主要法規的外部鍵';


--
-- Name: COLUMN law_hierarchy_relationships.related_law_id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.law_hierarchy_relationships.related_law_id IS '關聯法規的外部鍵';


--
-- Name: COLUMN law_hierarchy_relationships.hierarchy_type; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.law_hierarchy_relationships.hierarchy_type IS '階層關係類型';


--
-- Name: COLUMN law_hierarchy_relationships.data; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.law_hierarchy_relationships.data IS '儲存完整的法規階層關係 Meta Data JSON 內容';


--
-- Name: law_hierarchy_relationships_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.law_hierarchy_relationships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.law_hierarchy_relationships_id_seq OWNER TO root;

--
-- Name: law_hierarchy_relationships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.law_hierarchy_relationships_id_seq OWNED BY public.law_hierarchy_relationships.id;


--
-- Name: law_relationships; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.law_relationships (
    id integer NOT NULL,
    code character varying(255) NOT NULL,
    relationship_type character varying(100) NOT NULL,
    main_law_id integer,
    main_law_name character varying(255),
    main_article_id integer,
    related_law_id integer,
    related_law_name character varying(255),
    related_article_id integer,
    data jsonb
);


ALTER TABLE public.law_relationships OWNER TO root;

--
-- Name: TABLE law_relationships; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON TABLE public.law_relationships IS '描述不同法規之間、法條與法規之間、法條與法條(跨法規)等的外部關聯性 (Law Relationship Meta Data)';


--
-- Name: COLUMN law_relationships.id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.law_relationships.id IS '自動生成的唯一識別碼';


--
-- Name: COLUMN law_relationships.code; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.law_relationships.code IS '關係代號，唯一識別';


--
-- Name: COLUMN law_relationships.relationship_type; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.law_relationships.relationship_type IS '關聯類型';


--
-- Name: COLUMN law_relationships.main_law_id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.law_relationships.main_law_id IS '主要法規的外部鍵 (若關聯涉及法規)';


--
-- Name: COLUMN law_relationships.main_article_id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.law_relationships.main_article_id IS '主要法條的外部鍵 (若關聯涉及法條)';


--
-- Name: COLUMN law_relationships.related_law_id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.law_relationships.related_law_id IS '關聯法規的外部鍵 (若關聯涉及法規)';


--
-- Name: COLUMN law_relationships.related_article_id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.law_relationships.related_article_id IS '關聯法條的外部鍵 (若關聯涉及法條)';


--
-- Name: COLUMN law_relationships.data; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.law_relationships.data IS '儲存完整的法規關聯性 Meta Data JSON 內容';


--
-- Name: law_relationships_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.law_relationships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.law_relationships_id_seq OWNER TO root;

--
-- Name: law_relationships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.law_relationships_id_seq OWNED BY public.law_relationships.id;


--
-- Name: laws; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.laws (
    id integer NOT NULL,
    pcode character varying(50) NOT NULL,
    xml_law_nature character varying(100),
    xml_law_name character varying(255) NOT NULL,
    xml_law_url character varying(512),
    xml_law_category character varying(255),
    xml_latest_change_date date,
    xml_effective_date text,
    xml_effective_content text,
    xml_abolition_mark text,
    xml_is_english_translated boolean,
    xml_english_law_name character varying(512),
    xml_attachment text,
    xml_history_content text,
    xml_preamble text,
    llm_summary text,
    llm_keywords text,
    is_active boolean DEFAULT true,
    law_metadata jsonb
);


ALTER TABLE public.laws OWNER TO root;

--
-- Name: TABLE laws; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON TABLE public.laws IS '儲存法規核心資訊(來自XML)、LLM生成資料以及豐富的JSON元數據 (Law Meta Data)';


--
-- Name: COLUMN laws.id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.id IS '自動生成的唯一識別碼';


--
-- Name: COLUMN laws.pcode; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.pcode IS '法規PCode (來自法規網址中的pcode)，作為主要唯一識別碼';


--
-- Name: COLUMN laws.xml_law_nature; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.xml_law_nature IS 'XML來源: 法規性質';


--
-- Name: COLUMN laws.xml_law_name; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.xml_law_name IS 'XML來源: 法規名稱';


--
-- Name: COLUMN laws.xml_law_url; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.xml_law_url IS 'XML來源: 法規網址';


--
-- Name: COLUMN laws.xml_law_category; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.xml_law_category IS 'XML來源: 法規類別';


--
-- Name: COLUMN laws.xml_latest_change_date; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.xml_latest_change_date IS 'XML來源: 最新異動日期';


--
-- Name: COLUMN laws.xml_effective_date; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.xml_effective_date IS 'XML來源: 生效日期';


--
-- Name: COLUMN laws.xml_effective_content; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.xml_effective_content IS 'XML來源: 生效內容';


--
-- Name: COLUMN laws.xml_abolition_mark; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.xml_abolition_mark IS 'XML來源: 廢止註記';


--
-- Name: COLUMN laws.xml_is_english_translated; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.xml_is_english_translated IS 'XML來源: 是否英譯註記';


--
-- Name: COLUMN laws.xml_english_law_name; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.xml_english_law_name IS 'XML來源: 英文法規名稱';


--
-- Name: COLUMN laws.xml_attachment; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.xml_attachment IS 'XML來源: 附件';


--
-- Name: COLUMN laws.xml_history_content; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.xml_history_content IS 'XML來源: 沿革內容';


--
-- Name: COLUMN laws.xml_preamble; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.xml_preamble IS 'XML來源: 前言';


--
-- Name: COLUMN laws.llm_summary; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.llm_summary IS 'LLM生成的法規摘要';


--
-- Name: COLUMN laws.llm_keywords; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.llm_keywords IS 'LLM生成的關鍵字 (合併為單一字串)';


--
-- Name: COLUMN laws.law_metadata; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.laws.law_metadata IS '儲存完整的法規元數據JSON內容 (依法律語法形式化.md)';


--
-- Name: laws_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.laws_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.laws_id_seq OWNER TO root;

--
-- Name: laws_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.laws_id_seq OWNED BY public.laws.id;


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
-- Name: COLUMN legal_concepts.law_id; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.legal_concepts.law_id IS '指向所屬法規的外部鍵';


--
-- Name: COLUMN legal_concepts.code; Type: COMMENT; Schema: public; Owner: root
--

COMMENT ON COLUMN public.legal_concepts.code IS '法律概念代號，在同一法規內唯一';


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
-- Name: articles id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.articles ALTER COLUMN id SET DEFAULT nextval('public.articles_id_seq'::regclass);


--
-- Name: law_hierarchy_relationships id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.law_hierarchy_relationships ALTER COLUMN id SET DEFAULT nextval('public.law_hierarchy_relationships_id_seq'::regclass);


--
-- Name: law_relationships id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.law_relationships ALTER COLUMN id SET DEFAULT nextval('public.law_relationships_id_seq'::regclass);


--
-- Name: laws id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.laws ALTER COLUMN id SET DEFAULT nextval('public.laws_id_seq'::regclass);


--
-- Name: legal_concepts id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.legal_concepts ALTER COLUMN id SET DEFAULT nextval('public.legal_concepts_id_seq'::regclass);


--
-- Name: article_legal_concept article_legal_concept_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.article_legal_concept
    ADD CONSTRAINT article_legal_concept_pkey PRIMARY KEY (article_id, legal_concept_id);


--
-- Name: articles articles_law_id_xml_article_number_key; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_law_id_xml_article_number_key UNIQUE (law_id, xml_article_number);


--
-- Name: articles articles_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_pkey PRIMARY KEY (id);


--
-- Name: law_hierarchy_relationships law_hierarchy_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.law_hierarchy_relationships
    ADD CONSTRAINT law_hierarchy_relationships_pkey PRIMARY KEY (id);


--
-- Name: law_hierarchy_relationships law_hierarchy_relationships_relationship_code_key; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.law_hierarchy_relationships
    ADD CONSTRAINT law_hierarchy_relationships_relationship_code_key UNIQUE (relationship_code);


--
-- Name: law_relationships law_relationships_code_key; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.law_relationships
    ADD CONSTRAINT law_relationships_code_key UNIQUE (code);


--
-- Name: law_relationships law_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.law_relationships
    ADD CONSTRAINT law_relationships_pkey PRIMARY KEY (id);


--
-- Name: laws laws_pcode_key; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.laws
    ADD CONSTRAINT laws_pcode_key UNIQUE (pcode);


--
-- Name: laws laws_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.laws
    ADD CONSTRAINT laws_pkey PRIMARY KEY (id);


--
-- Name: legal_concepts legal_concepts_law_id_code_key; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.legal_concepts
    ADD CONSTRAINT legal_concepts_law_id_code_key UNIQUE (law_id, code);


--
-- Name: legal_concepts legal_concepts_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.legal_concepts
    ADD CONSTRAINT legal_concepts_pkey PRIMARY KEY (id);


--
-- Name: idx_alc_article_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_alc_article_id ON public.article_legal_concept USING btree (article_id);


--
-- Name: idx_alc_legal_concept_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_alc_legal_concept_id ON public.article_legal_concept USING btree (legal_concept_id);


--
-- Name: idx_articles_article_metadata_gin; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_articles_article_metadata_gin ON public.articles USING gin (article_metadata);


--
-- Name: idx_articles_law_id_article_number; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_articles_law_id_article_number ON public.articles USING btree (law_id, xml_article_number);


--
-- Name: idx_law_hierarchy_data_gin; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_law_hierarchy_data_gin ON public.law_hierarchy_relationships USING gin (data);


--
-- Name: idx_law_hierarchy_main_law_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_law_hierarchy_main_law_id ON public.law_hierarchy_relationships USING btree (main_law_id);


--
-- Name: idx_law_hierarchy_related_law_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_law_hierarchy_related_law_id ON public.law_hierarchy_relationships USING btree (related_law_id);


--
-- Name: idx_law_hierarchy_type; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_law_hierarchy_type ON public.law_hierarchy_relationships USING btree (hierarchy_type);


--
-- Name: idx_law_relationships_data_gin; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_law_relationships_data_gin ON public.law_relationships USING gin (data);


--
-- Name: idx_law_relationships_main_article; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_law_relationships_main_article ON public.law_relationships USING btree (main_article_id);


--
-- Name: idx_law_relationships_main_law; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_law_relationships_main_law ON public.law_relationships USING btree (main_law_id);


--
-- Name: idx_law_relationships_related_article; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_law_relationships_related_article ON public.law_relationships USING btree (related_article_id);


--
-- Name: idx_law_relationships_related_law; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_law_relationships_related_law ON public.law_relationships USING btree (related_law_id);


--
-- Name: idx_law_relationships_type; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_law_relationships_type ON public.law_relationships USING btree (relationship_type);


--
-- Name: idx_laws_law_metadata_gin; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_laws_law_metadata_gin ON public.laws USING gin (law_metadata);


--
-- Name: idx_laws_llm_keywords_fts; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_laws_llm_keywords_fts ON public.laws USING gin (to_tsvector('simple'::regconfig, llm_keywords));


--
-- Name: idx_laws_pcode; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_laws_pcode ON public.laws USING btree (pcode);


--
-- Name: idx_laws_xml_law_category; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_laws_xml_law_category ON public.laws USING btree (xml_law_category);


--
-- Name: idx_laws_xml_law_name; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX idx_laws_xml_law_name ON public.laws USING btree (xml_law_name);


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
-- Name: article_legal_concept article_legal_concept_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.article_legal_concept
    ADD CONSTRAINT article_legal_concept_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.articles(id) ON DELETE CASCADE;


--
-- Name: article_legal_concept article_legal_concept_legal_concept_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.article_legal_concept
    ADD CONSTRAINT article_legal_concept_legal_concept_id_fkey FOREIGN KEY (legal_concept_id) REFERENCES public.legal_concepts(id) ON DELETE CASCADE;


--
-- Name: articles articles_law_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_law_id_fkey FOREIGN KEY (law_id) REFERENCES public.laws(id) ON DELETE CASCADE;


--
-- Name: law_hierarchy_relationships law_hierarchy_relationships_main_law_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.law_hierarchy_relationships
    ADD CONSTRAINT law_hierarchy_relationships_main_law_id_fkey FOREIGN KEY (main_law_id) REFERENCES public.laws(id) ON DELETE CASCADE;


--
-- Name: law_hierarchy_relationships law_hierarchy_relationships_related_law_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.law_hierarchy_relationships
    ADD CONSTRAINT law_hierarchy_relationships_related_law_id_fkey FOREIGN KEY (related_law_id) REFERENCES public.laws(id) ON DELETE CASCADE;


--
-- Name: law_relationships law_relationships_main_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.law_relationships
    ADD CONSTRAINT law_relationships_main_article_id_fkey FOREIGN KEY (main_article_id) REFERENCES public.articles(id) ON DELETE CASCADE;


--
-- Name: law_relationships law_relationships_main_law_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.law_relationships
    ADD CONSTRAINT law_relationships_main_law_id_fkey FOREIGN KEY (main_law_id) REFERENCES public.laws(id) ON DELETE CASCADE;


--
-- Name: law_relationships law_relationships_related_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.law_relationships
    ADD CONSTRAINT law_relationships_related_article_id_fkey FOREIGN KEY (related_article_id) REFERENCES public.articles(id) ON DELETE CASCADE;


--
-- Name: law_relationships law_relationships_related_law_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.law_relationships
    ADD CONSTRAINT law_relationships_related_law_id_fkey FOREIGN KEY (related_law_id) REFERENCES public.laws(id) ON DELETE CASCADE;


--
-- Name: legal_concepts legal_concepts_law_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.legal_concepts
    ADD CONSTRAINT legal_concepts_law_id_fkey FOREIGN KEY (law_id) REFERENCES public.laws(id) ON DELETE CASCADE;


--
-- Name: TABLE article_legal_concept; Type: ACL; Schema: public; Owner: root
--

GRANT ALL ON TABLE public.article_legal_concept TO lawdb;


--
-- Name: TABLE articles; Type: ACL; Schema: public; Owner: root
--

GRANT ALL ON TABLE public.articles TO lawdb;


--
-- Name: SEQUENCE articles_id_seq; Type: ACL; Schema: public; Owner: root
--

GRANT ALL ON SEQUENCE public.articles_id_seq TO lawdb;


--
-- Name: TABLE law_hierarchy_relationships; Type: ACL; Schema: public; Owner: root
--

GRANT ALL ON TABLE public.law_hierarchy_relationships TO lawdb;


--
-- Name: SEQUENCE law_hierarchy_relationships_id_seq; Type: ACL; Schema: public; Owner: root
--

GRANT ALL ON SEQUENCE public.law_hierarchy_relationships_id_seq TO lawdb;


--
-- Name: TABLE law_relationships; Type: ACL; Schema: public; Owner: root
--

GRANT ALL ON TABLE public.law_relationships TO lawdb;


--
-- Name: SEQUENCE law_relationships_id_seq; Type: ACL; Schema: public; Owner: root
--

GRANT ALL ON SEQUENCE public.law_relationships_id_seq TO lawdb;


--
-- Name: TABLE laws; Type: ACL; Schema: public; Owner: root
--

GRANT ALL ON TABLE public.laws TO lawdb;


--
-- Name: SEQUENCE laws_id_seq; Type: ACL; Schema: public; Owner: root
--

GRANT ALL ON SEQUENCE public.laws_id_seq TO lawdb;


--
-- Name: TABLE legal_concepts; Type: ACL; Schema: public; Owner: root
--

GRANT ALL ON TABLE public.legal_concepts TO lawdb;


--
-- Name: SEQUENCE legal_concepts_id_seq; Type: ACL; Schema: public; Owner: root
--

GRANT ALL ON SEQUENCE public.legal_concepts_id_seq TO lawdb;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: root
--

ALTER DEFAULT PRIVILEGES FOR ROLE root IN SCHEMA public GRANT ALL ON SEQUENCES TO lawdb;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: lawdb
--

ALTER DEFAULT PRIVILEGES FOR ROLE lawdb IN SCHEMA public GRANT ALL ON SEQUENCES TO lawdb;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: root
--

ALTER DEFAULT PRIVILEGES FOR ROLE root IN SCHEMA public GRANT ALL ON TABLES TO lawdb;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: lawdb
--

ALTER DEFAULT PRIVILEGES FOR ROLE lawdb IN SCHEMA public GRANT ALL ON TABLES TO lawdb;


--
-- PostgreSQL database dump complete
--

