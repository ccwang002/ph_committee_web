from bottle import Bottle, jinja2_view, run, abort
import sqlite3

app = Bottle()
conn = sqlite3.connect('comm.db')
conn.row_factory = sqlite3.Row

@app.route('/')
@jinja2_view('index.html', template_lookup=['templates'])
def index():
    return {}


# @app.route('/teacher/', method='POST')
# def teacher():
#     redirect('/teacher/{}/'.format(request.forms.get('teacherName')))


@app.route('/teacher/<id>/')
@jinja2_view('teacher.html', template_lookup=['templates'])
def teacher(id):
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

run(app, host='localhost', port=8080, debug=True, reloader=True)
