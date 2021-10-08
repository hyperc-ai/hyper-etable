--
-- PostgreSQL database dump
--

-- Dumped from database version 10.18 (Ubuntu 10.18-0ubuntu0.18.04.1)
-- Dumped by pg_dump version 10.18 (Ubuntu 10.18-0ubuntu0.18.04.1)

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
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: plpython3u; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpython3u WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpython3u; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpython3u IS 'PL/Python3U untrusted procedural language';


--
-- Name: actions(); Type: FUNCTION; Schema: public; Owner: myrole
--

CREATE FUNCTION public.actions() RETURNS boolean
    LANGUAGE plpython3u
    AS $$def move_forward(t:TRANSPORT_Class, l_a:LOCATION_Class):
    assert t.LOCATION == l_a.LOCATION_A
    t.LOCATION = l_a.LOCATION_B

def move_backward(t:TRANSPORT_Class, l_a:LOCATION_Class):
    assert t.LOCATION == l_a.LOCATION_B
    t.LOCATION = l_a.LOCATION_A

def my_truck_finish(t:TRANSPORT_Class):
    assert t.LOCATION == 'LocC'
    assert t.NAME == 'MyTruck1'
    DATA.GOAL=True    $$;


ALTER FUNCTION public.actions() OWNER TO myrole;

--
-- Name: dummy_test(); Type: FUNCTION; Schema: public; Owner: myrole
--

CREATE FUNCTION public.dummy_test() RETURNS boolean
    LANGUAGE plpython3u
    AS $$import sys
import dummy_test

with open('/tmp/plpython.out', 'w') as f:
    print(sys.version,file=f)
    source = plpy.execute("SELECT routine_definition FROM information_schema.routines WHERE specific_schema LIKE 'public' AND routine_name LIKE 'actions';", 100)
    print(source[0]['routine_definition'],file=f)
return True

$$;


ALTER FUNCTION public.dummy_test() OWNER TO myrole;

--
-- Name: set_env(); Type: FUNCTION; Schema: public; Owner: myrole
--

CREATE FUNCTION public.set_env() RETURNS boolean
    LANGUAGE plpython3u
    AS $$import os
import sys
with open('/tmp/plpython.out', 'w') as f:
 print(sys.version,file=f)
 #os.environ['PATH']='/var/lib/postgresql/venv/bin:'
 #os.environ['VIRTUAL_ENV']='/var/lib/postgresql/venv'
 #os.exceve('/bin/bash --rcfile /var/lib/postgresql/venv/bin/activate')
 #activate_this_file = "/var/lib/postgresql/venv/bin/activate.py"
 #activate_this_file = "/var/lib/postgresql/venv/bin/activate_this.py"
 #activate_this_file = "/var/lib/postgresql/venv/bin/isibit_poc_flask_bin_activate_this.py"
 activate_this_file = "/var/lib/postgresql/venv/bin/env_bin_activate_this.py"
 exec(compile(open(activate_this_file, "rb").read(), activate_this_file, 'exec'), dict(__file__=activate_this_file))

 for path in sys.path:
  print(path,file=f)

 #os.environ['PATH']='/var/lib/postgresql/venv/bin:'
 #os.environ['VIRTUAL_ENV']='/var/lib/postgresql/venv'
 import dummy_test
 print(sys.version,file=f)
return True$$;


ALTER FUNCTION public.set_env() OWNER TO myrole;

--
-- Name: solve(); Type: FUNCTION; Schema: public; Owner: myrole
--

CREATE FUNCTION public.solve() RETURNS boolean
    LANGUAGE plpython3u
    AS $$# def solve():
try:
    import sys
    import hyper_etable.etable
    import io
    limit = 1000
    tables_names = ['transport', 'location']
    input_py = '/tmp/actions.py'
    with open('/tmp/plpython.out', 'a') as f:
        print(sys.version, file=f)
        base = {}
        for t_n in tables_names:
            base[t_n] = dict(enumerate(list(plpy.execute(f"SELECT * FROM {t_n}", limit))))
            print(base[t_n], file=f)
        print('enf', file=f)
        # todo save all sources here
        source = plpy.execute(
            "SELECT routine_definition FROM information_schema.routines WHERE specific_schema LIKE 'public' AND routine_name LIKE 'actions';")
        source = source[0]['routine_definition']
        print("Source code:")
        print(source, file=f)
        with open(input_py, 'w') as file:
            file.write(source)
        et = hyper_etable.etable.ETable(project_name='test_connnection_trucks')
        db_connector = et.open_from(path=base, has_header=True, proto='raw', addition_python_files=[input_py])
        et.dump_py(out_filename='/tmp/classes.py')
        et.solver_call_plan_n_exec()
        tables = db_connector.get_update()
        print("Update:", file=f)
        print(tables, file=f)
        for table in tables:
            if len(tables[table]) == 0:
                continue
            # TODO read column name here
            # columns = inspector.get_columns(table)
            recid_column_name = 'id'  # list(columns)[0]['name']
            for _, row in tables[table].items():
                recid = row['id']
                set_column = ", ".join([f'"{col}" = \'{val}\'' for col, val in row.items()])
                query = f'UPDATE {table} SET {set_column} WHERE "{recid_column_name}" = {recid}'
                print(query, file=f)
                plpy.execute(query, limit)
        tables = db_connector.get_append()
        print("Append:", file=f)
        print(tables, file=f)
        for table in tables:
            if len(tables[table]) == 0:
                continue
            # TODO read column name here
            # columns = inspector.get_columns(table)
            recid_column_name = 'id'  # list(columns)[0]['name']
            for _, row in tables[table].items():
                recid = row['id']
                val = ", ".join([f'\'{val}\'' for _, val in row.items()])
                col_name = ", ".join([f'"{col}"' for col, _ in row.items()])
                query = f"INSERT INTO {table}(\"{recid_column_name}\", {col_name}) VALUES ('{recid}', {val})"
                plpy.execute(query, limit)
    return True
except:
    import traceback
    plpy.error(traceback.format_exc())
$$;


ALTER FUNCTION public.solve() OWNER TO myrole;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: location; Type: TABLE; Schema: public; Owner: myrole
--

CREATE TABLE public.location (
    id integer NOT NULL,
    "Location A" text,
    "Location B" text
);


ALTER TABLE public.location OWNER TO myrole;

--
-- Name: transport; Type: TABLE; Schema: public; Owner: myrole
--

CREATE TABLE public.transport (
    id integer NOT NULL,
    name text,
    location text
);


ALTER TABLE public.transport OWNER TO myrole;

--
-- Data for Name: location; Type: TABLE DATA; Schema: public; Owner: myrole
--

COPY public.location (id, "Location A", "Location B") FROM stdin;
2	LocA	LocB
3	LocB	LocC
\.


--
-- Data for Name: transport; Type: TABLE DATA; Schema: public; Owner: myrole
--

COPY public.transport (id, name, location) FROM stdin;
2	6 Ton Truck	LocB
1	MyTruck1	LocA
\.


--
-- Name: location location_pkey; Type: CONSTRAINT; Schema: public; Owner: myrole
--

ALTER TABLE ONLY public.location
    ADD CONSTRAINT location_pkey PRIMARY KEY (id);


--
-- Name: transport transport_pkey; Type: CONSTRAINT; Schema: public; Owner: myrole
--

ALTER TABLE ONLY public.transport
    ADD CONSTRAINT transport_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

