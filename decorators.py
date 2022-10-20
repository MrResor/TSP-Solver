def db_con(func):
    def wrapper_catch_db_error(instance):
        try:
            func(instance)
        except FileNotFoundError:
            instance.error_signal.error_signal.emit(1)

    return wrapper_catch_db_error
