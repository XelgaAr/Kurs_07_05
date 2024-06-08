import os

from flask import Flask, request, render_template, session, redirect
from functools import wraps
from utils import SQLiteDatabase

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET_KEY")


def check_credentials(username, password):
    with SQLiteDatabase('db.db') as db:
        user = db.fetch('user', {'login': username, 'password': password}, fetch_all=False)
    return user is not None


def login_required(func):
    @wraps(func)
    def wr1(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        results = func(*args, **kwargs)
        return results

    return wr1


@app.route('/', methods=['GET'])
def index():
    return 'Welcome to homepage!'


@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch('user')
        return res
    if request.method == 'POST':
        return f'input user info'
    if request.method == 'PUT':
        return f'change user info'


@app.route('/user/<user_id>', methods=['GET', 'POST'])
@login_required
def user_info(user_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch("user", f'id={user_id}', ["login", "phone", "birth_date", "funds"],
                           fetch_all=False)
        return render_template('user_info.html', user_info=res)

    if request.method == 'POST':
        return f'add funds'


@app.route('/user/<user_id>/funds', methods=['GET', 'POST'])
@login_required
def user_funds(user_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch('user', {'id': user_id})
        return render_template('funds.html', funds=res)

    if request.method == 'POST':
        return f'add funds'


@app.route('/user/reservations', methods=['GET', 'POST'])
@login_required
def user_reservations():
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch('reservations')
        return res
    if request.method == 'POST':
        return f'create reservations'


@app.route('/user/reservations/<reservation_id>', methods=['GET', 'POST'])
@login_required
def user_reservations_id(reservation_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch('reservation', {'id': reservation_id}, fetch_all=False)
        return res

    if request.method == 'POST':
        return f'create reservation with id: {reservation_id}'


@app.route('/user/reservations/<reservation_id>/delete', methods=['GET'])
@login_required
def user_reservations_delete(reservation_id):
    return 0


@app.route('/user/checkout', methods=['GET', 'POST', 'PUT'])
@login_required
def user_checkout():
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch('checkout')
        return res
    if request.method == 'POST':
        return f'create user checkout'
    if request.method == 'PUT':
        return f'change user checkout '


@app.route('/fitness_center', methods=['GET'])
def fitness_center():
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch('fitness_center')
        return res


@app.route('/fitness_center/<fitness_center_id>', methods=['GET'])
def fitness_center_id(fitness_center_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch('fitness_center', {'id': fitness_center_id}, fetch_all=False)
        return res


@app.route('/fitness_center/<fitness_center_id>/trainer', methods=['GET'])
def fitness_center_trainer(fitness_center_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch('trainer', {'id': fitness_center_id})
        return res


@app.route('/fitness_center/<fitness_center_id>/trainer/<trainer_id>', methods=['GET'])
def fitness_center_trainer_id(fitness_center_id, trainer_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch('trainer', {'fitness_center_id': fitness_center_id, 'id': trainer_id}, fetch_all=False)
        return res


@app.route('/trainer/<trainer_id>/rating', methods=['GET', 'POST'])
@login_required
def fitness_center_trainer_id_rating(trainer_id):
    if request.method == 'GET':
        return render_template('rating.html')
    if request.method == 'POST':
        form_data = request.form
        with SQLiteDatabase('db.db') as db:
            user_found = db.fetch('user', {'login': form_data['login'], 'password': form_data['password']},
                                  fetch_all=False)
            db.insert("rating", {'user_id': user_found['id'],
                                 'points': form_data['points'], 'text': form_data['text'],
                                 'trainer_id': form_data['trainer_id']})
        return f'created rating trainer with id:{trainer_id}'


@app.route('/fitness_center/<fitness_center_id>/services', methods=['GET'])
def fitness_center_services(fitness_center_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            info = db.fetch('service', {'fitness_center_id': fitness_center_id})
        return f'Info about services in fitness center with id :{fitness_center_id}:<br>{info}'


@app.route('/login', methods=['GET', 'POST'])
def get_login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        if check_credentials(login, password):
            with SQLiteDatabase('db.db') as db:
                user = db.fetch("user", {'login': login}, fetch_all=False)
                session['user_id'] = user['id']
            return redirect(f'/user/{user['id']}')
        else:
            return 'Incorrect login or password'


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    session.pop('user_id', None)
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        form_data = request.form
        with SQLiteDatabase('db.db') as db:
            db.insert("user", {'login': form_data['login'], 'password': form_data['password'],
                               'birth_date': form_data['birth_date'], 'phone': form_data['phone']})
        return f'you are registered'


@app.route('/user/<user_id>/resources', methods=['GET'])
def user_resources(user_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch('resources', {'user_id': user_id})
        return res or 'No info about current user resources'
