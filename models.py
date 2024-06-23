from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Time
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    birth_date = Column(DateTime, default='1940-01-01', nullable=False)
    phone = Column(String(50), nullable=False)
    funds = Column(Integer, default=0, nullable=False)

    resources = relationship("Resources", back_populates="user")

    def __init__(self, login, password, birth_date, phone):
        self.login = login
        self.password = password
        self.birth_date = birth_date
        self.phone = phone
        self.funds = 0

    def add_funds(self, amount):
        if amount is not None and amount > 0:
            self.funds += amount

    def withdraw(self, amount):
        if amount is not None and amount > 0:
            new_funds = self.funds - amount
            self.funds = max(new_funds, 0)


class FitnessCenter(Base):
    __tablename__ = 'fitness_center'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    address = Column(String(300), nullable=False)
    contacts = Column(String(300), nullable=False)

    def __init__(self, name, address, contacts):
        self.name = name
        self.address = address
        self.contacts = contacts


class Trainer(Base):
    __tablename__ = 'trainer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    fitness_center_id = Column(Integer, ForeignKey(FitnessCenter.id), nullable=False)
    age = Column(Integer)
    sex = Column(String(50), nullable=False)

    def __init__(self, name, fitness_center_id, age, sex):
        self.name = name
        self.fitness_center_id = fitness_center_id
        self.age = age
        self.sex = sex


class Service(Base):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    duration = Column(Integer, nullable=False)
    description = Column(String(500))
    price = Column(Integer, default=0, nullable=False)
    fitness_center_id = Column(Integer, ForeignKey(FitnessCenter.id), nullable=False)
    max_attendees = Column(Integer, default=1, nullable=False)

    def __init__(self, name, duration, description, price, fitness_center_id, max_attendance):
        self.name = name
        self.duration = duration
        self.description = description
        self.price = price
        self.fitness_center_id = fitness_center_id
        self.max_attendees = max_attendance


class TrainerServices(Base):
    __tablename__ = 'trainer_services'
    id = Column(Integer, primary_key=True, autoincrement=True)
    trainer_id = Column(Integer, ForeignKey(Trainer.id), nullable=False)
    service_id = Column(Integer, ForeignKey(Service.id), nullable=False)
    capacity = Column(Integer, nullable=False)

    def __init__(self, trainer_id, service_id, capacity):
        self.trainer_id = trainer_id
        self.service_id = service_id
        self.capacity = capacity


class TrainerSchedule(Base):
    __tablename__ = 'trainer_schedule'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    trainer_id = Column(Integer, ForeignKey(Trainer.id), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    def __init__(self, date, trainer_id, start_time, end_time):
        self.date = date
        self.trainer_id = trainer_id
        self.start_time = start_time
        self.end_time = end_time


class Resources(Base):
    __tablename__ = 'resources'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('service.id'), nullable=False)
    amount = Column(Integer, nullable=False)

    user = relationship("User", back_populates="resources")
    service = relationship("Service", back_populates="resources")

    def __init__(self, user_id, service_id, amount):
        self.user_id = user_id
        self.service_id = service_id
        self.amount = amount


class Reservation(Base):
    __tablename__ = 'reservation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    trainer_id = Column(Integer, ForeignKey(Trainer.id), nullable=False)
    service_id = Column(Integer, ForeignKey(Service.id), nullable=False)
    date = Column(DateTime, nullable=False)
    time = Column(Time, nullable=False)

    def __init__(self, user_id, service_id, trainer_id, date, time):
        self.user_id = user_id
        self.trainer_id = trainer_id
        self.service_id = service_id
        self.date = date
        self.time = time


class Rating(Base):
    __tablename__ = 'rating'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    trainer_id = Column(Integer, ForeignKey(Trainer.id), nullable=False)
    points = Column(Integer, nullable=False)
    text = Column(String(500))

    def __init__(self, user_id, trainer_id, points, text):
        self.user_id = user_id
        self.trainer_id = trainer_id
        self.points = points
        self.text = text


class Checkout(Base):
    __tablename__ = 'checkout'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    trainer_id = Column(Integer, ForeignKey(Trainer.id), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    def __init__(self, date, trainer_id, start_time, end_time):
        self.date = date
        self.trainer_id = trainer_id
        self.start_time = start_time
        self.end_time = end_time
