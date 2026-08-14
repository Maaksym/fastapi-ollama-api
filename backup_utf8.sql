--
-- PostgreSQL database dump
--

\restrict g31GI4XHA2mUS0W3HP8jRYkds3U7ELU9iNgeJy0kBUeH0HeDYCUzZ0PP7vsHDuI

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg13+1)
-- Dumped by pg_dump version 16.14 (Debian 16.14-1.pgdg13+1)

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
-- Name: ai_requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_requests (
    id integer NOT NULL,
    prompt character varying(1000) NOT NULL,
    answer text NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.ai_requests OWNER TO postgres;

--
-- Name: ai_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ai_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ai_requests_id_seq OWNER TO postgres;

--
-- Name: ai_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ai_requests_id_seq OWNED BY public.ai_requests.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: ai_requests id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_requests ALTER COLUMN id SET DEFAULT nextval('public.ai_requests_id_seq'::regclass);


--
-- Data for Name: ai_requests; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ai_requests (id, prompt, answer, created_at) FROM stdin;
1	Що таке FastAPI?	FastAPI - це простий і ефективний середовище для створення API-веб-серверів на Python.	2026-08-12 11:45:34.868047
2	Що таке django	Django - це фреймворк для створення web-апплікацій на Python. Він надає основи для створення корисних інфраструктури без вивчання всього з нуля.	2026-08-12 13:12:41.733486
3	ШО таке Json	Json - це формат даних для обміnu та передачі даних. Він є абстрактним языком із вбудованими типами даних, наприклад, числа, строки, списки та словники.	2026-08-12 13:57:44.891155
4	Шо таке python	Python - це програмний конвектор на складних языках, простий для навчання та використання. Він широко використовується для створення додатків, інтернет-сайтів та бібліотек.	2026-08-12 14:20:35.684705
5	Поясни FastAPI	Тестова відповідь	2026-08-12 14:22:52.892922
6	Поясни FastAPI	Тестова відповідь	2026-08-12 14:31:36.839566
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
9c5e0acfaa8b
\.


--
-- Name: ai_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ai_requests_id_seq', 6, true);


--
-- Name: ai_requests ai_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_requests
    ADD CONSTRAINT ai_requests_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- PostgreSQL database dump complete
--

\unrestrict g31GI4XHA2mUS0W3HP8jRYkds3U7ELU9iNgeJy0kBUeH0HeDYCUzZ0PP7vsHDuI

