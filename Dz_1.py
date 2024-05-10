from flask import Flask, request

app = Flask(__name__)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return f'please login'
    else:
        return f'you are have registered'


@app.route('/user', methods=['GET', 'POST', 'PUT'])
def user():
    if request.method == 'GET':
        return f'user info'
    if request.method == 'POST':
        return f'input user info'
    if request.method == 'PUT':
        return f'change user info'


@app.route('/user/funds', methods=['GET', 'POST'])
def user_funds():
    if request.method == 'GET':
        return f'info about funds'
    if request.method == 'POST':
        return f'add funds'


@app.route('/user/reservations', methods=['GET', 'POST'])
def user_reservations():
    if request.method == 'GET':
        return f'info about reservations'
    if request.method == 'POST':
        return f'create reservations'


@app.route('/user/reservations/<reservation_id>', methods=['GET', 'POST', 'DELETE'])
def user_reservations(reservation_id):
    if request.method == 'GET':
        return f'info about reservation with id: {reservation_id}'
    if request.method == 'POST':
        return f'create reservation with id: {reservation_id}'
    if request.method == 'DELETE':
        return f'delete reservation with id: {reservation_id}'


@app.route('/user/checkout ', methods=['GET', 'POST', 'PUT'])
def user_checkout():
    if request.method == 'GET':
        return f'info about user checkout'
    if request.method == 'POST':
        return f'create user checkout'
    if request.method == 'PUT':
        return f'change user checkout '


@app.route('/fitness_center', methods=['GET'])
def fitness_center():
    if request.method == 'GET':
        return f'info about fitness center'


@app.route('/fitness_center/<fitness_center_id>', methods=['GET'])
def fitness_center(fitness_center_id):
    if request.method == 'GET':
        return f'info about fitness center with id :{fitness_center_id}'


@app.route('/fitness_center/<fitness_center_id>/trainer', methods=['GET'])
def fitness_center_trainer(fitness_center_id):
    if request.method == 'GET':
        return f'info about trainer from fitness center with id :{fitness_center_id}'


@app.route('/fitness_center/<fitness_center_id>/trainer/<trainer_id>', methods=['GET'])
def fitness_center_trainer_id(fitness_center_id, trainer_id):
    if request.method == 'GET':
        return f'info about trainer with id:{trainer_id} from fitness center with id :{fitness_center_id}'


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
        return f'please register'
    if request.method == 'POST':
        return f'you are registered'


@app.route('/fitness_center/<fitness_center_id>/loyalty_programs', methods=['GET'])
def fitness_center_id_loyalty_programs(fitness_center_id):
    if request.method == 'GET':
        return f'info about loyalty_programs in fitness center with id :{fitness_center_id}'

# /login [get, post]
# /user [get, put, post]
# /user/funds [get, post]
# /user/reservations [get, post]
# /user/reservations/<reservation_id> [get, put, delete]
# /user/checkout [get, post, put]
# /fitness_center [get]
# /fitness_center/<id> [get]
# /fitness_center/<id>/trainer [get]
# /fitness_center/<id>/trainer/<trainer_id> [get]
# /fitness_center/<id>/trainer/<trainer_id>/rating [get, post, put]
# /fitness_center/<id>/services [get]
# /fitness_center/<id>/services/<service_id> [get]
# /register [get, post]
# /fitness_center/<id>/loyality_programs [get]
