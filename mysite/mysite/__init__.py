# mysite/__init__.py

from __future__ import absolute_import, unicode_literals

# Import Celery application so it gets loaded when Django starts
from .celery import app as celery_app

__all__ = ('celery_app',)


import pymysql
pymysql.version_info = (1, 4, 3, "final", 0)
from pymysql.constants import CLIENT

pymysql.install_as_MySQLdb()

class Database:
    database_cred = {
        "host": "localhost",
        "user": "root",
        "password": "waketech",
        "database": "flashcard_db",
        "autocommit": True,
        "cursorclass": pymysql.cursors.DictCursor,
    }


    def __init__(self, database_cred: dict = None):
        if database_cred:
            self.conn = pymysql.connect(**database_cred)
        else:
            self.conn = pymysql.connect(**self.database_cred)

        # end if

    def run_qry(self, sql: str):
        # to check DB Connection pin the instance
        self.conn.ping()
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            self.conn.commit()
            result = cursor.fetchall()
        # end with
        return result

    def run_multiple_queries(self, sql_statements: list[str]):
        if len(sql_statements) == 1:
            return self.run_qry(sql_statements[0])

        new_db_cred = {"client_flag": CLIENT.MULTI_STATEMENTS, **self.database_cred}
        sql_statements = ";".join(sql_statements)

        sql_connetion = pymysql.connect(**new_db_cred)
         # to check DB Connection pin the instance
        sql_connetion.ping()

        with sql_connetion.cursor() as cursor:
            cursor.execute(sql_statements)
            self.conn.commit()
            result = cursor.fetchall()
        return result
# end class
