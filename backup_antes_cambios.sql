--
-- PostgreSQL database dump
--

\restrict efcPkso969qxnoWrhIOwTfY9V5J8dEew87AN20aMBFQRkhxV5Hi64oMLLi29dvH

-- Dumped from database version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)

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

--
-- Name: petcare; Type: SCHEMA; Schema: -; Owner: petuser
--

CREATE SCHEMA petcare;


ALTER SCHEMA petcare OWNER TO petuser;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: reminder_frequency; Type: TYPE; Schema: petcare; Owner: postgres
--

CREATE TYPE petcare.reminder_frequency AS ENUM (
    'once',
    'daily',
    'weekly',
    'monthly',
    'yearly'
);


ALTER TYPE petcare.reminder_frequency OWNER TO postgres;

--
-- Name: reminderfrequency; Type: TYPE; Schema: public; Owner: petuser
--

CREATE TYPE public.reminderfrequency AS ENUM (
    'once',
    'daily',
    'weekly',
    'monthly',
    'yearly'
);


ALTER TYPE public.reminderfrequency OWNER TO petuser;

--
-- Name: update_updated_at(); Type: FUNCTION; Schema: petcare; Owner: postgres
--

CREATE FUNCTION petcare.update_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;


ALTER FUNCTION petcare.update_updated_at() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_logs; Type: TABLE; Schema: petcare; Owner: postgres
--

CREATE TABLE petcare.audit_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    actor_user_id uuid,
    action text NOT NULL,
    object_type text,
    object_id uuid,
    meta jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE petcare.audit_logs OWNER TO postgres;

--
-- Name: dewormings; Type: TABLE; Schema: petcare; Owner: postgres
--

CREATE TABLE petcare.dewormings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pet_id uuid NOT NULL,
    medication text,
    date_administered date NOT NULL,
    next_due date,
    veterinarian text,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE petcare.dewormings OWNER TO postgres;

--
-- Name: meals; Type: TABLE; Schema: petcare; Owner: postgres
--

CREATE TABLE petcare.meals (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pet_id uuid NOT NULL,
    plan_id uuid,
    meal_time timestamp with time zone NOT NULL,
    description text,
    calories integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE petcare.meals OWNER TO postgres;

--
-- Name: notifications; Type: TABLE; Schema: petcare; Owner: postgres
--

CREATE TABLE petcare.notifications (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    reminder_id uuid,
    owner_id uuid,
    pet_id uuid,
    sent_at timestamp with time zone DEFAULT now() NOT NULL,
    method text,
    status text,
    provider_response jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE petcare.notifications OWNER TO postgres;

--
-- Name: nutrition_plans; Type: TABLE; Schema: petcare; Owner: postgres
--

CREATE TABLE petcare.nutrition_plans (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pet_id uuid NOT NULL,
    name text,
    description text,
    calories_per_day integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE petcare.nutrition_plans OWNER TO postgres;

--
-- Name: password_resets; Type: TABLE; Schema: petcare; Owner: postgres
--

CREATE TABLE petcare.password_resets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    token text NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    used boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE petcare.password_resets OWNER TO postgres;

--
-- Name: pet_photos; Type: TABLE; Schema: petcare; Owner: postgres
--

CREATE TABLE petcare.pet_photos (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pet_id uuid NOT NULL,
    file_name text,
    file_size_bytes bigint,
    mime_type text,
    url text,
    data bytea,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE petcare.pet_photos OWNER TO postgres;

--
-- Name: pets; Type: TABLE; Schema: petcare; Owner: postgres
--

CREATE TABLE petcare.pets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    owner_id uuid NOT NULL,
    name text NOT NULL,
    species text NOT NULL,
    breed text,
    birth_date date,
    age_years integer,
    weight_kg numeric(5,2),
    sex text,
    photo_url text,
    photo_bytea bytea,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE petcare.pets OWNER TO postgres;

--
-- Name: reminders; Type: TABLE; Schema: petcare; Owner: postgres
--

CREATE TABLE petcare.reminders (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    owner_id uuid NOT NULL,
    pet_id uuid,
    title text NOT NULL,
    description text,
    event_time timestamp with time zone NOT NULL,
    timezone text,
    frequency petcare.reminder_frequency DEFAULT 'once'::petcare.reminder_frequency,
    rrule text,
    is_active boolean DEFAULT true NOT NULL,
    notify_by_email boolean DEFAULT true NOT NULL,
    notify_in_app boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE petcare.reminders OWNER TO postgres;

--
-- Name: upcoming_reminders; Type: VIEW; Schema: petcare; Owner: postgres
--

CREATE VIEW petcare.upcoming_reminders AS
 SELECT id,
    owner_id,
    pet_id,
    title,
    description,
    event_time,
    timezone,
    frequency,
    rrule,
    is_active,
    notify_by_email,
    notify_in_app,
    created_at,
    updated_at
   FROM petcare.reminders r
  WHERE ((is_active = true) AND ((frequency <> 'once'::petcare.reminder_frequency) OR (event_time >= now())) AND (event_time >= (now() - '1 day'::interval)))
  ORDER BY event_time;


ALTER VIEW petcare.upcoming_reminders OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: petcare; Owner: postgres
--

CREATE TABLE petcare.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    username text,
    email text NOT NULL,
    hashed_password text NOT NULL,
    full_name text,
    phone text,
    timezone text,
    role text DEFAULT 'user'::text,
    auth_provider text DEFAULT 'local'::text,
    email_verified boolean DEFAULT false,
    verification_token text,
    failed_attempts integer DEFAULT 0,
    locked_until timestamp with time zone,
    refresh_token text,
    last_login_at timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE petcare.users OWNER TO postgres;

--
-- Name: vaccinations; Type: TABLE; Schema: petcare; Owner: postgres
--

CREATE TABLE petcare.vaccinations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pet_id uuid NOT NULL,
    vaccine_name text NOT NULL,
    manufacturer text,
    lot_number text,
    date_administered date NOT NULL,
    next_due date,
    veterinarian text,
    notes text,
    proof_document_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE petcare.vaccinations OWNER TO postgres;

--
-- Name: vet_visits; Type: TABLE; Schema: petcare; Owner: postgres
--

CREATE TABLE petcare.vet_visits (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pet_id uuid NOT NULL,
    visit_date timestamp with time zone NOT NULL,
    reason text,
    diagnosis text,
    treatment text,
    follow_up_date timestamp with time zone,
    veterinarian text,
    documents_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE petcare.vet_visits OWNER TO postgres;

--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: petcare; Owner: postgres
--

COPY petcare.audit_logs (id, actor_user_id, action, object_type, object_id, meta, created_at, updated_at) FROM stdin;
5e9c2022-448b-4c3f-8485-1b72987e94da	e46302ea-b80b-4638-8e26-4a8435b4421a	USER_REGISTERED	User	e46302ea-b80b-4638-8e26-4a8435b4421a	{"email": "john@example.com", "username": "johndoe"}	2025-11-12 17:32:44.277113-05	2025-11-12 17:32:44.277118-05
a70d1f53-6e7c-471c-a7ac-b70bdd422d86	e46302ea-b80b-4638-8e26-4a8435b4421a	USER_LOGIN	User	e46302ea-b80b-4638-8e26-4a8435b4421a	{"email": "john@example.com"}	2025-11-12 17:33:39.578127-05	2025-11-12 17:33:39.57813-05
ae32b3b1-bf0e-4f51-8df0-3f8058f0acb3	e46302ea-b80b-4638-8e26-4a8435b4421a	USER_LOGIN	User	e46302ea-b80b-4638-8e26-4a8435b4421a	{"email": "john@example.com"}	2025-11-12 17:37:24.783137-05	2025-11-12 17:37:24.78314-05
372057a7-dfe3-4474-80c5-9e168a21391a	e46302ea-b80b-4638-8e26-4a8435b4421a	USER_LOGIN	User	e46302ea-b80b-4638-8e26-4a8435b4421a	{"email": "john@example.com"}	2025-11-12 17:38:41.8232-05	2025-11-12 17:38:41.823203-05
abd48e6f-4445-43e3-aec9-2d1772c11039	e46302ea-b80b-4638-8e26-4a8435b4421a	USER_LOGIN	User	e46302ea-b80b-4638-8e26-4a8435b4421a	{"email": "john@example.com"}	2025-11-12 18:47:33.481782-05	2025-11-12 18:47:33.481784-05
1a95fa43-1e76-480f-8e3f-44867e9526ee	e46302ea-b80b-4638-8e26-4a8435b4421a	USER_LOGIN	User	e46302ea-b80b-4638-8e26-4a8435b4421a	{"email": "john@example.com"}	2025-11-12 19:03:29.429154-05	2025-11-12 19:03:29.429157-05
30dedebe-bfd6-4c4d-b8be-54abe24d27d5	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	USER_REGISTERED	User	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	{"email": "julian@example.com", "username": "julian"}	2025-11-12 19:32:50.357229-05	2025-11-12 19:32:50.357232-05
4faafc21-cda1-46c3-ad9c-dfc951a4c064	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	EMAIL_VERIFIED	User	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	\N	2025-11-12 19:34:34.962222-05	2025-11-12 19:34:34.962225-05
62e8383a-116b-4f3d-846e-04d47df03e89	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	USER_LOGIN	User	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	{"email": "julian@example.com"}	2025-11-12 19:35:25.835962-05	2025-11-12 19:35:25.835965-05
ab25447c-02b8-4e82-873b-2faddfd0a9cf	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	USER_LOGIN	User	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	{"email": "julian@example.com"}	2025-11-12 19:38:58.418924-05	2025-11-12 19:38:58.418928-05
d3c03ab1-7077-4b08-be19-e89621d1db5f	e46302ea-b80b-4638-8e26-4a8435b4421a	EMAIL_VERIFIED	User	e46302ea-b80b-4638-8e26-4a8435b4421a	\N	2025-11-12 19:44:11.911332-05	2025-11-12 19:44:11.911336-05
e38a60d4-5b03-4331-94c1-5f032c7af5ce	e46302ea-b80b-4638-8e26-4a8435b4421a	USER_LOGIN	User	e46302ea-b80b-4638-8e26-4a8435b4421a	{"email": "john@example.com"}	2025-11-12 19:44:42.368451-05	2025-11-12 19:44:42.368453-05
fad0d6b4-75ac-423a-97a7-b16e459851d1	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	PASSWORD_RESET	User	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	\N	2025-11-12 19:51:31.608905-05	2025-11-12 19:51:31.608908-05
711ee78b-ef77-4644-a253-d7f0a842dc5c	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	USER_LOGIN	User	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	{"email": "julian@example.com"}	2025-11-12 21:42:25.564508-05	2025-11-12 21:42:25.564512-05
e09f4e6c-0299-407d-8459-d7150af36a43	64c39108-a084-4649-9275-577b1b5a651e	USER_REGISTERED	User	64c39108-a084-4649-9275-577b1b5a651e	{"email": "gonzalo@example.com", "username": "gonzalo"}	2025-11-13 08:31:17.271354-05	2025-11-13 08:31:17.271357-05
1460a8f9-d9dc-462d-9b0c-bc04fa7d8f94	64c39108-a084-4649-9275-577b1b5a651e	EMAIL_VERIFIED	User	64c39108-a084-4649-9275-577b1b5a651e	\N	2025-11-13 08:32:43.63048-05	2025-11-13 08:32:43.630483-05
07e2db1b-6834-4175-8f03-7e42737c6ee0	64c39108-a084-4649-9275-577b1b5a651e	USER_LOGIN	User	64c39108-a084-4649-9275-577b1b5a651e	{"email": "gonzalo@example.com"}	2025-11-13 08:33:10.294398-05	2025-11-13 08:33:10.294401-05
07dd5540-a4ea-454d-9798-2aee2b8434c0	64c39108-a084-4649-9275-577b1b5a651e	PASSWORD_RESET	User	64c39108-a084-4649-9275-577b1b5a651e	\N	2025-11-13 08:40:17.860865-05	2025-11-13 08:40:17.860869-05
4094d393-0d32-4031-8ddd-2afc7e578590	64c39108-a084-4649-9275-577b1b5a651e	USER_LOGIN	User	64c39108-a084-4649-9275-577b1b5a651e	{"email": "gonzalo@example.com"}	2025-11-13 08:45:49.395237-05	2025-11-13 08:45:49.39524-05
e5805fb0-46db-4add-b36e-4975607e0c85	64c39108-a084-4649-9275-577b1b5a651e	USER_LOGOUT	User	64c39108-a084-4649-9275-577b1b5a651e	\N	2025-11-13 08:46:12.440506-05	2025-11-13 08:46:12.440511-05
222814df-8f03-4a08-a22e-35ba88c465e0	0e44b716-317a-4095-a658-62f7c6000103	USER_REGISTERED	User	0e44b716-317a-4095-a658-62f7c6000103	{"email": "prueba@example.com", "username": "prueba"}	2025-11-14 15:17:02.009177-05	2025-11-14 15:17:02.00918-05
fba92436-26ef-4182-81dc-3b68b24055c1	7e726572-8b62-4f32-ab14-2a0d029cc309	USER_REGISTERED	User	7e726572-8b62-4f32-ab14-2a0d029cc309	{"email": "95juliandos@gmail.com", "username": "Julian"}	2025-11-14 15:17:59.031811-05	2025-11-14 15:17:59.031814-05
8b422ffe-1b8f-4356-9f28-1e7a67badc98	6bb60491-ba8b-46f7-bca5-d6342029fd73	USER_REGISTERED	User	6bb60491-ba8b-46f7-bca5-d6342029fd73	{"email": "julian.dos@hotmail.com", "username": "Julianhotmail"}	2025-11-14 17:25:18.580169-05	2025-11-14 17:25:18.580173-05
c35071b9-3096-4f74-985b-00e0921b39b4	508d56b3-91a4-4a81-9aad-413a76b017a0	USER_REGISTERED	User	508d56b3-91a4-4a81-9aad-413a76b017a0	{"email": "9505juliandos@gmail.com", "username": "Juliangmail"}	2025-11-14 17:28:57.338871-05	2025-11-14 17:28:57.338874-05
5a9022bc-85e0-41ea-8140-1c760bd97b97	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	USER_LOGIN	User	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	{"email": "julian@example.com"}	2025-11-18 09:09:39.494285-05	2025-11-18 09:09:39.494288-05
\.


--
-- Data for Name: dewormings; Type: TABLE DATA; Schema: petcare; Owner: postgres
--

COPY petcare.dewormings (id, pet_id, medication, date_administered, next_due, veterinarian, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: meals; Type: TABLE DATA; Schema: petcare; Owner: postgres
--

COPY petcare.meals (id, pet_id, plan_id, meal_time, description, calories, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: petcare; Owner: postgres
--

COPY petcare.notifications (id, reminder_id, owner_id, pet_id, sent_at, method, status, provider_response, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nutrition_plans; Type: TABLE DATA; Schema: petcare; Owner: postgres
--

COPY petcare.nutrition_plans (id, pet_id, name, description, calories_per_day, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: password_resets; Type: TABLE DATA; Schema: petcare; Owner: postgres
--

COPY petcare.password_resets (id, user_id, token, expires_at, used, created_at, updated_at) FROM stdin;
919cb23e-b99c-421c-a482-4469fa17eb5a	882ec8ea-6c58-4390-a3ea-bf7f15b8e667	IgjbREK76zGqVlaZX38qzOR_tLR3-5xpU17xSK8IZ04	2025-11-13 01:47:19.759452-05	t	2025-11-12 19:47:19.760944-05	2025-11-12 19:51:31.377797-05
3a8eeb0c-6131-439f-88ae-4535573ded15	64c39108-a084-4649-9275-577b1b5a651e	H-Fp5mvLSKaMOvbi_9ACESbdGPfTq_vsxPUj4TrJKng	2025-11-13 14:37:51.028729-05	t	2025-11-13 08:37:51.029929-05	2025-11-13 08:40:17.61277-05
\.


--
-- Data for Name: pet_photos; Type: TABLE DATA; Schema: petcare; Owner: postgres
--

COPY petcare.pet_photos (id, pet_id, file_name, file_size_bytes, mime_type, url, data, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: pets; Type: TABLE DATA; Schema: petcare; Owner: postgres
--

COPY petcare.pets (id, owner_id, name, species, breed, birth_date, age_years, weight_kg, sex, photo_url, photo_bytea, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: reminders; Type: TABLE DATA; Schema: petcare; Owner: postgres
--

COPY petcare.reminders (id, owner_id, pet_id, title, description, event_time, timezone, frequency, rrule, is_active, notify_by_email, notify_in_app, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: petcare; Owner: postgres
--

COPY petcare.users (id, username, email, hashed_password, full_name, phone, timezone, role, auth_provider, email_verified, verification_token, failed_attempts, locked_until, refresh_token, last_login_at, is_active, created_at, updated_at) FROM stdin;
64c39108-a084-4649-9275-577b1b5a651e	gonzalo	gonzalo@example.com	$2b$12$YaZTY1vMl8m7MWCiFdpkSuk7SIuKBncRHLECUTnqmAL0Bj/thSvSO	Gonzalo Lira	+54999999999	America/Buenos Aires	user	local	t	\N	0	\N	\N	2025-11-13 13:45:49.391224-05	t	2025-11-13 08:31:17.253992-05	2025-11-13 08:46:12.434469-05
0e44b716-317a-4095-a658-62f7c6000103	prueba	prueba@example.com	$2b$12$83qQhuIE75nL0ecEmIn3c.ilLHjx99.8oBnep97GCF4Tt7ao1CRfi	prueba	+1456789123	America/Bogotá	user	local	f	xiNnlu6cTuCbriabuskLqe0fIWtflohHBYURFQosQhU	0	\N	\N	\N	t	2025-11-14 15:17:01.997446-05	2025-11-14 15:17:01.997449-05
7e726572-8b62-4f32-ab14-2a0d029cc309	Julian	95juliandos@gmail.com	$2b$12$55ldt8qEOc.5qUCxK62WpOY6OTxfs8DPE4a62adqO9YjiQHE5lBgG	Julian Ortega	+573117857025	America/Bogotá	user	local	f	nV7gNWHcAhqwq1sAGWMJYOLfZ_aX-63ZVm9Gr0KqlT0	0	\N	\N	\N	t	2025-11-14 15:17:59.027248-05	2025-11-14 15:17:59.027252-05
6bb60491-ba8b-46f7-bca5-d6342029fd73	Julianhotmail	julian.dos@hotmail.com	$2b$12$QB/fwOQ4Cy3POYxMeWPBgOnfc4IY0QpiPhkTL2zGbscPcf4trVRJq	Julian Ortega	+45321654987	America/Bogotá	user	local	f	4MhfLS1_E9zhgrOO4fFZDKQ8PaaawPjU3JABcj2ewoo	0	\N	\N	\N	t	2025-11-14 17:25:18.571082-05	2025-11-14 17:25:18.571085-05
508d56b3-91a4-4a81-9aad-413a76b017a0	Juliangmail	9505juliandos@gmail.com	$2b$12$i7trrR115JhYfYwCY.DNYeVOFWzAdQTFQ9YxiWS98PEBPhm8uYDaK	Julian Ortega	+45321654987	America/Bogotá	user	local	f	RKXyoCtYMwg-RPyow_ZGrqUeN9hqzW9jO-bRZlQP0hs	0	\N	\N	\N	t	2025-11-14 17:28:57.333906-05	2025-11-14 17:28:57.33391-05
882ec8ea-6c58-4390-a3ea-bf7f15b8e667	julian	julian@example.com	$2b$12$Tk2pkDqfbJos4xZVTm5t7.80sjNQv0Ndu6fOjFH70qhiRnKh1jaqW	Julian	+573117857025	America/Bogota	user	local	t	\N	0	\N	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ODJlYzhlYS02YzU4LTQzOTAtYTNlYS1iZjdmMTViOGU2NjciLCJlbWFpbCI6Imp1bGlhbkBleGFtcGxlLmNvbSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzY0MDk3Nzc5LCJpYXQiOjE3NjM0OTI5NzksInR5cGUiOiJyZWZyZXNoIn0.y6gHhkjt2oLr_Yk-QQyoKIGuv1RP5mKHS4J1OGWg-RQ	2025-11-18 14:09:39.463123-05	t	2025-11-12 19:32:50.349859-05	2025-11-18 09:09:39.21076-05
e46302ea-b80b-4638-8e26-4a8435b4421a	johndoe	john@example.com	$2b$12$pyYUFpP4ASTO8ELTbeZj4.7o.rehvGZfBRRRYMwTMMEZD.6fkUJjW	John Doe	+1234567890	America/Bogota	user	local	t	\N	0	\N	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlNDYzMDJlYS1iODBiLTQ2MzgtOGUyNi00YTg0MzViNDQyMWEiLCJlbWFpbCI6ImpvaG5AZXhhbXBsZS5jb20iLCJyb2xlIjoidXNlciIsImV4cCI6MTc2MzU5OTQ4MiwidHlwZSI6InJlZnJlc2gifQ.ofa-z6WGfVJoXGrx7X04XVicnY5tBm6EMeFw1T9UW-o	2025-11-13 00:44:42.363941-05	t	2025-11-12 17:32:44.262493-05	2025-11-12 19:44:42.14244-05
\.


--
-- Data for Name: vaccinations; Type: TABLE DATA; Schema: petcare; Owner: postgres
--

COPY petcare.vaccinations (id, pet_id, vaccine_name, manufacturer, lot_number, date_administered, next_due, veterinarian, notes, proof_document_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: vet_visits; Type: TABLE DATA; Schema: petcare; Owner: postgres
--

COPY petcare.vet_visits (id, pet_id, visit_date, reason, diagnosis, treatment, follow_up_date, veterinarian, documents_id, created_at, updated_at) FROM stdin;
\.


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: dewormings dewormings_pkey; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.dewormings
    ADD CONSTRAINT dewormings_pkey PRIMARY KEY (id);


--
-- Name: meals meals_pkey; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.meals
    ADD CONSTRAINT meals_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: nutrition_plans nutrition_plans_pkey; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.nutrition_plans
    ADD CONSTRAINT nutrition_plans_pkey PRIMARY KEY (id);


--
-- Name: password_resets password_resets_pkey; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.password_resets
    ADD CONSTRAINT password_resets_pkey PRIMARY KEY (id);


--
-- Name: password_resets password_resets_token_key; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.password_resets
    ADD CONSTRAINT password_resets_token_key UNIQUE (token);


--
-- Name: pet_photos pet_photos_pkey; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.pet_photos
    ADD CONSTRAINT pet_photos_pkey PRIMARY KEY (id);


--
-- Name: pets pets_pkey; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.pets
    ADD CONSTRAINT pets_pkey PRIMARY KEY (id);


--
-- Name: reminders reminders_pkey; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.reminders
    ADD CONSTRAINT reminders_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: vaccinations vaccinations_pkey; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.vaccinations
    ADD CONSTRAINT vaccinations_pkey PRIMARY KEY (id);


--
-- Name: vet_visits vet_visits_pkey; Type: CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.vet_visits
    ADD CONSTRAINT vet_visits_pkey PRIMARY KEY (id);


--
-- Name: idx_pets_owner; Type: INDEX; Schema: petcare; Owner: postgres
--

CREATE INDEX idx_pets_owner ON petcare.pets USING btree (owner_id);


--
-- Name: audit_logs trg_audit_logs_updated_at; Type: TRIGGER; Schema: petcare; Owner: postgres
--

CREATE TRIGGER trg_audit_logs_updated_at BEFORE UPDATE ON petcare.audit_logs FOR EACH ROW EXECUTE FUNCTION petcare.update_updated_at();


--
-- Name: dewormings trg_dewormings_updated_at; Type: TRIGGER; Schema: petcare; Owner: postgres
--

CREATE TRIGGER trg_dewormings_updated_at BEFORE UPDATE ON petcare.dewormings FOR EACH ROW EXECUTE FUNCTION petcare.update_updated_at();


--
-- Name: meals trg_meals_updated_at; Type: TRIGGER; Schema: petcare; Owner: postgres
--

CREATE TRIGGER trg_meals_updated_at BEFORE UPDATE ON petcare.meals FOR EACH ROW EXECUTE FUNCTION petcare.update_updated_at();


--
-- Name: notifications trg_notifications_updated_at; Type: TRIGGER; Schema: petcare; Owner: postgres
--

CREATE TRIGGER trg_notifications_updated_at BEFORE UPDATE ON petcare.notifications FOR EACH ROW EXECUTE FUNCTION petcare.update_updated_at();


--
-- Name: nutrition_plans trg_nutrition_updated_at; Type: TRIGGER; Schema: petcare; Owner: postgres
--

CREATE TRIGGER trg_nutrition_updated_at BEFORE UPDATE ON petcare.nutrition_plans FOR EACH ROW EXECUTE FUNCTION petcare.update_updated_at();


--
-- Name: password_resets trg_password_resets_updated_at; Type: TRIGGER; Schema: petcare; Owner: postgres
--

CREATE TRIGGER trg_password_resets_updated_at BEFORE UPDATE ON petcare.password_resets FOR EACH ROW EXECUTE FUNCTION petcare.update_updated_at();


--
-- Name: pet_photos trg_pet_photos_updated_at; Type: TRIGGER; Schema: petcare; Owner: postgres
--

CREATE TRIGGER trg_pet_photos_updated_at BEFORE UPDATE ON petcare.pet_photos FOR EACH ROW EXECUTE FUNCTION petcare.update_updated_at();


--
-- Name: pets trg_pets_updated_at; Type: TRIGGER; Schema: petcare; Owner: postgres
--

CREATE TRIGGER trg_pets_updated_at BEFORE UPDATE ON petcare.pets FOR EACH ROW EXECUTE FUNCTION petcare.update_updated_at();


--
-- Name: reminders trg_reminders_updated_at; Type: TRIGGER; Schema: petcare; Owner: postgres
--

CREATE TRIGGER trg_reminders_updated_at BEFORE UPDATE ON petcare.reminders FOR EACH ROW EXECUTE FUNCTION petcare.update_updated_at();


--
-- Name: users trg_users_updated_at; Type: TRIGGER; Schema: petcare; Owner: postgres
--

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON petcare.users FOR EACH ROW EXECUTE FUNCTION petcare.update_updated_at();


--
-- Name: vaccinations trg_vaccinations_updated_at; Type: TRIGGER; Schema: petcare; Owner: postgres
--

CREATE TRIGGER trg_vaccinations_updated_at BEFORE UPDATE ON petcare.vaccinations FOR EACH ROW EXECUTE FUNCTION petcare.update_updated_at();


--
-- Name: vet_visits trg_vet_visits_updated_at; Type: TRIGGER; Schema: petcare; Owner: postgres
--

CREATE TRIGGER trg_vet_visits_updated_at BEFORE UPDATE ON petcare.vet_visits FOR EACH ROW EXECUTE FUNCTION petcare.update_updated_at();


--
-- Name: audit_logs audit_logs_actor_user_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.audit_logs
    ADD CONSTRAINT audit_logs_actor_user_id_fkey FOREIGN KEY (actor_user_id) REFERENCES petcare.users(id);


--
-- Name: dewormings dewormings_pet_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.dewormings
    ADD CONSTRAINT dewormings_pet_id_fkey FOREIGN KEY (pet_id) REFERENCES petcare.pets(id) ON DELETE CASCADE;


--
-- Name: meals meals_pet_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.meals
    ADD CONSTRAINT meals_pet_id_fkey FOREIGN KEY (pet_id) REFERENCES petcare.pets(id) ON DELETE CASCADE;


--
-- Name: meals meals_plan_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.meals
    ADD CONSTRAINT meals_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES petcare.nutrition_plans(id);


--
-- Name: notifications notifications_owner_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.notifications
    ADD CONSTRAINT notifications_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES petcare.users(id) ON DELETE SET NULL;


--
-- Name: notifications notifications_pet_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.notifications
    ADD CONSTRAINT notifications_pet_id_fkey FOREIGN KEY (pet_id) REFERENCES petcare.pets(id) ON DELETE SET NULL;


--
-- Name: notifications notifications_reminder_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.notifications
    ADD CONSTRAINT notifications_reminder_id_fkey FOREIGN KEY (reminder_id) REFERENCES petcare.reminders(id) ON DELETE SET NULL;


--
-- Name: nutrition_plans nutrition_plans_pet_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.nutrition_plans
    ADD CONSTRAINT nutrition_plans_pet_id_fkey FOREIGN KEY (pet_id) REFERENCES petcare.pets(id) ON DELETE CASCADE;


--
-- Name: password_resets password_resets_user_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.password_resets
    ADD CONSTRAINT password_resets_user_id_fkey FOREIGN KEY (user_id) REFERENCES petcare.users(id) ON DELETE CASCADE;


--
-- Name: pet_photos pet_photos_pet_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.pet_photos
    ADD CONSTRAINT pet_photos_pet_id_fkey FOREIGN KEY (pet_id) REFERENCES petcare.pets(id) ON DELETE CASCADE;


--
-- Name: pets pets_owner_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.pets
    ADD CONSTRAINT pets_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES petcare.users(id) ON DELETE CASCADE;


--
-- Name: reminders reminders_owner_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.reminders
    ADD CONSTRAINT reminders_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES petcare.users(id) ON DELETE CASCADE;


--
-- Name: reminders reminders_pet_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.reminders
    ADD CONSTRAINT reminders_pet_id_fkey FOREIGN KEY (pet_id) REFERENCES petcare.pets(id) ON DELETE CASCADE;


--
-- Name: vaccinations vaccinations_pet_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.vaccinations
    ADD CONSTRAINT vaccinations_pet_id_fkey FOREIGN KEY (pet_id) REFERENCES petcare.pets(id) ON DELETE CASCADE;


--
-- Name: vaccinations vaccinations_proof_document_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.vaccinations
    ADD CONSTRAINT vaccinations_proof_document_id_fkey FOREIGN KEY (proof_document_id) REFERENCES petcare.pet_photos(id);


--
-- Name: vet_visits vet_visits_documents_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.vet_visits
    ADD CONSTRAINT vet_visits_documents_id_fkey FOREIGN KEY (documents_id) REFERENCES petcare.pet_photos(id);


--
-- Name: vet_visits vet_visits_pet_id_fkey; Type: FK CONSTRAINT; Schema: petcare; Owner: postgres
--

ALTER TABLE ONLY petcare.vet_visits
    ADD CONSTRAINT vet_visits_pet_id_fkey FOREIGN KEY (pet_id) REFERENCES petcare.pets(id) ON DELETE CASCADE;


--
-- Name: TABLE audit_logs; Type: ACL; Schema: petcare; Owner: postgres
--

GRANT ALL ON TABLE petcare.audit_logs TO petuser;


--
-- Name: TABLE dewormings; Type: ACL; Schema: petcare; Owner: postgres
--

GRANT ALL ON TABLE petcare.dewormings TO petuser;


--
-- Name: TABLE meals; Type: ACL; Schema: petcare; Owner: postgres
--

GRANT ALL ON TABLE petcare.meals TO petuser;


--
-- Name: TABLE notifications; Type: ACL; Schema: petcare; Owner: postgres
--

GRANT ALL ON TABLE petcare.notifications TO petuser;


--
-- Name: TABLE nutrition_plans; Type: ACL; Schema: petcare; Owner: postgres
--

GRANT ALL ON TABLE petcare.nutrition_plans TO petuser;


--
-- Name: TABLE password_resets; Type: ACL; Schema: petcare; Owner: postgres
--

GRANT ALL ON TABLE petcare.password_resets TO petuser;


--
-- Name: TABLE pet_photos; Type: ACL; Schema: petcare; Owner: postgres
--

GRANT ALL ON TABLE petcare.pet_photos TO petuser;


--
-- Name: TABLE pets; Type: ACL; Schema: petcare; Owner: postgres
--

GRANT ALL ON TABLE petcare.pets TO petuser;


--
-- Name: TABLE reminders; Type: ACL; Schema: petcare; Owner: postgres
--

GRANT ALL ON TABLE petcare.reminders TO petuser;


--
-- Name: TABLE upcoming_reminders; Type: ACL; Schema: petcare; Owner: postgres
--

GRANT ALL ON TABLE petcare.upcoming_reminders TO petuser;


--
-- Name: TABLE users; Type: ACL; Schema: petcare; Owner: postgres
--

GRANT ALL ON TABLE petcare.users TO petuser;


--
-- Name: TABLE vaccinations; Type: ACL; Schema: petcare; Owner: postgres
--

GRANT ALL ON TABLE petcare.vaccinations TO petuser;


--
-- Name: TABLE vet_visits; Type: ACL; Schema: petcare; Owner: postgres
--

GRANT ALL ON TABLE petcare.vet_visits TO petuser;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: petcare; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA petcare GRANT ALL ON SEQUENCES TO petuser;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: petcare; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA petcare GRANT ALL ON TABLES TO petuser;


--
-- PostgreSQL database dump complete
--

\unrestrict efcPkso969qxnoWrhIOwTfY9V5J8dEew87AN20aMBFQRkhxV5Hi64oMLLi29dvH

