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
    with open(csv_pth, encoding='utf8') as f:
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
            int_csv_reader('raw_export/teacher.txt', [0])
        )
        conn.executemany(
            'INSERT INTO comm_names VALUES (?, ?, ?)',
            int_csv_reader('raw_export/comm_name.txt', [0])
        )
        conn.executemany(
            'INSERT INTO comm_list VALUES (?, ?, ?)',
            int_csv_reader('raw_export/comm_list.txt', [0, 1])
        )
        conn.commit()
    except Exception as e:
        conn.close()
        if db_existed:
            Path('comm.db').unlink()
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


@app.route('/teacher/<t_id>/')
@jinja2_view('teacher.html', template_lookup=['templates'])
def teacher(t_id):
    conn = connect_db()
    records = conn.execute(
        'SELECT * FROM committee WHERE t_id = ? ORDER BY year DESC', (t_id,)
    ).fetchall()
    if not records:
        abort(404, 'Teacher ID %s not exists or no record found.' % t_id)
    try:
        name = records[0]['teacher']
        return {'name': name, 'records': records}
    except Exception as e:
        abort(500,
              'Teacher %s record loading failed with error:\n%r' % (t_id, e))


@app.route('/teacher/<t_id>/filter-year/<s_yr>/<e_yr>/')
@jinja2_view('teacher.html', template_lookup=['templates'])
def teacher_year_filter(t_id, s_yr, e_yr):
    conn = connect_db()
    records = conn.execute(
        'SELECT * FROM committee '
        'WHERE t_id = ? AND year BETWEEN ? AND ?'
        'ORDER BY year DESC', (t_id, s_yr, e_yr)
    ).fetchall()
    if not records:
        abort(404, 'Teacher ID %s not exists or no record found.' % t_id)
    try:
        name = records[0]['teacher']
        return {
            'name': name, 'records': records, 't_id': t_id,
            'start_year': s_yr, 'end_year': e_yr,
        }
    except Exception as e:
        abort(500,
              'Teacher %s record loading failed with error:\n%r' % (t_id, e))


@app.route('/committee/<c_id>/')
@jinja2_view('committee.html', template_lookup=['templates'])
def committee(c_id):
    conn = connect_db()
    records = conn.execute(
        'SELECT * FROM committee WHERE c_id = ? '
        'ORDER BY year DESC', (c_id,)
    ).fetchall()
    if not records:
        abort(404, 'Committee ID %s not exists or no record found.' % c_id)
    try:
        rec = records[0]
        name, level = rec['committee'], rec['committee_level']
        return {'name': name, 'level': level, 'records': records}
    except Exception as e:
        abort(500,
              'Committee %s record loading failed with error:\n%r' % (c_id, e))

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


@app.route('/tutorial/')
@jinja2_view('tutorial.html', template_lookup=['templates'])
def tutorial():
    return {}


@app.route('/static/<path:path>')
def callback(path):
    return static_file(path, './static')


if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True, reloader=True)
