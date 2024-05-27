from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)


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

    def fetch_all(self, table, condition=None, join_table=None, join_condition=None):
        query = f"SELECT * FROM{table}"
        condition = []

        if join_table is not None:
            join_cond_list = []
            for key, val in join_condition.items():
                join_cond_list.append(f" {key}={val} ")
            join_cond_str = ' and '.join(join_cond_list)
            join_str = f' join{join_table} ON {join_cond_str}'
            query = query + join_str

        if condition is not None:
            for key, val in join_condition.items():
                condition.append(f" {key}={val} ")
            str_conditions = ' and '.join(condition)
            str_conditions = ' where ' + str_conditions
            query = query + str_conditions

        cursor = self.connection.cursor()
        cursor.execute(query)
        res = cursor.fetchall()
        if res:
            return res
        return None

    def fetch_one(self, query, *args, **kwargs):
        cursor = self.connection.cursor()
        cursor.execute(query, *args, **kwargs)
        res = cursor.fetchone()
        if res:
            return res
        return None

    def insert(self, teble, data):
        keys = []
        vals = []
        for key, value in data.items():
            keys.append(key)
            vals.append("'" + str(value) + "'")
        str_keys = ', '.join(keys)
        str_vals = ', '.join(vals)
        query = f"""INSERT INTO {teble} ({str_keys}) VALUES ({str_vals}) """
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()


@app.route('/user', methods=['GET', 'POST', 'PUT'])
def user():
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_all('user')
        return res
    if request.method == 'POST':
        return f'input user info'
    if request.method == 'PUT':
        return f'change user info'


@app.route('/user/<user_id>/funds', methods=['GET', 'POST'])
def user_funds(user_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_all('user', {'id':user_id})
        return render_template('funds.html', funds=res)

    if request.method == 'POST':
        return f'add funds'


@app.route('/user/reservations', methods=['GET', 'POST'])
def user_reservations():
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_all('reservations')
        return res
    if request.method == 'POST':
        return f'create reservations'


@app.route('/user/reservations/<reservation_id>', methods=['GET', 'POST', 'DELETE'])
def user_reservations_id(reservation_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_one('reservation', {'id':reservation_id})
        return res

    if request.method == 'POST':
        return f'create reservation with id: {reservation_id}'
    if request.method == 'DELETE':
        return f'delete reservation with id: {reservation_id}'


@app.route('/user/checkout', methods=['GET', 'POST', 'PUT'])
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
            res = db.fetch_one('fitness_center', {'id':fitness_center_id})
        return res


@app.route('/fitness_center/<fitness_center_id>/trainer', methods=['GET'])
def fitness_center_trainer(fitness_center_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_all('trainer', {'id':fitness_center_id})
        return res


@app.route('/fitness_center/<fitness_center_id>/trainer/<trainer_id>', methods=['GET'])
def fitness_center_trainer_id(fitness_center_id, trainer_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_one('trainer', {'fitness_center_id':fitness_center_id, 'id':trainer_id})
        return res



@app.route('/fitness_center/<fitness_center_id>/trainer/<trainer_id>/rating', methods=['GET', 'POST', 'PUT'])
def fitness_center_trainer_id_rating(fitness_center_id, trainer_id):
    if request.method == 'GET':
        return f'info about rating trainer with id:{trainer_id} from fitness center with id :{fitness_center_id}'
    if request.method == 'POST':
        return f'create rating trainer with id:{trainer_id} from fitness center with id :{fitness_center_id}'
    if request.method == 'PUT':
        return f'change rating trainer with id:{trainer_id} from fitness center with id :{fitness_center_id} '


@app.route('/fitness_center/<fitness_center_id>/services', methods=['GET'])
def fitness_center_services(fitness_center_id):
    if request.method == 'GET':
        return f'info about services in fitness center with id :{fitness_center_id}'


@app.route('/fitness_center/<fitness_center_id>/services/<service_id>', methods=['GET'])
def fitness_center_services_id(fitness_center_id, services_id):
    if request.method == 'GET':
        return f'info about services with id:{services_id} in fitness center with id :{fitness_center_id}'

def check_credentials(username, password):
    with SQLiteDatabase('db.db') as db:
        user = db.fetch_one('user', {'username':username, 'password':password})
    return user is not None


@app.route('/login', methods=['GET', 'POST'])
def get_login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        if check_credentials(login, password):
            return 'succesful login'
        else:
            return 'Incorrect login or password'
    else:
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        form_data = request.form
        with SQLiteDatabase('db.db') as db:
            db.insert("user", {'login':form_data['login'], 'password':form_data['password'], 'birth_date':form_data['birth_date'], 'phone':form_data['phone']})
        return f'you are registered'
@app.route('/user/<user_id>/resources', methods=['GET'])
def user_resources(user_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch_all('resources', {'user_id':user_id})
        return res
