ALTER USER postgres WITH PASSWORD '4815162342';

CREATE TABLESPACE admin_bot_tbs LOCATION '/db';

CREATE DATABASE admin_bot WITH OWNER = 'postgres' TABLESPACE = 'admin_bot_tbs';

