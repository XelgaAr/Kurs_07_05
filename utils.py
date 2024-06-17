import datetime
import sqlite3


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

    def fetch(self, table, condition=None, columns=None, join=None, fetch_all=True):
        query = f"SELECT "
        if columns:
            query += ', '.join(columns)
        else:
            query += '*'
        query += f' FROM {table}'
        if join:
            for join_table, join_condition in join.items():
                query += f' JOIN {join_table} ON {join_condition}'
        conditions = []
        if condition is not None:
            for key, val in condition.items():
                conditions.append(f" {key}='{val}' ")
            str_conditions = ' AND '.join(conditions)
            str_conditions = ' WHERE ' + str_conditions
            query = query + str_conditions

        print(query)

        cursor = self.connection.cursor()
        cursor.execute(query)
        if fetch_all:
            res = cursor.fetchall()
        else:
            res = cursor.fetchone()
        if res:
            return res
        return None

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


def edit(self, table, data, condition):
    update_values = []
    conditions = []
    for key, val in data.items():
        update_values.append(f" {key}='{val}' ")
    set_clause = ', '.join(update_values)
    query = f'UPDATE {table} SET {set_clause}'
    if condition is not None:
        for key, val in condition.items():
            conditions.append(f" {key}='{val}'")
        str_conditions = ' AND '.join(conditions)
        str_conditions = ' WHERE ' + str_conditions
        query = query + str_conditions
    cursor = self.connection.cursor()
    cursor.execute(query)
    self.connection.commit()


def calc_slots(trainer_id, service_id, desired_date, user_id):
    with SQLiteDatabase('db.db') as db:
        booked_time = db.fetch("reservation", {"trainer_id": trainer_id, "date": desired_date}, join={'service': 'service.id = reservation.service_id'})
        trainer_schedule = db.fetch("trainer_schedule", {"trainer_id": trainer_id, "date": desired_date}, fetch_all=False)
        trainer_capacity = db.fetch("trainer_services", {"trainer_id": trainer_id, "service_id": service_id}, fetch_all=False)
        service_info = db.fetch('service', {'id': service_id}, fetch_all=False)

        if not trainer_schedule or not trainer_capacity or not service_info:
            error_message = "Missing required info:"
            if not trainer_schedule:
                error_message += " No schedule found for the trainer."
            if not trainer_capacity:
                error_message += " No capacity information found for the trainer and service."
            if not service_info:
                error_message += " No service information found."
            return error_message

        booked_time = booked_time or []

        start_dt = datetime.datetime.strptime(trainer_schedule["date"] + ' ' + trainer_schedule["start_time"], '%d.%m.%Y %H:%M')
        end_dt = datetime.datetime.strptime(trainer_schedule["date"] + ' ' + trainer_schedule["end_time"], '%d.%m.%Y %H:%M')
        trainer_slots = {}
        curr_dt = start_dt
        while curr_dt < end_dt:
            trainer_slots[curr_dt] = trainer_capacity['capacity']
            curr_dt += datetime.timedelta(minutes=15)

        for one_booking in booked_time:
            one_booking_start = datetime.datetime.strptime(one_booking["date"] + " " + one_booking["time"], '%d.%m.%Y %H:%M')
            booking_end = one_booking_start + datetime.timedelta(minutes=one_booking["duration"])
            curr_dt = one_booking_start
            while curr_dt < booking_end:
                if curr_dt in trainer_slots:
                    trainer_slots[curr_dt] -= 1
                curr_dt += datetime.timedelta(minutes=15)

        user_booked_times = [datetime.datetime.strptime(b["date"] + " " + b["time"], '%d.%m.%Y %H:%M')
                             for b in booked_time if b['user_id'] == user_id]

        result_times = []
        service_duration = service_info["duration"]
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
        return final_result