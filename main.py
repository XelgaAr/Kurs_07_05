import datetime
import os
import models

from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from functools import wraps
from utils import calc_slots
from database import init_db, db_session, shutdown_session
from models import *

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET_KEY")

with app.app_context():
    init_db()


@app.teardown_appcontext
def cleanup(exception=None):
    shutdown_session()


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
        user = db_session.query(User).filter(User.id == user_id).first()
        if user:
            return render_template('user_info.html', user_info=user, user_login=session.get('user_login'))
        else:
            return render_template('error.html', error_message="User not found!", user_login=session.get('user_login'))

    if request.method == 'POST':
        return 'Change user info'


@app.route('/user/funds', methods=['GET', 'POST'])
@login_required
def user_funds():
    user_id = session.get('user_id')
    if request.method == 'GET':
        user = db_session.query(User).filter(User.id == user_id).first()
        if user:
            return render_template('funds.html', funds=user.funds)
        else:
            return render_template('error.html', error_message="User not found!", user_login=session.get('user_login'))

    elif request.method == 'POST':
        return 'add funds'


@app.route('/user/reservations', methods=['GET', 'POST'])
@login_required
def user_reservations():
    user_id = session.get('user_id')
    if request.method == 'GET':
        services = db_session.query(Service).all()

        reservations = db_session.query(
            Reservation.id.label('reservation_id'),
            Reservation.date,
            Reservation.time,
            User.login.label('user_name'),
            Service.name.label('service_name'),
            FitnessCenter.name.label('fitness_center_name')
        ).join(User, Reservation.user_id == User.id) \
            .join(Service, Reservation.service_id == Service.id) \
            .join(FitnessCenter, Service.fitness_center_id == FitnessCenter.id) \
            .filter(Reservation.user_id == user_id) \
            .all()

        return render_template('reservations.html', reservations=reservations, services=services,
                               user_login=session.get('user_login'))

    elif request.method == 'POST':
        new_reservation = Reservation(
            user_id=user_id,
            service_id=request.form.get('service_id'),
            trainer_id=request.form.get('trainer_id'),
            date=request.form.get('date'),
            time=request.form.get('slots')
        )
        db_session.add(new_reservation)
        db_session.commit()

        return redirect('/user/reservations')


@app.route('/user/reservations/<int:reservation_id>', methods=['GET', 'POST'])
@login_required
def user_reservations_id(reservation_id):
    if request.method == 'GET':
        reservation = db_session.query(Reservation).filter_by(id=reservation_id).join(User).join(Trainer).join(
            Service).first()
        if reservation:
            return render_template('reservation_details.html', reservation=reservation,
                                   user_login=session.get('user_login'))
        else:
            return render_template('error.html', error_message="Reservation not found",
                                   user_login=session.get('user_login'))
    if request.method == 'POST':
        return f'create reservation with id: {reservation_id}'


@app.route('/user/reservations/<int:reservation_id>/delete',
           methods=['POST'])
@login_required
def user_reservations_delete(reservation_id):
    reservation = db_session.query(Reservation).get(reservation_id)
    if reservation:
        db_session.delete(reservation)
        db_session.commit()
        return jsonify({'status': 'success', 'message': 'Reservation deleted successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Reservation not found'}), 404


@app.route('/user/checkout', methods=['GET', 'POST', 'PUT'])
@login_required
def user_checkout():
    if request.method == 'GET':
        checkouts = db_session.query(Reservation).all()
        reservations_json = [
            {
                'id': checkout.id,
                'date': checkout.date.strftime("%Y-%m-%d"),
                'trainer_id': checkout.trainer_id,
                'start_time': checkout.start_time.strftime("%H:%M"),
                'end_time': checkout.end_time.strftime("%H:%M")
            }
            for checkout in checkouts
        ]
        return jsonify(reservations_json)
    if request.method == 'POST':
        return f'create user checkout'
    if request.method == 'PUT':
        return f'change user checkout '


@app.route('/fitness_centers', methods=['GET'])
def fitness_center():
    fitness_centers = db_session.query(FitnessCenter).all()
    return render_template('fitness_centers.html', fitness_centers=fitness_centers,
                           user_login=session.get('user_login'), title='Fitness Centers')


@app.route('/fitness_center/<int:fitness_center_id>', methods=['GET'])
def fitness_center_id(fitness_center_id):
    fitness_center = db_session.query(FitnessCenter).filter_by(id=fitness_center_id).first()
    if not fitness_center:
        return render_template('error.html', error_message="Fitness center not found",
                               user_login=session.get('user_login')), 404

    services = db_session.query(Service).filter_by(fitness_center_id=fitness_center_id).all()
    trainers = db_session.query(Trainer).filter_by(fitness_center_id=fitness_center_id).all()

    return render_template('fitness_center_details.html', fitness_center=fitness_center, services=services,
                           trainers=trainers, user_login=session.get('user_login'))


@app.route('/fitness_center/<int:fitness_center_id>/services/<int:service_id>', methods=['GET'])
def service_info(fitness_center_id, service_id):
    service = (db_session.query(
        Service.id.label('service_id'),
        Service.name,
        Service.duration,
        Service.price,
        Service.description,
        Service.max_attendees,
        FitnessCenter.name.label('fitness_center_name')
    ).join(FitnessCenter)
     .filter(Service.id == service_id, Service.fitness_center_id == fitness_center_id).first())

    if not service:
        return render_template('error.html', error_message="Service not found",
                               user_login=session.get('user_login')), 404

    trainers = (db_session.query(
        Trainer.id,
        Trainer.name,
        TrainerServices.capacity
    ).join(TrainerServices, TrainerServices.trainer_id == Trainer.id)
     .filter(TrainerServices.service_id == service_id).all())

    if not trainers:
        return render_template('error.html', error_message="Trainers not found for current fitness center and service.",
                               user_login=session.get('user_login')), 404

    return render_template('service.html', service=service, trainers=trainers, user_login=session.get('user_login'))


@app.route('/fitness_center/<int:fitness_center_id>/trainer/<int:trainer_id>', methods=['GET'])
def fitness_center_trainer_id(fitness_center_id, trainer_id):
    trainer = db_session.query(Trainer).filter_by(fitness_center_id=fitness_center_id, id=trainer_id).first()
    if not trainer:
        return render_template('error.html', error_message="Trainer not found",
                               user_login=session.get('user_login')), 404

    services = (db_session.query(Service.id, Service.name, Service.description)
                .join(TrainerServices, Service.id == TrainerServices.service_id)
                .filter(TrainerServices.trainer_id == trainer_id).all())

    if not services:
        services = []

    return render_template('trainer.html', trainer=trainer, services=services, user_login=session.get('user_login'))


@app.route('/pre_reservation', methods=['POST'])
@login_required
def pre_reservation():
    user_id = session.get('user_id')
    trainer_id = request.form['trainer_id']
    service_id = request.form['service_id']
    desired_date = request.form['date']
    formatted_date = datetime.datetime.strptime(desired_date, "%Y-%m-%d")

    time_slots = calc_slots(trainer_id, service_id, formatted_date, user_id)

    if isinstance(time_slots, str):  # if the value is an error message
        return render_template('error.html', error_message=time_slots, user_login=session.get('user_login'))

    return render_template('pre_reservation.html',
                           form_info={'trainer_id': trainer_id, 'service_id': service_id, 'date': formatted_date,
                                      'time_slots': time_slots}, user_login=session.get('user_login'))


@app.route('/trainer/<int:trainer_id>/rating', methods=['GET', 'POST'])
@login_required
def fitness_center_trainer_id_rating(trainer_id):
    if request.method == 'GET':
        current_rating = db_session.query(Rating).filter_by(user_id=session.get('user_id'), trainer_id=trainer_id).first()
        return render_template('rating.html', user_login=session.get('user_login'), current_rating=current_rating)

    if request.method == 'POST':
        form_data = request.form
        existing_rating = db_session.query(Rating).filter_by(user_id=session.get('user_id'), trainer_id=trainer_id).first()
        if existing_rating:
            return render_template('error.html', error_message="You have already rated this trainer.",
                                   user_login=session.get('user_login')), 404

        new_rating = Rating(
            user_id=session.get('user_id'),
            trainer_id=trainer_id,
            points=form_data['points'],
            text=form_data['text']
        )
        db_session.add(new_rating)
        db_session.commit()

        return redirect(url_for('fitness_center_trainer_id_rating', trainer_id=trainer_id))


def check_credentials(username, password):
    user = db_session.query(models.User).filter_by(login=username, password=password).first()
    # user = database.session.execute(select(models.User).where(models.User.login==username, models.User.password==password)).first()[0]
    return user


@app.route('/login', methods=['GET', 'POST'])
def get_login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = check_credentials(login, password)
        if user is not None:
            session['user_id'] = user.id
            session['user_login'] = user.login
            return redirect('/')
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
        user = models.User(login=form_data['login'], password=form_data['password'],
                           birth_date=datetime.datetime.strptime(form_data['birth_date'], "%Y-%m-%d"),
                           phone=form_data['phone'])
        db_session.add(user)
        db_session.commit()

        session['user_id'] = user.id
        session['user_login'] = user.login
        return redirect('/')


@app.route('/user/resources', methods=['GET'])
@login_required
def user_resources():
    user_id = session.get('user_id')
    if user_id:
        resources = db_session.query(Resources).filter_by(user_id=user_id).all()
        if resources:
            return render_template('resources.html', resources=resources, user_login=session.get('user_login'))
        else:
            return render_template('error.html', error_message="No info about current user resources", user_login=session.get('user_login')), 404
    else:
        return render_template('error.html', error_message="User not identified", user_login=session.get('user_login')), 404
