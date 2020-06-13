from Sql.Connect import stockConnect


class KLine:
    codeId = ''
    year = 0
    month = 0
    day = 0
    takeover = 0.0
    high = 0.0
    low = 0.0
    open = 0.0
    close = 0.0


class KLineTable:

    @staticmethod
    def get_table_name(table_id):
        if table_id == 0:
            return 'DayKLineTable'
        elif table_id == 1:
            return 'WeekKlineTable'
        elif table_id == 2:
            return 'MonthKlineTable'
        else:
            return 'WeekKlineTable'

    @staticmethod
    def clear_k_line_table(table_id):
        conn = stockConnect.get_connect()
        sql = ('delete from ' + KLineTable.get_table_name(table_id))
        conn.execute(sql)
        conn.commit()

    @staticmethod
    def select_k_line_list(code_id, table_id):
        k_line_list = []
        conn = stockConnect.get_connect()
        sql = KLineTable.gen_select_sql(code_id, table_id)
        cursor = conn.execute(sql)
        for row in cursor:
            k_line = KLine()
            k_line.codeId = row[0]
            k_line.year = row[1]
            k_line.month = row[2]
            k_line.day = row[3]
            k_line.open = row[4]
            k_line.close = row[5]
            k_line.high = row[6]
            k_line.low = row[7]
            k_line.takeover = row[8]
            k_line_list.append(k_line)

        return k_line_list

    @staticmethod
    def gen_select_sql(code_id, table_id):
        sql = ('select codeId, year, month, day, open, close, high, low, takeover from '
               + KLineTable.get_table_name(table_id)
               + ' where '
               + "codeId = " + code_id
               + ";")
        return sql

    @staticmethod
    def insert_k_line_list(k_line_list, table_id):
        conn = stockConnect.get_connect()
        list_len = len(k_line_list)
        for i in range(0, list_len):
            k_line_item = k_line_list[i]
            sql = KLineTable.gen_insert_sql(k_line_item, table_id)
            try:
                conn.execute(sql)
            except Exception:
                pass
        conn.commit()

    @staticmethod
    def gen_insert_sql(k_line_item, table_id):
        sql = ('insert into '
               + KLineTable.get_table_name(table_id)
               + ' (codeId, year, month, day, open, close, high, low, takeover)values('
               + k_line_item.codeId + ", "
               + str(k_line_item.year) + ", "
               + str(k_line_item.month) + ", "
               + str(k_line_item.day) + ", "
               + str(k_line_item.open) + ", "
               + str(k_line_item.close) + ", "
               + str(k_line_item.high) + ", "
               + str(k_line_item.low) + ", "
               + str(k_line_item.takeover) + ") "
               )

        return sql
