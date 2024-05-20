from flask import Flask, request
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


@app.route('/user', methods=['GET', 'POST', 'PUT'])
def user():
    if request.method == 'GET':
        res = get_from_db('SELECT login, phone, birth_date from user where id=1')

        return res
    if request.method == 'POST':
        return f'input user info'
    if request.method == 'PUT':
        return f'change user info'


@app.route('/user/<user_id>/funds', methods=['GET', 'POST'])
def user_funds(user_id):
    if request.method == 'GET':
        res = get_from_db(f'SELECT funds from user where id={user_id}',many=False)
        return res
    if request.method == 'POST':
        return f'add funds'


@app.route('/user/reservations', methods=['GET', 'POST'])
def user_reservations():
    if request.method == 'GET':
        res = get_from_db(f'SELECT user_id, trainer_id, service_id, date, time from reservation')
        return res
    if request.method == 'POST':
        return f'create reservations'


@app.route('/user/reservations/<reservation_id>', methods=['GET', 'POST', 'DELETE'])
def user_reservations_id(reservation_id):
    if request.method == 'GET':
        res = get_from_db(f'SELECT user_id, trainer_id, service_id, date, time from reservation where id={reservation_id}', many=False)
        return res
    if request.method == 'POST':
        return f'create reservation with id: {reservation_id}'
    if request.method == 'DELETE':
        return f'delete reservation with id: {reservation_id}'


@app.route('/user/checkout', methods=['GET', 'POST', 'PUT'])
def user_checkout():
    if request.method == 'GET':
        res = get_from_db(f'SELECT * from checkout ')
        return res
    if request.method == 'POST':
        return f'create user checkout'
    if request.method == 'PUT':
        return f'change user checkout '


@app.route('/fitness_center', methods=['GET'])
def fitness_center():
    if request.method == 'GET':
        res = get_from_db('SELECT name, adress FROM fitness_center')

        return str(res)


@app.route('/fitness_center/<fitness_center_id>', methods=['GET'])
def fitness_center_id(fitness_center_id):
    if request.method == 'GET':
        res = get_from_db(f'SELECT name, adress FROM fitness_center where id= {fitness_center_id}', many=False)

        return str(res)


@app.route('/fitness_center/<fitness_center_id>/trainer', methods=['GET'])
def fitness_center_trainer(fitness_center_id):
    if request.method == 'GET':
        res = get_from_db(f'SELECT id,name, sex, age, fitness_center_id from trainer where id = {fitness_center_id}')
        return res



@app.route('/fitness_center/<fitness_center_id>/trainer/<trainer_id>', methods=['GET'])
def fitness_center_trainer_id(fitness_center_id, trainer_id):
    if request.method == 'GET':
        res = get_from_db(f'SELECT * from trainer where fitness_center_id= {fitness_center_id} AND id={trainer_id}', many=False)
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return f"""<form action="/register" method="POST"">
  <label for="login">login:</label><br>
  <input type="text" id="login" name="login"><br>
  <label for="password">password:</label><br>
  <input type="password" id="password" name="password"><br>
  <label for="birth_date">birth_date:</label><br>
  <input type="date" id="birth_date" name="birth_date"><br>
  <label for="phone">phone:</label><br>
  <input type="text" id="phone" name="phone"><br>
  
  <input type="submit" value="Submit">
</form>"""
    if request.method == 'POST':
        form_data = request.form
        insert_into_db(f'INSERT INTO user (login, password, birth_date, phone) VALUES (\'{form_data["login"]}\', \'{form_data["password"]}\', \'{form_data["birth_date"]}\', \'{form_data["phone"]}\')')
        return f'you are registered'


@app.route('/user/<user_id>/resources', methods=['GET'])
def fitness_center_id_loyalty_programs(user_id):
    if request.method == 'GET':
        res = get_from_db(f'SELECT * from resources where user_id = {user_id}')
        return res

