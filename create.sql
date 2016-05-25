-- Table: abc

-- DROP TABLE abc;

CREATE TABLE abc
(
  key serial NOT NULL,
  slovo text,
  ch_g integer,
  ch_s integer,
  CONSTRAINT abc_pkey PRIMARY KEY (key)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE abc
  OWNER TO postgres;
 
