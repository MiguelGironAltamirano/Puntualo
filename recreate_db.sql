--
-- PostgreSQL database dump
--

\restrict tjgqzUSXyXKgcRy4gfVKJ0ZBebDvx99pzKeFnCHvAFJQYO0UhVBmeAoHBBfeqdt

-- Dumped from database version 16.13 (Debian 16.13-1.pgdg13+1)
-- Dumped by pg_dump version 16.13 (Debian 16.13-1.pgdg13+1)

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
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: academic_degrees; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.academic_degrees (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    level character varying(50) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_academic_degrees_level CHECK (((level)::text = ANY ((ARRAY['bachelor'::character varying, 'master'::character varying, 'doctorate'::character varying, 'specialization'::character varying])::text[])))
);


--
-- Name: academic_degrees_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.academic_degrees ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.academic_degrees_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: ai_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ai_jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_type character varying(100) NOT NULL,
    status character varying(20) NOT NULL,
    input_payload jsonb,
    result_payload jsonb,
    error_message text,
    started_at timestamp with time zone,
    finished_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_ai_jobs_status CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'running'::character varying, 'completed'::character varying, 'failed'::character varying])::text[])))
);


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: banned_terms; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.banned_terms (
    id bigint NOT NULL,
    term character varying(100) NOT NULL,
    severity character varying(10) DEFAULT 'high'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_banned_terms_severity CHECK (((severity)::text = ANY ((ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying])::text[])))
);


--
-- Name: banned_terms_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.banned_terms ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.banned_terms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: career_courses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.career_courses (
    career_id bigint NOT NULL,
    course_id bigint NOT NULL
);


--
-- Name: careers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.careers (
    id bigint NOT NULL,
    faculty_id bigint NOT NULL,
    name character varying(150) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: careers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.careers ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.careers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: chat_messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_messages (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_id uuid NOT NULL,
    role text NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_chat_messages_role CHECK ((role = ANY (ARRAY['user'::text, 'assistant'::text])))
);


--
-- Name: chat_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_sessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    ended_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: comment_reactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comment_reactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    comment_id uuid NOT NULL,
    user_id uuid NOT NULL,
    type character varying(20) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_reactions_type CHECK (((type)::text = ANY ((ARRAY['like'::character varying, 'dislike'::character varying])::text[])))
);


--
-- Name: comment_reports; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comment_reports (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    comment_id uuid NOT NULL,
    user_id uuid NOT NULL,
    reason character varying(20) NOT NULL,
    description text,
    status character varying(30) DEFAULT 'pending'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_reports_reason CHECK (((reason)::text = ANY ((ARRAY['spam'::character varying, 'hate_speech'::character varying, 'harassment'::character varying, 'off_topic'::character varying, 'other'::character varying])::text[]))),
    CONSTRAINT ck_reports_status CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'under_review'::character varying, 'resolved_offensive'::character varying, 'resolved_safe'::character varying])::text[])))
);


--
-- Name: comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    evaluation_id uuid NOT NULL,
    user_id uuid,
    professor_id uuid NOT NULL,
    course_id bigint NOT NULL,
    text text,
    modality character varying(15) NOT NULL,
    status character varying(30) DEFAULT 'published'::character varying NOT NULL,
    hidden_at timestamp with time zone,
    removed_at timestamp with time zone,
    moderation_verdict character varying(20),
    like_count integer DEFAULT 0 NOT NULL,
    dislike_count integer DEFAULT 0 NOT NULL,
    reports_count integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    CONSTRAINT ck_comments_modality CHECK (((modality)::text = ANY ((ARRAY['virtual'::character varying, 'presencial'::character varying, 'ambas'::character varying])::text[]))),
    CONSTRAINT ck_comments_status CHECK (((status)::text = ANY ((ARRAY['published'::character varying, 'hidden_pending_review'::character varying, 'removed'::character varying])::text[]))),
    CONSTRAINT ck_comments_text_null_when_removed CHECK (((removed_at IS NULL) OR (text IS NULL)))
);


--
-- Name: courses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.courses (
    id bigint NOT NULL,
    university_id bigint NOT NULL,
    faculty_id bigint NOT NULL,
    name character varying(150) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone
);


--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.courses ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.courses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: email_verifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.email_verifications (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email character varying NOT NULL,
    full_name character varying NOT NULL,
    username character varying NOT NULL,
    dni character varying,
    career_id bigint,
    hashed_password character varying NOT NULL,
    code_hash character varying NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    attempts integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: evaluation_hashtags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.evaluation_hashtags (
    evaluation_id uuid NOT NULL,
    hashtag_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: evaluations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.evaluations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    professor_id uuid NOT NULL,
    course_id bigint NOT NULL,
    semester character varying(7) NOT NULL,
    clarity integer NOT NULL,
    easiness integer NOT NULL,
    helpfulness integer NOT NULL,
    punctuality integer NOT NULL,
    modality character varying(15) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_evaluations_clarity CHECK (((clarity >= 1) AND (clarity <= 5))),
    CONSTRAINT ck_evaluations_easiness CHECK (((easiness >= 1) AND (easiness <= 5))),
    CONSTRAINT ck_evaluations_helpfulness CHECK (((helpfulness >= 1) AND (helpfulness <= 5))),
    CONSTRAINT ck_evaluations_modality CHECK (((modality)::text = ANY ((ARRAY['virtual'::character varying, 'presencial'::character varying, 'ambas'::character varying])::text[]))),
    CONSTRAINT ck_evaluations_punctuality CHECK (((punctuality >= 1) AND (punctuality <= 5)))
);


--
-- Name: faculties; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.faculties (
    id bigint NOT NULL,
    university_id bigint NOT NULL,
    name character varying(150) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: faculties_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.faculties ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.faculties_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: hashtags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hashtags (
    id bigint NOT NULL,
    label character varying(100) NOT NULL,
    created_by_id uuid,
    usage_count integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: hashtags_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.hashtags ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.hashtags_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: moderation_actions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.moderation_actions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    comment_id uuid NOT NULL,
    decision character varying NOT NULL,
    reasoning text NOT NULL,
    reports_count_at_trigger integer NOT NULL,
    triggered_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_moderation_actions_decision CHECK (((decision)::text = ANY ((ARRAY['keep'::character varying, 'remove'::character varying])::text[])))
);


--
-- Name: password_resets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.password_resets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email character varying NOT NULL,
    code_hash character varying NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    attempts integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: professor_ai_summaries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.professor_ai_summaries (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    professor_id uuid NOT NULL,
    summary text NOT NULL,
    pros text[] DEFAULT '{}'::text[] NOT NULL,
    cons text[] DEFAULT '{}'::text[] NOT NULL,
    model_version character varying(100) NOT NULL,
    generated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: professor_courses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.professor_courses (
    professor_id uuid NOT NULL,
    course_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: professor_degrees; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.professor_degrees (
    professor_id uuid NOT NULL,
    degree_id bigint NOT NULL,
    institution character varying(200),
    year_obtained integer
);


--
-- Name: professor_evidence; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.professor_evidence (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    professor_id uuid NOT NULL,
    source character varying(30) NOT NULL,
    role character varying(20) NOT NULL,
    found boolean DEFAULT false NOT NULL,
    affiliation_confirmed boolean DEFAULT false NOT NULL,
    confidence numeric(3,2),
    raw_payload jsonb,
    fetched_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: professors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.professors (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    full_name character varying(200) NOT NULL,
    university_id bigint NOT NULL,
    faculty_id bigint NOT NULL,
    validation_status character varying(30) DEFAULT 'pending_validation'::character varying NOT NULL,
    registered_by_id uuid,
    global_score numeric(3,2),
    total_evaluations integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    CONSTRAINT ck_professors_global_score_range CHECK (((global_score IS NULL) OR ((global_score >= 1.0) AND (global_score <= 5.0)))),
    CONSTRAINT ck_professors_validation_status CHECK (((validation_status)::text = ANY ((ARRAY['pending_validation'::character varying, 'validated'::character varying, 'not_found'::character varying, 'rejected'::character varying])::text[])))
);


--
-- Name: universities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.universities (
    id bigint NOT NULL,
    name character varying(150) NOT NULL,
    city character varying(100) NOT NULL,
    country character varying(100) DEFAULT 'Perú'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: universities_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.universities ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.universities_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: uploaded_documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.uploaded_documents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    document_type character varying(20) NOT NULL,
    file_path text NOT NULL,
    mime_type character varying(50) NOT NULL,
    file_size_bytes bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_uploaded_documents_mime CHECK (((mime_type)::text = ANY ((ARRAY['image/jpeg'::character varying, 'image/png'::character varying, 'application/pdf'::character varying])::text[]))),
    CONSTRAINT ck_uploaded_documents_type CHECK (((document_type)::text = ANY ((ARRAY['carnet'::character varying, 'matricula'::character varying])::text[])))
);


--
-- Name: user_strikes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_strikes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    comment_id uuid NOT NULL,
    moderation_action_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email character varying NOT NULL,
    full_name character varying NOT NULL,
    username character varying NOT NULL,
    dni character varying,
    career_id bigint,
    hashed_password character varying NOT NULL,
    role character varying DEFAULT 'student'::character varying NOT NULL,
    provider character varying DEFAULT 'local'::character varying NOT NULL,
    is_verified boolean DEFAULT false NOT NULL,
    strike_count integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    CONSTRAINT ck_users_role CHECK (((role)::text = ANY ((ARRAY['student'::character varying, 'admin'::character varying])::text[])))
);


--
-- Name: verification_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.verification_requests (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    document_id uuid,
    status character varying DEFAULT 'pending'::character varying NOT NULL,
    rejection_reason text,
    reviewed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_verification_requests_status CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'approved'::character varying, 'rejected'::character varying])::text[])))
);


--
-- Name: academic_degrees academic_degrees_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.academic_degrees
    ADD CONSTRAINT academic_degrees_name_key UNIQUE (name);


--
-- Name: academic_degrees academic_degrees_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.academic_degrees
    ADD CONSTRAINT academic_degrees_pkey PRIMARY KEY (id);


--
-- Name: ai_jobs ai_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_jobs
    ADD CONSTRAINT ai_jobs_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: banned_terms banned_terms_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.banned_terms
    ADD CONSTRAINT banned_terms_pkey PRIMARY KEY (id);


--
-- Name: banned_terms banned_terms_term_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.banned_terms
    ADD CONSTRAINT banned_terms_term_key UNIQUE (term);


--
-- Name: careers careers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.careers
    ADD CONSTRAINT careers_pkey PRIMARY KEY (id);


--
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);


--
-- Name: chat_sessions chat_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_pkey PRIMARY KEY (id);


--
-- Name: comment_reactions comment_reactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_reactions
    ADD CONSTRAINT comment_reactions_pkey PRIMARY KEY (id);


--
-- Name: comment_reports comment_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_reports
    ADD CONSTRAINT comment_reports_pkey PRIMARY KEY (id);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: email_verifications email_verifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.email_verifications
    ADD CONSTRAINT email_verifications_pkey PRIMARY KEY (id);


--
-- Name: evaluations evaluations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evaluations
    ADD CONSTRAINT evaluations_pkey PRIMARY KEY (id);


--
-- Name: faculties faculties_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.faculties
    ADD CONSTRAINT faculties_pkey PRIMARY KEY (id);


--
-- Name: hashtags hashtags_label_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hashtags
    ADD CONSTRAINT hashtags_label_key UNIQUE (label);


--
-- Name: hashtags hashtags_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hashtags
    ADD CONSTRAINT hashtags_pkey PRIMARY KEY (id);


--
-- Name: moderation_actions moderation_actions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moderation_actions
    ADD CONSTRAINT moderation_actions_pkey PRIMARY KEY (id);


--
-- Name: password_resets password_resets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT password_resets_pkey PRIMARY KEY (id);


--
-- Name: career_courses pk_career_courses; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_courses
    ADD CONSTRAINT pk_career_courses PRIMARY KEY (career_id, course_id);


--
-- Name: evaluation_hashtags pk_evaluation_hashtags; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evaluation_hashtags
    ADD CONSTRAINT pk_evaluation_hashtags PRIMARY KEY (evaluation_id, hashtag_id);


--
-- Name: professor_courses pk_professor_courses; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professor_courses
    ADD CONSTRAINT pk_professor_courses PRIMARY KEY (professor_id, course_id);


--
-- Name: professor_degrees pk_professor_degrees; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professor_degrees
    ADD CONSTRAINT pk_professor_degrees PRIMARY KEY (professor_id, degree_id);


--
-- Name: professor_ai_summaries professor_ai_summaries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professor_ai_summaries
    ADD CONSTRAINT professor_ai_summaries_pkey PRIMARY KEY (id);


--
-- Name: professor_evidence professor_evidence_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professor_evidence
    ADD CONSTRAINT professor_evidence_pkey PRIMARY KEY (id);


--
-- Name: professors professors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professors
    ADD CONSTRAINT professors_pkey PRIMARY KEY (id);


--
-- Name: universities universities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.universities
    ADD CONSTRAINT universities_pkey PRIMARY KEY (id);


--
-- Name: uploaded_documents uploaded_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uploaded_documents
    ADD CONSTRAINT uploaded_documents_pkey PRIMARY KEY (id);


--
-- Name: careers uq_careers_name_faculty; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.careers
    ADD CONSTRAINT uq_careers_name_faculty UNIQUE (name, faculty_id);


--
-- Name: comments uq_comments_evaluation_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT uq_comments_evaluation_id UNIQUE (evaluation_id);


--
-- Name: email_verifications uq_email_verifications_dni; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.email_verifications
    ADD CONSTRAINT uq_email_verifications_dni UNIQUE (dni);


--
-- Name: email_verifications uq_email_verifications_email; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.email_verifications
    ADD CONSTRAINT uq_email_verifications_email UNIQUE (email);


--
-- Name: email_verifications uq_email_verifications_username; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.email_verifications
    ADD CONSTRAINT uq_email_verifications_username UNIQUE (username);


--
-- Name: evaluations uq_evaluations_user_professor_course_semester; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evaluations
    ADD CONSTRAINT uq_evaluations_user_professor_course_semester UNIQUE (user_id, professor_id, course_id, semester);


--
-- Name: faculties uq_faculties_name_university; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.faculties
    ADD CONSTRAINT uq_faculties_name_university UNIQUE (name, university_id);


--
-- Name: password_resets uq_password_resets_email; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT uq_password_resets_email UNIQUE (email);


--
-- Name: professor_ai_summaries uq_professor_ai_summaries_professor; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professor_ai_summaries
    ADD CONSTRAINT uq_professor_ai_summaries_professor UNIQUE (professor_id);


--
-- Name: comment_reactions uq_reactions_user_comment; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_reactions
    ADD CONSTRAINT uq_reactions_user_comment UNIQUE (comment_id, user_id);


--
-- Name: comment_reports uq_reports_user_comment; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_reports
    ADD CONSTRAINT uq_reports_user_comment UNIQUE (comment_id, user_id);


--
-- Name: universities uq_universities_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.universities
    ADD CONSTRAINT uq_universities_name UNIQUE (name);


--
-- Name: user_strikes user_strikes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_strikes
    ADD CONSTRAINT user_strikes_pkey PRIMARY KEY (id);


--
-- Name: users users_dni_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_dni_key UNIQUE (dni);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: verification_requests verification_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verification_requests
    ADD CONSTRAINT verification_requests_pkey PRIMARY KEY (id);


--
-- Name: idx_professor_evidence_lookup; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_professor_evidence_lookup ON public.professor_evidence USING btree (professor_id, source);


--
-- Name: ix_ai_jobs_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_jobs_status ON public.ai_jobs USING btree (status);


--
-- Name: ix_career_courses_career_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_career_courses_career_id ON public.career_courses USING btree (career_id);


--
-- Name: ix_career_courses_course_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_career_courses_course_id ON public.career_courses USING btree (course_id);


--
-- Name: ix_careers_faculty_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_careers_faculty_id ON public.careers USING btree (faculty_id);


--
-- Name: ix_chat_messages_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_chat_messages_session_id ON public.chat_messages USING btree (session_id);


--
-- Name: ix_chat_sessions_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_chat_sessions_user_id ON public.chat_sessions USING btree (user_id);


--
-- Name: ix_comment_reactions_comment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_comment_reactions_comment_id ON public.comment_reactions USING btree (comment_id);


--
-- Name: ix_comment_reactions_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_comment_reactions_user_id ON public.comment_reactions USING btree (user_id);


--
-- Name: ix_comment_reports_comment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_comment_reports_comment_id ON public.comment_reports USING btree (comment_id);


--
-- Name: ix_comment_reports_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_comment_reports_user_id ON public.comment_reports USING btree (user_id);


--
-- Name: ix_comments_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_comments_is_active ON public.comments USING btree (is_active);


--
-- Name: ix_comments_professor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_comments_professor_id ON public.comments USING btree (professor_id);


--
-- Name: ix_comments_professor_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_comments_professor_status ON public.comments USING btree (professor_id, status);


--
-- Name: ix_comments_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_comments_status ON public.comments USING btree (status);


--
-- Name: ix_comments_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_comments_user_id ON public.comments USING btree (user_id);


--
-- Name: ix_courses_faculty_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_courses_faculty_id ON public.courses USING btree (faculty_id);


--
-- Name: ix_courses_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_courses_is_active ON public.courses USING btree (is_active);


--
-- Name: ix_courses_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_courses_name ON public.courses USING btree (name);


--
-- Name: ix_courses_university_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_courses_university_id ON public.courses USING btree (university_id);


--
-- Name: ix_email_verifications_career_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_email_verifications_career_id ON public.email_verifications USING btree (career_id);


--
-- Name: ix_evaluation_hashtags_evaluation_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_evaluation_hashtags_evaluation_id ON public.evaluation_hashtags USING btree (evaluation_id);


--
-- Name: ix_evaluation_hashtags_hashtag_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_evaluation_hashtags_hashtag_id ON public.evaluation_hashtags USING btree (hashtag_id);


--
-- Name: ix_evaluations_course_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_evaluations_course_id ON public.evaluations USING btree (course_id);


--
-- Name: ix_evaluations_professor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_evaluations_professor_id ON public.evaluations USING btree (professor_id);


--
-- Name: ix_evaluations_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_evaluations_user_id ON public.evaluations USING btree (user_id);


--
-- Name: ix_faculties_university_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_faculties_university_id ON public.faculties USING btree (university_id);


--
-- Name: ix_hashtags_created_by_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hashtags_created_by_id ON public.hashtags USING btree (created_by_id);


--
-- Name: ix_hashtags_label_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hashtags_label_gin ON public.hashtags USING gin (label public.gin_trgm_ops);


--
-- Name: ix_moderation_actions_comment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_moderation_actions_comment_id ON public.moderation_actions USING btree (comment_id);


--
-- Name: ix_professor_ai_summaries_professor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_professor_ai_summaries_professor_id ON public.professor_ai_summaries USING btree (professor_id);


--
-- Name: ix_professor_courses_course_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_professor_courses_course_id ON public.professor_courses USING btree (course_id);


--
-- Name: ix_professor_courses_professor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_professor_courses_professor_id ON public.professor_courses USING btree (professor_id);


--
-- Name: ix_professor_degrees_degree_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_professor_degrees_degree_id ON public.professor_degrees USING btree (degree_id);


--
-- Name: ix_professor_degrees_professor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_professor_degrees_professor_id ON public.professor_degrees USING btree (professor_id);


--
-- Name: ix_professor_evidence_professor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_professor_evidence_professor_id ON public.professor_evidence USING btree (professor_id);


--
-- Name: ix_professors_faculty_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_professors_faculty_id ON public.professors USING btree (faculty_id);


--
-- Name: ix_professors_full_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_professors_full_name ON public.professors USING btree (full_name);


--
-- Name: ix_professors_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_professors_is_active ON public.professors USING btree (is_active);


--
-- Name: ix_professors_university_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_professors_university_id ON public.professors USING btree (university_id);


--
-- Name: ix_uploaded_documents_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_uploaded_documents_user_id ON public.uploaded_documents USING btree (user_id);


--
-- Name: ix_user_strikes_comment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_strikes_comment_id ON public.user_strikes USING btree (comment_id);


--
-- Name: ix_user_strikes_moderation_action_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_strikes_moderation_action_id ON public.user_strikes USING btree (moderation_action_id);


--
-- Name: ix_user_strikes_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_strikes_user_id ON public.user_strikes USING btree (user_id);


--
-- Name: ix_users_career_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_career_id ON public.users USING btree (career_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_is_active ON public.users USING btree (is_active);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_verification_requests_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_verification_requests_user_id ON public.verification_requests USING btree (user_id);


--
-- Name: uq_courses_name_university_active; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_courses_name_university_active ON public.courses USING btree (lower((name)::text), university_id) WHERE (is_active = true);


--
-- Name: uq_professors_name_university_active; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_professors_name_university_active ON public.professors USING btree (lower((full_name)::text), university_id) WHERE (is_active = true);


--
-- Name: career_courses career_courses_career_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_courses
    ADD CONSTRAINT career_courses_career_id_fkey FOREIGN KEY (career_id) REFERENCES public.careers(id) ON DELETE CASCADE;


--
-- Name: career_courses career_courses_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_courses
    ADD CONSTRAINT career_courses_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE RESTRICT;


--
-- Name: careers careers_faculty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.careers
    ADD CONSTRAINT careers_faculty_id_fkey FOREIGN KEY (faculty_id) REFERENCES public.faculties(id) ON DELETE CASCADE;


--
-- Name: chat_messages chat_messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.chat_sessions(id) ON DELETE CASCADE;


--
-- Name: chat_sessions chat_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: comment_reactions comment_reactions_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_reactions
    ADD CONSTRAINT comment_reactions_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id) ON DELETE CASCADE;


--
-- Name: comment_reactions comment_reactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_reactions
    ADD CONSTRAINT comment_reactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: comment_reports comment_reports_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_reports
    ADD CONSTRAINT comment_reports_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id) ON DELETE CASCADE;


--
-- Name: comment_reports comment_reports_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_reports
    ADD CONSTRAINT comment_reports_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: comments comments_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE RESTRICT;


--
-- Name: comments comments_evaluation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_evaluation_id_fkey FOREIGN KEY (evaluation_id) REFERENCES public.evaluations(id) ON DELETE CASCADE;


--
-- Name: comments comments_professor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_professor_id_fkey FOREIGN KEY (professor_id) REFERENCES public.professors(id) ON DELETE CASCADE;


--
-- Name: comments comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: courses courses_faculty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_faculty_id_fkey FOREIGN KEY (faculty_id) REFERENCES public.faculties(id) ON DELETE RESTRICT;


--
-- Name: courses courses_university_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_university_id_fkey FOREIGN KEY (university_id) REFERENCES public.universities(id) ON DELETE RESTRICT;


--
-- Name: email_verifications email_verifications_career_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.email_verifications
    ADD CONSTRAINT email_verifications_career_id_fkey FOREIGN KEY (career_id) REFERENCES public.careers(id) ON DELETE SET NULL;


--
-- Name: evaluation_hashtags evaluation_hashtags_evaluation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evaluation_hashtags
    ADD CONSTRAINT evaluation_hashtags_evaluation_id_fkey FOREIGN KEY (evaluation_id) REFERENCES public.evaluations(id) ON DELETE CASCADE;


--
-- Name: evaluation_hashtags evaluation_hashtags_hashtag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evaluation_hashtags
    ADD CONSTRAINT evaluation_hashtags_hashtag_id_fkey FOREIGN KEY (hashtag_id) REFERENCES public.hashtags(id) ON DELETE RESTRICT;


--
-- Name: evaluations evaluations_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evaluations
    ADD CONSTRAINT evaluations_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE RESTRICT;


--
-- Name: evaluations evaluations_professor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evaluations
    ADD CONSTRAINT evaluations_professor_id_fkey FOREIGN KEY (professor_id) REFERENCES public.professors(id) ON DELETE CASCADE;


--
-- Name: evaluations evaluations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evaluations
    ADD CONSTRAINT evaluations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: faculties faculties_university_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.faculties
    ADD CONSTRAINT faculties_university_id_fkey FOREIGN KEY (university_id) REFERENCES public.universities(id) ON DELETE CASCADE;


--
-- Name: hashtags hashtags_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hashtags
    ADD CONSTRAINT hashtags_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: moderation_actions moderation_actions_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moderation_actions
    ADD CONSTRAINT moderation_actions_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id) ON DELETE CASCADE;


--
-- Name: professor_ai_summaries professor_ai_summaries_professor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professor_ai_summaries
    ADD CONSTRAINT professor_ai_summaries_professor_id_fkey FOREIGN KEY (professor_id) REFERENCES public.professors(id) ON DELETE CASCADE;


--
-- Name: professor_courses professor_courses_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professor_courses
    ADD CONSTRAINT professor_courses_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE RESTRICT;


--
-- Name: professor_courses professor_courses_professor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professor_courses
    ADD CONSTRAINT professor_courses_professor_id_fkey FOREIGN KEY (professor_id) REFERENCES public.professors(id) ON DELETE CASCADE;


--
-- Name: professor_degrees professor_degrees_degree_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professor_degrees
    ADD CONSTRAINT professor_degrees_degree_id_fkey FOREIGN KEY (degree_id) REFERENCES public.academic_degrees(id) ON DELETE RESTRICT;


--
-- Name: professor_degrees professor_degrees_professor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professor_degrees
    ADD CONSTRAINT professor_degrees_professor_id_fkey FOREIGN KEY (professor_id) REFERENCES public.professors(id) ON DELETE CASCADE;


--
-- Name: professor_evidence professor_evidence_professor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professor_evidence
    ADD CONSTRAINT professor_evidence_professor_id_fkey FOREIGN KEY (professor_id) REFERENCES public.professors(id) ON DELETE CASCADE;


--
-- Name: professors professors_faculty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professors
    ADD CONSTRAINT professors_faculty_id_fkey FOREIGN KEY (faculty_id) REFERENCES public.faculties(id) ON DELETE RESTRICT;


--
-- Name: professors professors_registered_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professors
    ADD CONSTRAINT professors_registered_by_id_fkey FOREIGN KEY (registered_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: professors professors_university_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professors
    ADD CONSTRAINT professors_university_id_fkey FOREIGN KEY (university_id) REFERENCES public.universities(id) ON DELETE RESTRICT;


--
-- Name: uploaded_documents uploaded_documents_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uploaded_documents
    ADD CONSTRAINT uploaded_documents_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_strikes user_strikes_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_strikes
    ADD CONSTRAINT user_strikes_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id) ON DELETE CASCADE;


--
-- Name: user_strikes user_strikes_moderation_action_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_strikes
    ADD CONSTRAINT user_strikes_moderation_action_id_fkey FOREIGN KEY (moderation_action_id) REFERENCES public.moderation_actions(id) ON DELETE CASCADE;


--
-- Name: user_strikes user_strikes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_strikes
    ADD CONSTRAINT user_strikes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: users users_career_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_career_id_fkey FOREIGN KEY (career_id) REFERENCES public.careers(id) ON DELETE SET NULL;


--
-- Name: verification_requests verification_requests_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verification_requests
    ADD CONSTRAINT verification_requests_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.uploaded_documents(id) ON DELETE SET NULL;


--
-- Name: verification_requests verification_requests_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verification_requests
    ADD CONSTRAINT verification_requests_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict tjgqzUSXyXKgcRy4gfVKJ0ZBebDvx99pzKeFnCHvAFJQYO0UhVBmeAoHBBfeqdt

