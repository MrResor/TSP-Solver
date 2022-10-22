from __init__ import sqlite3


def db_con(func):
    """ Wrapper that catches error when database file is not found.
    """
    def wrapper_catch_db_error(instance):
        try:
            func(instance)
        except FileNotFoundError:
            instance.error_signal.error_signal.emit(1)

    return wrapper_catch_db_error


def db_querry(func):
    """ Catches any errors related to querries send to database.
    """
    def wrapper_catch_querry_error(instance, querry):
        try:
            return func(instance, querry)
        except sqlite3.OperationalError:
            instance.error_signal.error_signal.emit(2)

    return wrapper_catch_querry_error


def db_data(func):
    """ Wrapper that catches errors thrown from function that
        verifies if the data is as we expect.
    """
    def wrapper_catch_data_inconsistency(instance):
        try:
            func(instance)
        except RuntimeError as err:
            if "Cities" in str(err):
                instance.error_signal.error_signal.emit(3)
            else:
                instance.error_signal.error_signal.emit(4)

    return wrapper_catch_data_inconsistency
