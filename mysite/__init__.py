# mysite/__init__.py

from __future__ import absolute_import, unicode_literals

# Import Celery application so it gets loaded when Django starts
from .celery import app as celery_app

__all__ = ('celery_app',)


import pymysql
from pymysql.constants import CLIENT

pymysql.install_as_MySQLdb()

class Database:
    database_cred = {
        "host": "localhost",
        "user": "flashcarduser",
        "password": "Group1!!",
        "database": "flashcard_db",
        "autocommit": True,
        "cursorclass": pymysql.cursors.DictCursor,
    }

    def __init__(self, database_cred: dict = None):
        if database_cred:
            self.conn = pymysql.connect(**database_cred)
        else:
            self.conn = pymysql.connect(**self.database_cred)

    def run_qry(self, sql: str):
        self.conn.ping()
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            self.conn.commit()
            result = cursor.fetchall()
        return result

    def run_multiple_queries(self, sql_statements: list[str]):
        if len(sql_statements) == 1:
            return self.run_qry(sql_statements[0])

        new_db_cred = {"client_flag": CLIENT.MULTI_STATEMENTS, **self.database_cred}
        sql_statements = ";".join(sql_statements)

        sql_connetion = pymysql.connect(**new_db_cred)
        sql_connetion.ping()

        with sql_connetion.cursor() as cursor:
            cursor.execute(sql_statements)
            self.conn.commit()
            result = cursor.fetchall()
        return result
