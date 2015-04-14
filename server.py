import csv
from pathlib import Path
import sqlite3
from bottle import Bottle, jinja2_view, run, abort, static_file

app = Bottle()
_create_db_tables_sql = '''\
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
'''

_create_db_view_sql = '''\
    CREATE VIEW committee AS
    SELECT
        t.name AS teacher, t.id AS t_id,
        c.name AS committee, c.id AS c_id,
        c.level AS committee_level, cl.year AS year
    FROM teachers AS t, comm_names AS c, comm_list AS cl
    WHERE t.id == cl.teacher_id AND c.id == cl.comm_id;
'''


def int_csv_reader(csv_pth, int_fields=None):
    with open(csv_pth) as f:
        reader = csv.reader(f)
        for row in reader:
            converted_row = [
                int(v) if i in int_fields else v for i, v in enumerate(row)
            ]
            yield converted_row


@app.route('/', method='POST')
def reload_db():
    # if database does not exist, create a new one without renaming.
    # otherwise move the original databse as xxx.prev
    try:
        Path('comm.db').rename('comm.db.prev')
        db_existed = True
    except FileNotFoundError:
        db_existed = False
    # recreate the database. If any move fails, move back the original databse.
    try:
        conn = sqlite3.connect('comm.db')
        conn.executescript(_create_db_tables_sql)
        conn.executescript(_create_db_view_sql)
        conn.executemany(
            'INSERT INTO teachers VALUES (?, ?, ?)',
            int_csv_reader('raw_export/teacher.headless', [0])
        )
        conn.executemany(
            'INSERT INTO comm_names VALUES (?, ?, ?)',
            int_csv_reader('raw_export/comm_name.headless', [0])
        )
        conn.executemany(
            'INSERT INTO comm_list VALUES (?, ?, ?)',
            int_csv_reader('raw_export/comm_list.headless', [0, 1])
        )
        conn.commit()
    except Exception as e:
        if db_existed:
            Path('comm.db.prev').rename('comm.db')
        abort(500, 'Database reload FAILED with following error:\n' + repr(e))
    else:
        if db_existed:
            Path('comm.db.prev').unlink()
        return index(msg='Successfully reload!')


# @app.route('/teacher/', method='POST')
# def teacher():
#     redirect('/teacher/{}/'.format(request.forms.get('teacherName')))


def connect_db():
    conn = sqlite3.connect('comm.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/', method='GET')
@jinja2_view('index.html', template_lookup=['templates'])
def index(msg=''):
    return {'msg': msg}


@app.route('/teacher/<id>/')
@jinja2_view('teacher.html', template_lookup=['templates'])
def teacher(id):
    conn = connect_db()
    name = conn.execute(
        'SELECT name FROM teachers WHERE id = ?', (id,)
    ).fetchone()[0]
    records = conn.execute(
        'SELECT * FROM committee WHERE teacher = ? ORDER BY year DESC', (name,)
    ).fetchall()
    if records:
        return {'name': name, 'records': records}
    else:
        abort(404, 'Teacher {} no record'.format(name))


@app.route('/committee/<id>/')
@jinja2_view('committee.html', template_lookup=['templates'])
def committee(id):
    conn = connect_db()
    name, level = conn.execute(
        'SELECT name, level FROM comm_names WHERE id = ?', (id,)
    ).fetchone()
    records = conn.execute(
        'SELECT * FROM committee WHERE committee = ? '
        'ORDER BY year DESC', (name,)
    ).fetchall()
    return {'name': name, 'level': level, 'records': records}


@app.route('/search/')
@jinja2_view('search.html', template_lookup=['templates'])
def search():
    conn = connect_db()
    teachers = conn.execute('SELECT id, name FROM teachers').fetchall()
    school_committees = conn.execute(
        "SELECT id, name FROM comm_names WHERE level = '校'"
    ).fetchall()
    disp_committees = conn.execute(
        "SELECT id, name FROM comm_names WHERE level = '院'"
    ).fetchall()
    return {
        'teachers': teachers,
        'school_committees': school_committees,
        'disp_committees': disp_committees,
    }


@app.route('/static/<path:path>')
def callback(path):
    return static_file(path, './static')

run(app, host='localhost', port=8080, debug=True, reloader=True)