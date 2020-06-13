import sqlite3


class Connect:
    conn = None

    def __init__(self):
        self.conn = sqlite3.connect('stock.db')

    def get_connect(self):
        return self.conn

    def commit(self):
        self.conn.commit()

stockConnect = Connect()
