import datetime
import sqlite3

from database import db_session
from models import Reservation, TrainerSchedule, TrainerServices, Service


def calc_slots(trainer_id, service_id, desired_date, user_id):
    start_of_day = desired_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = desired_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    formatted_date = desired_date.strftime('%Y-%m-%d')

    booked_times = db_session.query(Reservation).filter(
        Reservation.trainer_id == trainer_id,
        Reservation.date.between(start_of_day, end_of_day)
    ).join(Service, Service.id == Reservation.service_id).all()

    trainer_schedule = db_session.query(TrainerSchedule).filter(
        TrainerSchedule.trainer_id == trainer_id,
        TrainerSchedule.date == formatted_date
    ).first()

    trainer_capacity = db_session.query(TrainerServices).filter(
        TrainerServices.trainer_id == trainer_id,
        TrainerServices.service_id == service_id
    ).first()

    service_info = db_session.query(Service).filter(
        Service.id == service_id
    ).first()

    if not trainer_schedule or not trainer_capacity or not service_info:
        error_message = "Missing required info:"
        if not trainer_schedule:
            error_message += f" No schedule found for the trainer on {formatted_date}."
        if not trainer_capacity:
            error_message += " No capacity information found for the trainer and service."
        if not service_info:
            error_message += " No service information found."
        return error_message

    start_dt = datetime.datetime.combine(trainer_schedule.date, trainer_schedule.start_time)
    end_dt = datetime.datetime.combine(trainer_schedule.date, trainer_schedule.end_time)
    curr_dt = start_dt
    trainer_slots = {}
    while curr_dt < end_dt:
        trainer_slots[curr_dt] = trainer_capacity.capacity
        curr_dt += datetime.timedelta(minutes=15)

    for booking in booked_times:
        booking_start = datetime.datetime.combine(booking.date, booking.time)
        booking_end = booking_start + datetime.timedelta(minutes=booking.service.duration)
        while booking_start < booking_end:
            if booking_start in trainer_slots:
                trainer_slots[booking_start] -= 1
            booking_start += datetime.timedelta(minutes=15)

    user_booked_times = [
        datetime.datetime.combine(b.date, b.time) for b in booked_times if b.user_id == user_id
    ]

    result_times = []
    service_duration = service_info.duration
    service_start_time = start_dt
    while service_start_time < end_dt:
        service_end_time = service_start_time + datetime.timedelta(minutes=service_duration)
        if service_end_time > end_dt:
            break
        everything_is_free = True
        iter_start_time = service_start_time
        while iter_start_time < service_end_time:
            if iter_start_time in user_booked_times or not trainer_slots.get(iter_start_time, 0):
                everything_is_free = False
                break
            iter_start_time += datetime.timedelta(minutes=15)

        if everything_is_free:
            result_times.append(service_start_time)

        service_start_time += datetime.timedelta(minutes=15)

    if not result_times:
        return "No available slots."

    final_result = [datetime.datetime.strftime(el, '%H:%M') for el in result_times]
    db_session.close()
    return final_result
