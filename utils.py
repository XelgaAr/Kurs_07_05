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


def calc_slots(trainer_id, service_id, desired_date):
    query = f""" SELECT * FROM reservation
    join service on service.id = reservation.service_id
    where trainer_id = {trainer_id}"""
    with SQLiteDatabase('db.db') as db:
        booked_time = db.fetch("reservation", {"trainer_id": trainer_id, "date": "25.10.2024"}, join={'service': 'service.id = reservation.service_id'})
        trainer_schedule = db.fetch("trainer_schedule", {"trainer_id": trainer_id, "date": "25.10.2024"}, fetch_all=False)
        trainer_capacity = db.fetch("trainer_services", {"trainer_id": trainer_id, "service_id": service_id}, fetch_all=False)
        service_info = db.fetch('service', {'service_id': id}, fetch_all=False)
        start_dt = datetime.datetime.strptime(trainer_schedule["date"]+' '+trainer_schedule["start_time"], '%d.%m.%Y %H:%M')
        end_dt = datetime.datetime.strptime(trainer_schedule["date"]+' '+trainer_schedule["end_time"], '%d.%m.%Y %H:%M')
        curr_dt = start_dt
        trainer_schedule = {}
        while curr_dt < end_dt:
            trainer_schedule[curr_dt] = trainer_capacity['capacity']
            curr_dt += datetime.timedelta(minutes=15)
        for one_booking in booked_time:
            booking_date = one_booking["date"]
            booking_time = one_booking["time"]
            booking_duration = one_booking["duration"]
            one_booking_start = datetime.datetime.strptime(booking_date + " " + booking_time, '%d.%m.%Y %H:%M')
            booking_end = one_booking_start + datetime.timedelta(minutes=booking_duration)
            curr_dt = one_booking_start
            while curr_dt < booking_end:
                if curr_dt in trainer_schedule:
                    trainer_schedule[curr_dt] -= 1
                curr_dt += datetime.timedelta(minutes=15)
        result_times = []
        service_duration = service_info["duration"]
        service_start_time = start_dt
        while service_start_time < end_dt:
            service_end_time = service_start_time + datetime.timedelta(minutes=service_duration)
            everything_is_free = True
            iter_start_time = service_start_time
            while iter_start_time < service_end_time:
                if trainer_schedule[iter_start_time] == 0 or service_start_time > end_dt:
                    everything_is_free = False
                    break
                iter_start_time += datetime.timedelta(minutes=15)

            if everything_is_free:
                result_times.append(service_start_time)

            service_start_time += datetime.timedelta(minutes=15)
        final_result = [datetime.datetime.strftime(el, '%H:%M') for el in result_times]
        return final_result







    print('')


calc_slots(1, 1, 2)
