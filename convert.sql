CREATE TABLE comm_names (
    id INTEGER PRIMARY KEY ASC,
    name TEXT,
    level TEXT
);

CREATE TABLE teachers (
    id INTEGER PRIMARY KEY ASC,
    name TEXT,
    student TEXT
);

CREATE TABLE comm_list (
    comm_id     INTEGER,
    teacher_id  INTEGER,
    year        INTEGER,
    FOREIGN KEY(comm_id) REFERENCES comm_names(id),
    FOREIGN KEY(teacher_id) REFERENCES teachers(id)
);

.mode csv
.import raw_export/comm_name.headless comm_names
.import raw_export/teacher.headless teachers
.import raw_export/comm_list.headless comm_list

CREATE VIEW committee AS
    SELECT t.name AS teacher, c.name AS committee, c.level AS committee_level, cl.year AS year
    FROM teachers AS t, comm_names AS c, comm_list AS cl
    WHERE t.id == cl.teacher_id AND c.id == cl.comm_id;
