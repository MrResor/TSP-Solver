from __init__ import sqlite3


def db_con(func):
    def wrapper_catch_db_error(instance):
        try:
            func(instance)
        except FileNotFoundError:
            instance.error_signal.error_signal.emit(1)

    return wrapper_catch_db_error


def db_querry(func):
    def wrapper_catch_querry_error(instance, querry):
        try:
            return func(instance, querry)
        except sqlite3.OperationalError:
            instance.error_signal.error_signal.emit(2)

    return wrapper_catch_querry_error
