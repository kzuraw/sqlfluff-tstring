import os

DATABASE_URL = os.environ["DATABASE_URL"]


def get_users(active: bool):
    return sql(t"select   *   from   users   where   active = {active}")


def get_count():
    total = 42
    return sql(t"select   count(*)   from   orders")
