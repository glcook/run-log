from flask import Flask, session, render_template, request, redirect, url_for, g
import os
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helper_funcs import null_to_zero, time_to_string, time_to_pace, secs_to_hms

app = Flask(__name__)
app.secret_key = os.urandom(24)

os.environ['DATABASE_URL'] = 'postgres://bkcowuzjoysdqm:1485ff603f38a51999a4727ade2323bddff44d705f850c87b8c11dedaf61aea8@ec2-54-225-68-133.compute-1.amazonaws.com:5432/dfiobqn6g2jv5b'
engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind=engine))


@app.route('/')
def index():
    if 'user' in session:
        un = session['user']
        result1 = db.execute(
            f"SELECT id, first_name FROM users WHERE username = '{un}'").fetchone()
        uid = result1[0]
        name = result1[1]

        result2 = db.execute(
            f"SELECT date, dist, dur_secs FROM runs WHERE user_id = '{uid}' ORDER BY date DESC LIMIT 3").fetchall()
        recent_runs = []
        for row in result2:
            time = time_to_string(row[2])
            recent_runs.append([row[0], row[1], time])

        result3 = db.execute(
            f"SELECT AVG(dist) FROM runs WHERE user_id = '{uid}' AND date >= current_date - interval '30 day'").fetchone()
        avg_dist = result3[0]

        if avg_dist is None:
            avg_dist = 'NA'
        else:
            avg_dist = str(round(avg_dist, 1)) + ' miles'

        result4 = db.execute(
            f"SELECT SUM(dist), SUM(dur_secs) FROM runs WHERE user_id = '{uid}' AND dur_secs > 0 AND date >= current_date - interval '30 day'").fetchone()
        avg_pace = ''

        if result4[0] is None or result4[1] is None:
            avg_pace = 'NA'

        else:
            avg_pace = time_to_pace(
                result4[1] / result4[0]) + " minutes per mile"

        return(render_template('index.html', name=name, runs=recent_runs, avg_dist=avg_dist, avg_pace=avg_pace))

    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first = request.form['firstname']
        last = request.form['lastname']
        un = request.form['username']
        pw = generate_password_hash(request.form['password'])

        db.execute("INSERT INTO users (first_name, last_name, username, password) VALUES \
            (:first_name, :last_name, :user_name, :password)", {"first_name": first,
                                                                "last_name": last, "user_name": un, "password": pw})
        db.commit()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user', None)

        un_entered = request.form['username']
        pw_entered = request.form['password']

        retrieved = db.execute(
            f"SELECT first_name, username, password FROM users WHERE username = '{un_entered}'").fetchone()

        if retrieved is None:
            message = 'No such user.'
            return render_template('message.html', message=message)

        elif check_password_hash(retrieved[2], pw_entered):
            session['user'] = un_entered
            name = retrieved[0]

            return redirect(url_for('index'))

        else:
            message = 'Incorrect password.'
            return render_template('message.html', message=message)

    return render_template('login.html')


@app.route('/log_run', methods=['GET', 'POST'])
def log_run():
    if 'user' in session:
        if request.method == 'POST':
            date = request.form['date']
            distance = request.form['distance']
            hours = null_to_zero(request.form['hours'])
            minutes = null_to_zero(request.form['minutes'])
            seconds = null_to_zero(request.form['seconds'])

            if distance in (None, 0, ""):
                message = "Please enter a valid distance."
                return render_template('message.html', message=message)
            else:

                total_duration_seconds = (
                    hours * 60 * 60) + (minutes * 60) + seconds

                un = session['user']
                result = db.execute(
                    f"SELECT id FROM users WHERE username = '{un}'").fetchone()
                uid = result[0]

                db.execute("INSERT INTO runs (user_id, date, dist, dur_secs) \
                    VALUES (:user_id, :date, :dist, :dur_secs)",
                           {"user_id": uid, "date": date, "dist": distance, "dur_secs": total_duration_seconds})
                db.commit()
                return redirect(url_for('index'))

        return render_template('log_run.html')

    return redirect(url_for('login'))


@app.route('/all_runs')
def all_runs():
    if 'user' in session:
        un = session['user']
        result1 = db.execute(
            f"SELECT id FROM users WHERE username = '{un}'").fetchone()
        uid = result1[0]

        result2 = db.execute(
            f"SELECT id, date, dist, dur_secs FROM runs WHERE user_id = '{uid}' ORDER BY date DESC").fetchall()
        runs = []

        for row in result2:
            if row[2] > 0:
                time = time_to_string(row[3])
                pace = time_to_pace(row[3] / row[2])
                dist = str(round(row[2], 1)) + " miles"
            runs.append([row[0], row[1], dist, time, pace])

        return render_template('all_runs.html', runs=runs)

    return redirect(url_for('login'))


@app.route('/edit_run/<id>', methods=['GET', 'POST'])
def edit(id):
    if 'user' in session:
        if request.method == 'GET':
            run_data = db.execute(
                f"SELECT id, date, dist, dur_secs FROM runs  WHERE id = '{id}'").fetchone()
            hms = secs_to_hms(run_data[3])
            run = [run_data[0], run_data[1],
                   run_data[2], hms[0], hms[1], hms[2]]

            return render_template('edit_run.html', run=run)

        elif request.method == 'POST':
            date = request.form['date']
            distance = request.form['distance']
            hours = null_to_zero(request.form['hours'])
            minutes = null_to_zero(request.form['minutes'])
            seconds = null_to_zero(request.form['seconds'])

            if distance in (None, 0, ""):
                message = "Please enter a valid distance."
                return render_template('message.html', message=message)
            else:
                total_duration_seconds = (
                    hours * 60 * 60) + (minutes * 60) + seconds
                db.execute(
                    f"UPDATE runs SET date = '{date}', dist = '{distance}', dur_secs = '{total_duration_seconds}' WHERE id = '{id}'")
                db.commit()

                message = "Run has been updated."
                return render_template('message.html', message=message)

    return redirect(url_for('login'))


@app.route('/delete/<id>')
def delete(id):
    if 'user' in session:
        db.execute(f"DELETE FROM runs WHERE id = '{id}'")
        db.commit()

        message = "Run has been deleted."

        return render_template('message.html', message=message)

    return redirect(url_for('login'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    message = "You have logged out."
    return render_template('message.html', message=message)


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']
