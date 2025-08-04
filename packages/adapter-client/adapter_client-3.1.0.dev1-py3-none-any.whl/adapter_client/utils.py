from functools import wraps


def close_connections(func):
    """Декоратор для функций, запускаемых через ThreadPoolExecutor.

    Закрывает соединение с БД после вызова функции.
    TODO: поискать решение лучше.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            pass
        finally:
            from django.db import connections
            connections.close_all()

    return wrapper
