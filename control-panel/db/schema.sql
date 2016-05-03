drop table if exists settings;
create table settings(
	id integer primary key,
	name varchar(255),
	temp_status float(3),
	temp_target float(3),
	temp_max float(3),
	enable boolean
);
