-- evento_fogo.focos_bdq_c2 definition

-- Drop table

-- DROP TABLE evento_fogo.focos_bdq_c2;

CREATE TABLE evento_fogo.focos_bdq_c2 (
	id_foco_bdq int8 NOT NULL,
	data_hora_gmt timestamp NOT NULL,
	longitude float8 NOT NULL,
	latitude float8 NOT NULL,
	satelite varchar(100) NOT NULL,
	confidence int4 NULL,
	geometria public.geometry(point, 4326) NOT NULL,
	collection varchar(100) NULL,
	eh_satelite_referencia bool DEFAULT false NOT NULL,
	id_0 int4 NULL,
	id_1 int4 NULL,
	id_2 int4 NULL,
	pais varchar(100) NULL,
	estado varchar(100) NULL,
	municipio varchar(100) NULL,
	bioma varchar(100) NULL,
	grade_wrs varchar(7) NULL,
	id_area_industrial int4 DEFAULT 0 NULL,
	am_pm bpchar(2) NULL,
	municipio_id int4 NULL,
	pais_id int4 NULL,
	estado_id int4 NULL,
	frp float8 NULL,
	precipitacao float8 NULL,
	numero_dias_sem_chuva int4 NULL,
	risco_fogo float8 NULL,
	vegetacao varchar(256) NULL,
	log_importacoes_id int4 NULL,
	continente_id int4 NULL,
	inserido_em timestamp DEFAULT now() NULL,
	atualizado_em timestamp NULL,
	removido_em timestamp NULL,
	id_importacao_bdq int4 NULL,
	numero int4 NULL,
	id_tipo_area_industrial int4 DEFAULT 0 NULL,
	id_regiao_especial _int4 NULL,
	path_row varchar(8) NULL,
	foco_id uuid DEFAULT uuid_generate_v1() NOT NULL,
	veg int4 NULL,
	"INSERT INTO evento_fogo.focos_bdq_c2 (data_hora_gmt" varchar(64) NULL,
	"veg) VALUES" varchar(50) NULL,
	desmatamento bool NULL,
	CONSTRAINT focos_bdq_c2_pkey PRIMARY KEY (id_foco_bdq),
	CONSTRAINT focos_bdq_c2_unique_foco_id UNIQUE (foco_id)
);
CREATE INDEX focobdqc2dataindex ON evento_fogo.focos_bdq_c2 USING btree (data_hora_gmt);
CREATE INDEX focos_geom_idx ON evento_fogo.focos_bdq_c2 USING gist (geometria);


-- evento_fogo.satelite definition

-- Drop table

-- DROP TABLE evento_fogo.satelite;

CREATE TABLE evento_fogo.satelite (
	id_sat int4 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	sat_nome text NOT NULL,
	CONSTRAINT sat_pk PRIMARY KEY (id_sat)
);


-- evento_fogo.status_evento definition

-- Drop table

-- DROP TABLE evento_fogo.status_evento;

CREATE TABLE evento_fogo.status_evento (
	id_status int4 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	status_nome text NOT NULL,
	CONSTRAINT status_evento_pk PRIMARY KEY (id_status)
);


-- evento_fogo.tipo_fogo definition

-- Drop table

-- DROP TABLE evento_fogo.tipo_fogo;

CREATE TABLE evento_fogo.tipo_fogo (
	id_tipo int4 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	tipo_nome text NOT NULL,
	CONSTRAINT tipo_pk PRIMARY KEY (id_tipo)
);


-- evento_fogo.tipo_regiao definition

-- Drop table

-- DROP TABLE evento_fogo.tipo_regiao;

CREATE TABLE evento_fogo.tipo_regiao (
	id_tipo_reg int4 NOT NULL,
	tipo_nome varchar NULL,
	CONSTRAINT tipo_regiao_pkey PRIMARY KEY (id_tipo_reg)
);


-- evento_fogo.evento_fogo definition

-- Drop table

-- DROP TABLE evento_fogo.evento_fogo;

CREATE TABLE evento_fogo.evento_fogo (
	id_evento serial4 NOT NULL,
	qtd_frente int4 NULL,
	duracao interval NULL,
	data_min timestamp NULL,
	data_max timestamp NULL,
	max_frp float4 NULL,
	risco_medio float4 NULL,
	max_dias_sem_chuva int4 NULL,
	area_acm float4 NULL,
	geom public.geometry(multipolygon, 4326) NULL,
	id_status int4 DEFAULT 1 NOT NULL,
	id_tipo int4 NULL,
	CONSTRAINT evento_fogo_pk PRIMARY KEY (id_evento),
	CONSTRAINT evento_fogo_status_evento_fk FOREIGN KEY (id_status) REFERENCES evento_fogo.status_evento(id_status)
);
CREATE INDEX evento_fogo_data_max_idx ON evento_fogo.evento_fogo USING btree (data_max);
CREATE INDEX evento_fogo_data_min_idx ON evento_fogo.evento_fogo USING btree (data_min);
CREATE INDEX idx_evento_fogo_id ON evento_fogo.evento_fogo USING btree (id_evento);
CREATE INDEX idx_evento_geom ON evento_fogo.evento_fogo USING gist (geom);


-- evento_fogo.evento_tipo_fogo definition

-- Drop table

-- DROP TABLE evento_fogo.evento_tipo_fogo;

CREATE TABLE evento_fogo.evento_tipo_fogo (
	id_evento int4 NOT NULL,
	id_tipo int4 NULL,
	CONSTRAINT evento_tipo_fogo_pkey PRIMARY KEY (id_evento),
	CONSTRAINT evento_tipo_fogo_evento_fogo_fk FOREIGN KEY (id_evento) REFERENCES evento_fogo.evento_fogo(id_evento),
	CONSTRAINT evento_tipo_fogo_tipo_fogo_fk FOREIGN KEY (id_tipo) REFERENCES evento_fogo.tipo_fogo(id_tipo)
);


-- evento_fogo.frente_fogo definition

-- Drop table

-- DROP TABLE evento_fogo.frente_fogo;

CREATE TABLE evento_fogo.frente_fogo (
	id_frente serial4 NOT NULL,
	qtd_focos int4 NULL,
	data_frente timestamp NULL,
	max_frp float4 NULL,
	risco_medio float4 NULL,
	max_dias_sem_chuva int4 NULL,
	delta_area float4 NULL,
	geom public.geometry(multipolygon, 4326) NULL,
	id_evento int4 NULL,
	media_precipitacao float4 NULL,
	CONSTRAINT id_frente_pk PRIMARY KEY (id_frente),
	CONSTRAINT frente_fogo_evento_fogo_fk FOREIGN KEY (id_evento) REFERENCES evento_fogo.evento_fogo(id_evento)
);
CREATE INDEX idx_frente_fogo_data ON evento_fogo.frente_fogo USING btree (data_frente);
CREATE INDEX idx_frente_fogo_geom ON evento_fogo.frente_fogo USING gist (geom);
CREATE INDEX idx_frente_fogo_id ON evento_fogo.frente_fogo USING btree (id_evento);
CREATE INDEX idx_frente_fogo_id_evento ON evento_fogo.frente_fogo USING btree (id_evento);


-- evento_fogo.frente_satelite definition

-- Drop table

-- DROP TABLE evento_fogo.frente_satelite;

CREATE TABLE evento_fogo.frente_satelite (
	id_frente int4 NOT NULL,
	id_sat int4 NOT NULL,
	CONSTRAINT pk_frente_satelite PRIMARY KEY (id_frente, id_sat),
	CONSTRAINT frente_satelite_frente_fogo_fk FOREIGN KEY (id_frente) REFERENCES evento_fogo.frente_fogo(id_frente),
	CONSTRAINT frente_satelite_satelite_fk FOREIGN KEY (id_sat) REFERENCES evento_fogo.satelite(id_sat)
);


-- evento_fogo.regiao definition

-- Drop table

-- DROP TABLE evento_fogo.regiao;

CREATE TABLE evento_fogo.regiao (
	id_regiao int4 DEFAULT nextval('descreve_regiao.regiao2_id_regiao_seq'::regclass) NOT NULL,
	nome_regiao text NOT NULL,
	geom public.geometry NULL,
	id_tipo_reg int4 NULL,
	CONSTRAINT regiao_pkey PRIMARY KEY (id_regiao),
	CONSTRAINT fk_regiao_tipo FOREIGN KEY (id_tipo_reg) REFERENCES evento_fogo.tipo_regiao(id_tipo_reg)
);
CREATE INDEX regiao_geom_idx ON evento_fogo.regiao USING gist (geom);
CREATE INDEX regiao_left_idx ON evento_fogo.regiao USING btree ("left"(nome_regiao, 100));
CREATE INDEX regiao_md5_idx ON evento_fogo.regiao USING hash (md5(nome_regiao));


-- evento_fogo.evento_regiao definition

-- Drop table

-- DROP TABLE evento_fogo.evento_regiao;

CREATE TABLE evento_fogo.evento_regiao (
	id_evento int4 NOT NULL,
	id_regiao int4 NOT NULL,
	CONSTRAINT pk_evento_regiao PRIMARY KEY (id_evento, id_regiao),
	CONSTRAINT evento_regiao_evento_fogo_fk FOREIGN KEY (id_evento) REFERENCES evento_fogo.evento_fogo(id_evento),
	CONSTRAINT evento_regiao_regiao_fk FOREIGN KEY (id_regiao) REFERENCES evento_fogo.regiao(id_regiao)
);