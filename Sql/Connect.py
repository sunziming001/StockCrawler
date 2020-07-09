import sqlite3


class Connect:
    conn = None
    db_name = ''

    def __init__(self, dbname):
        self.db_name = dbname
        self.conn = sqlite3.connect(dbname)

    def get_connect(self):
        return self.conn

    def commit(self):
        self.conn.commit()


nysdaq_conn = Connect("nysdaq_stock.db")
nyse_conn = Connect("nyse_stock.db")
amex_conn = Connect("amex_stock.db")

zh_conn = Connect("stock.db")

stock_connect = zh_conn


def switch_nysdaq_database():
    global stock_connect
    stock_connect = nysdaq_conn


def switch_nyse_database():
    global stock_connect
    stock_connect = nyse_conn


def switch_amex_database():
    global stock_connect
    stock_connect = amex_conn


def switch_zh_database():
    global stock_connect
    stock_connect = zh_conn


def get_sql_conn():
    return stock_connect.get_connect()
