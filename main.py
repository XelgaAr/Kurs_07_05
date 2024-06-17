import datetime
import os

from flask import Flask, request, render_template, session, redirect
from functools import wraps
from utils import SQLiteDatabase, calc_slots

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
    user_login = session.get('user_login')
    return render_template('home.html', user_login=user_login, title='Home Page')


@app.route('/user', methods=['GET', 'POST'])
@login_required
def user_info():
    user_id = session.get('user_id')
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch("user", {'id': user_id}, ["login", "phone", "birth_date", "funds"],
                           fetch_all=False)
        return render_template('user_info.html', user_info=res, user_login=session.get('user_login'))

    if request.method == 'POST':
        return f'change user info'


@app.route('/user/funds', methods=['GET', 'POST'])
@login_required
def user_funds():
    user_id = session.get('user_id')
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch('user', {'id': user_id}, fetch_all=False)
        return render_template('funds.html', funds=res['funds'])

    if request.method == 'POST':
        return f'add funds'


@app.route('/user/reservations', methods=['GET', 'POST'])
@login_required
def user_reservations():
    user_id = session.get('user_id')
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            services = db.fetch('service', columns=['id', 'name'])
            reservations = db.fetch(
                'reservation',
                join={'user': 'reservation.user_id = user.id', 'service': 'reservation.service_id = service.id',
                      'fitness_center': 'service.fitness_center_id=fitness_center.id'},
                columns=['reservation.id AS reservation_id', 'reservation.date', 'reservation.time',
                         'user.login AS user_name', 'service.name As service_name',
                         'fitness_center.name AS fitness_center_name'],
                condition={'user_id': user_id})

        return render_template('reservations.html', reservations=reservations, services=services, user_login=session.get('user_login'))

    if request.method == 'POST':
        with SQLiteDatabase('db.db') as db:
            db.insert("reservation", {'user_id': user_id, 'service_id': request.form.get('service_id'),
                                      'trainer_id': request.form.get('trainer_id'), 'date': request.form.get('date'),
                                      'time': request.form.get('slots')})

        return redirect('/user/reservations')


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


@app.route('/fitness_centers', methods=['GET'])
def fitness_center():
    with SQLiteDatabase('db.db') as db:
        res = db.fetch('fitness_center')
    return render_template('fitness_centers.html', fitness_centers=res, user_login=session.get('user_login'), title='Fitness Centers')


@app.route('/fitness_center/<int:fitness_center_id>', methods=['GET'])
def fitness_center_id(fitness_center_id):
    with SQLiteDatabase('db.db') as db:
        fitness_center = db.fetch('fitness_center', {'id': fitness_center_id}, fetch_all=False)
        if not fitness_center:
            return "Fitness center not found", 404

        services = db.fetch('service', {'fitness_center_id': fitness_center_id}, fetch_all=True)
        trainers = db.fetch('trainer', {'fitness_center_id': fitness_center_id}, fetch_all=True)

    return render_template('fitness_center_details.html', fitness_center=fitness_center, services=services,
                           trainers=trainers, user_login=session.get('user_login'))


@app.route('/fitness_center/<int:fitness_center_id>/services/<int:service_id>', methods=['GET'])
def service_info(fitness_center_id, service_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            service = db.fetch(
                'service', {'fitness_center_id': fitness_center_id, 'service_id': service_id},
                join={'fitness_center': 'service.fitness_center_id = fitness_center.id'},
                columns=['service.id AS service_id', 'service.name', 'service.duration', 'service.price',
                         'service.description', 'service.max_attendees', 'fitness_center.name AS fitness_center_name'],
                fetch_all=False)

            trainers = db.fetch(
                'trainer_services', {'service_id': service_id},
                join={'trainer': 'trainer.id = trainer_services.trainer_id'},
                columns=['trainer.id', 'trainer.name', 'trainer_services.capacity'])

            if not trainers:
                return render_template('error.html', error_message="Trainers not found for current fitness center and service.", user_login=session.get('user_login')), 404

            if service:
                return render_template('service.html', service=service, trainers=trainers, user_login=session.get('user_login'))
            else:
                return 'Service not found'


@app.route('/fitness_center/<fitness_center_id>/trainer', methods=['GET'])
def fitness_center_trainer(fitness_center_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch('trainer', {'id': fitness_center_id})
        return res


@app.route('/fitness_center/<int:fitness_center_id>/trainer/<int:trainer_id>', methods=['GET'])
def fitness_center_trainer_id(fitness_center_id, trainer_id):
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            trainer = db.fetch('trainer', {'fitness_center_id': fitness_center_id, 'id': trainer_id}, fetch_all=False)
            if not trainer:
                return render_template('Trainer not found', user_login=session.get('user_login')), 404

            services = db.fetch(
                'trainer_services',
                {'trainer_id': trainer_id},
                join={'service': 'trainer_services.service_id = service.id'},
                columns=['service.id', 'service.name', 'service.description'])

            if services is None:
                services = []

        return render_template('trainer.html', trainer=trainer, services=services, user_login=session.get('user_login'))


@app.route('/pre_reservation', methods=['POST'])
@login_required
def pre_reservation():
    user_id = session.get('user_id')
    trainer_id = request.form['trainer_id']
    service_id = request.form['service_id']
    desired_date = request.form['date']
    formatted_date = datetime.datetime.strptime(desired_date, "%Y-%m-%d").strftime("%d.%m.%Y")

    time_slots = calc_slots(trainer_id, service_id, formatted_date, user_id)

    if isinstance(time_slots, str):  # if the value is an error message
        return render_template('error.html', error_message=time_slots, user_login=session.get('user_login'))

    return render_template('pre_reservation.html',
                           form_info={'trainer_id': trainer_id, 'service_id': service_id, 'date': formatted_date,
                                      'time_slots': time_slots}, user_login=session.get('user_login'))


@app.route('/trainer/<trainer_id>/rating', methods=['GET', 'POST'])
@login_required
def fitness_center_trainer_id_rating(trainer_id):
    if request.method == 'GET':
        return render_template('rating.html', user_login=session.get('user_login'))
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
                session['user_login'] = user['login']
            return redirect(f'/')
        else:
            return 'Incorrect login or password'


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    session.pop('user_id')
    session.pop('user_login')
    return redirect('/')


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


@app.route('/user/resources', methods=['GET'])
@login_required
def user_resources():
    user_id = session.get('user_id')
    if request.method == 'GET':
        with SQLiteDatabase('db.db') as db:
            res = db.fetch('resources', {'user_id': user_id})
        return res or 'No info about current user resources'
