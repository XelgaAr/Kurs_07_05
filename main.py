import os

from flask import Flask, request, render_template, session, redirect
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET_KEY")


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_from_db(query, many=True):
    con = sqlite3.connect('db.db')
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute(query)
    if many:
        res = cur.fetchall()
    else:
        res = cur.fetchone()
    con.close()
    return res


def insert_into_db(query):
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()


class SQLiteDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = dict_factory
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

    def fetch_all(self, table, condition=None, join_table=None, join_condition=None, single=False):
        query = f"SELECT * FROM {table}"
        conditions = []

        if join_table is not None:
            join_cond_list = []
            for key, val in join_condition.items():
                join_cond_list.append(f" {key}='{val}' ")
            join_cond_str = ' and '.join(join_cond_list)
            join_str = f' join {join_table} ON {join_cond_str} '
            query = query + join_str

        if condition is not None:
            for key, val in condition.items():
                conditions.append(f" {key}='{val}' ")
            str_conditions = ' and '.join(conditions)
            str_conditions = ' where ' + str_conditions
            query = query + str_conditions

        print(query)

        cursor = self.connection.cursor()
        cursor.execute(query)
        if single:
            res = cursor.fetchone()
        else:
            res = cursor.fetchall()
        if res:
            return res
        return None

    def fetch_one_query(self, query, *args, **kwargs):
        cursor = self.connection.cursor()
        cursor.execute(query, *args, **kwargs)
        res = cursor.fetchone()
        if res:
            return res
        return None

    def fetch_one(self, table, condition=None, join_table=None, join_condition=None):
        return self.fetch_all(table, condition, join_table, join_condition, single=True)

    def insert(self, table, data):
        keys = []
        vals = []
        for key, value in data.items():
            keys.append(key)
            vals.append("'" + str(value) + "'")
        str_keys = ', '.join(keys)
        str_vals = ', '.join(vals)
        query = f"""INSERT INTO {table} ({str_keys}) VALUES ({str_vals}) """
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()

def check_credentials(username, password):
    with SQLiteDatabase('db.db') as db:
        user = db.fetch_one('user', {'login': username, 'password': password})
    return user is not None


def logion_required(func):
    @wraps(func)
    def wr1(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        results = func(*args, **kwargs)
        return results

    return wr1


app.route('/', methods=['GET'])


def index():
    return 'Welcome to homepage!'


@app.route('/user', methods=['GET', 'POST'])
@logion_required
def user():
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_all('user')
        return res
    if request.method == 'POST':
        return f'input user info'
    if request.method == 'PUT':
        return f'change user info'


@app.route('/user/<user_id>', methods=['GET', 'POST'])
@logion_required
def user_info(user_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_one_query(f'SELECT login, phone, birth_date, funds FROM user WHERE id={user_id}')
        return render_template('user_info.html', user_info=res)

    if request.method == 'POST':
        return f'add funds'


@app.route('/user/<user_id>/funds', methods=['GET', 'POST'])
@logion_required
def user_funds(user_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_all('user', {'id': user_id})
        return render_template('funds.html', funds=res)

    if request.method == 'POST':
        return f'add funds'


@app.route('/user/reservations', methods=['GET', 'POST'])
@logion_required
def user_reservations():
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_all('reservations')
        return res
    if request.method == 'POST':
        return f'create reservations'


@app.route('/user/reservations/<reservation_id>', methods=['GET', 'POST'])
@logion_required
def user_reservations_id(reservation_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_one('reservation', {'id': reservation_id})
        return res

    if request.method == 'POST':
        return f'create reservation with id: {reservation_id}'


@app.route('/user/reservations/<reservation_id>/delete', methods=['GET'])
@logion_required
def user_reservations_delete(reservation_id):
    return 0


@app.route('/user/checkout', methods=['GET', 'POST', 'PUT'])
@logion_required
def user_checkout():
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_all('checkout')
        return res
    if request.method == 'POST':
        return f'create user checkout'
    if request.method == 'PUT':
        return f'change user checkout '


@app.route('/fitness_center', methods=['GET'])
def fitness_center():
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_all('fitness_center')
        return res


@app.route('/fitness_center/<fitness_center_id>', methods=['GET'])
def fitness_center_id(fitness_center_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_one('fitness_center', {'id': fitness_center_id})
        return res


@app.route('/fitness_center/<fitness_center_id>/trainer', methods=['GET'])
def fitness_center_trainer(fitness_center_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_all('trainer', {'id': fitness_center_id})
        return res


@app.route('/fitness_center/<fitness_center_id>/trainer/<trainer_id>', methods=['GET'])
def fitness_center_trainer_id(fitness_center_id, trainer_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_one('trainer', {'fitness_center_id': fitness_center_id, 'id': trainer_id})
        return res


@app.route('/trainer/<trainer_id>/rating', methods=['GET', 'POST'])
@logion_required
def fitness_center_trainer_id_rating(trainer_id):
    if request.method == 'GET':
        return render_template('rating.html')
    if request.method == 'POST':
        form_data = request.form
        with SQLiteDatabase('db.db') as db:
            user_found = db.fetch_one('user', {'login': form_data['login'], 'password': form_data['password']})
            db.insert("rating", {'user_id': user_found['id'],
                                 'points': form_data['points'], 'text': form_data['text'],
                                 'trainer_id': form_data['trainer_id']})
        return f'created rating trainer with id:{trainer_id}'


@app.route('/fitness_center/<fitness_center_id>/services', methods=['GET'])
def fitness_center_services(fitness_center_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            info = db.fetch_all('service', {'fitness_center_id': fitness_center_id})
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
                user = db.fetch_one("user", {'login': login})
                session['user_id'] = user['id']
            return redirect(f'/user/{user['id']}')
        else:
            return 'Incorrect login or password'


@app.route('/loguot', methods=['GET'])
@logion_required
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
            res = db.fetch_all('resources', {'user_id': user_id})
        return res or 'No info about current user resources'
