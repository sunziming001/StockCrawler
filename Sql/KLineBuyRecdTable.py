from Sql.Connect import stockConnect


class KLineBuyRecd:
    code_id = ''
    buy_price = 0.0
    sell_price = 0.0
    buy_date = ' '
    sell_date = ' '
    days = 0

    def is_holding(self):
        return self.sell_date == 'None'

    def set_is_holding(self):
        self.sell_date = 'None'
        self.sell_price = 0.0
        self.days = 0


class KLineBuyRecdTable:

    @staticmethod
    def clear_table():
        conn = stockConnect.get_connect()
        sql = 'delete from KLineBuyRecdTable;'
        conn.execute(sql)
        conn.commit()

    @staticmethod
    def select_holding_code():
        recd_list = []
        conn = stockConnect.get_connect()
        str_sql = 'select codeId,buyDate,sellDate,buyPrice,sellPrice,takeDays from KLineBuyRecdTable where sellDate ' \
                  'is \'None\' '
        cursor = conn.execute(str_sql)
        for row in cursor:
            recd = KLineBuyRecd()
            recd.code_id = row[0]
            recd.buy_date = row[1]
            recd.sell_date = row[2]
            recd.buy_price = row[3]
            recd.sell_price = row[4]
            recd.days = row[5]
            recd_list.append(recd)
        return recd_list

    @staticmethod
    def select_holding_buy_recd_list_by_code_id(code_id):
        conn = stockConnect.get_connect()
        ret_list = []

        str_sql = KLineBuyRecdTable.gen_holding_select_sql_by_code_id(code_id)
        cursor = conn.execute(str_sql)
        for row in cursor:
            recd = KLineBuyRecd()
            recd.code_id = row[0]
            recd.buy_date = row[1]
            recd.sell_date = row[2]
            recd.buy_price = row[3]
            recd.sell_price = row[4]
            recd.days = row[5]
            ret_list.append(recd)
        return ret_list

    @staticmethod
    def gen_holding_select_sql_by_code_id(code_id):
        str_sql = ('select codeId,buyDate,sellDate,buyPrice,sellPrice,takeDays from KLineBuyRecdTable '
                   'where codeId = \'' + code_id + '\'')

        return str_sql

    @staticmethod
    def select_holding_buy_recd_list_by_date(date):
        conn = stockConnect.get_connect()
        ret_list = []

        str_sql = KLineBuyRecdTable.gen_holding_select_sql_by_date(date)
        cursor = conn.execute(str_sql)
        for row in cursor:
            recd = KLineBuyRecd()
            recd.code_id = row[0]
            recd.buy_date = row[1]
            recd.sell_date = row[2]
            recd.buy_price = row[3]
            recd.sell_price = row[4]
            recd.days = row[5]
            ret_list.append(recd)
        return ret_list

    @staticmethod
    def gen_holding_select_sql_by_date(date):
        start_date = '1991-01-01'
        future_date = '2050-01-01'
        str_sql = ('select codeId,buyDate,sellDate,buyPrice,sellPrice,takeDays from KLineBuyRecdTable '
                   'where buyDate between \'' + start_date + '\' and \'' + date.strftime("%Y-%m-%d") + '\' and ' +
                   'sellDate between \'' + date.strftime(
                    "%Y-%m-%d") + '\' and \'' + future_date + '\' and sellDate is not \'None\'; ')

        return str_sql

    @staticmethod
    def insert_buy_recd_list(buy_recd_list):
        conn = stockConnect.get_connect()
        list_len = len(buy_recd_list)
        for i in range(0, list_len):
            sql = KLineBuyRecdTable.gen_insert_sql(buy_recd_list[i])
            try:
                conn.execute(sql)
            except Exception:
                pass
        conn.commit()

    @staticmethod
    def gen_insert_sql(buy_recd):
        str_sql = ('insert into KLineBuyRecdTable(codeId,buyDate,sellDate,buyPrice,sellPrice,takeDays)values('
                   + "'" + buy_recd.code_id + "',"
                   + "'" + buy_recd.buy_date + "',"
                   + "'" + buy_recd.sell_date + "',"
                   + str(buy_recd.buy_price) + ","
                   + str(buy_recd.sell_price) + ","
                   + str(buy_recd.days) + ")"
                   )

        return str_sql
