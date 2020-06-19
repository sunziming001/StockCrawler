from Sql.Connect import stockConnect
from datetime import datetime
from datetime import timedelta


class ProfitRecd:
    codeId = ''
    year = -1
    season = -1
    value = -1
    recd_type_id = -1


class ProfitRecdTable:
    @staticmethod
    def clear_profit_recd_table():
        conn = stockConnect.get_connect()
        sql = 'delete from ProfitRecd'
        conn.execute(sql)
        conn.commit()

    @staticmethod
    def select_records(profit_recd):
        profit_recd_list = []
        conn = stockConnect.get_connect()
        str_sql = ProfitRecdTable.gen_select_sql(profit_recd)
        cursor = conn.execute(str_sql)
        for row in cursor:
            item = ProfitRecd()
            item.codeId = row[0]
            item.year = row[1]
            item.season = row[2]
            item.value = row[3]
            item.recd_type_id = row[4]
            profit_recd_list.append(item)
        return profit_recd_list


    @staticmethod
    def select_stock_recd(code_id):
        profit_recd_list = []
        conn = stockConnect.get_connect()
        str_sql = ProfitRecdTable.gen_select_stock_is_profitable(code_id)
        cursor = conn.execute(str_sql)
        for row in cursor:
            item = ProfitRecd()
            item.codeId = row[0]
            item.year = row[1]
            item.season = row[2]
            item.value = row[3]
            item.recd_type_id = row[4]
            profit_recd_list.append(item)
        return profit_recd_list

    @staticmethod
    def gen_select_stock_is_profitable(code_id):
        #cur_date = date - timedelta(days=180)
        #cur_season = 1
        #if cur_date.month <= 3:
        #    cur_season = 1
        #elif cur_date.month <= 6:
        #    cur_season = 2
        #elif cur_date.month <= 9:
        #    cur_season = 3
        #else:
        #    cur_season = 4
        int_code = int(code_id)
        str_sql = ("select codeId, year, season, value, recdTypeId from ProfitRecd where "
                   + "codeId = " + '\''+str(int_code)+'\''
                   + " and recdTypeId == 5")
        return str_sql

    @staticmethod
    def gen_select_sql(profit_recd):
        str_sql = "select codeId, year, season, value, recdTypeId from ProfitRecd "
        str_cmds = []
        str_cond = ''

        if profit_recd.codeId != '':
            str_cmds.append('codeId = ' + profit_recd.codeId)
        if profit_recd.year != -1:
            str_cmds.append('year = ' + str(profit_recd.year))
        if profit_recd.season != -1:
            str_cmds.append('season = ' + str(profit_recd.season))
        if profit_recd.value != -1:
            str_cmds.append('value = ' + str(profit_recd.value))
        if profit_recd.recd_type_id != -1:
            str_cmds.append('recdTypeId = ' + str(profit_recd.recd_type_id))

        cmds_cnt = len(str_cmds)
        if cmds_cnt > 0:
            str_cond += ' where '
            for i in range(0, cmds_cnt, 1):
                str_cond += str_cmds[i]
                if i != cmds_cnt - 1:
                    str_cond += ' and '
            str_cond += ' '
            str_sql += str_cond

        str_sql += ' order by year;'
        return str_sql

    @staticmethod
    def insert_profit_recd_list(profit_recd_list):
        conn = stockConnect.get_connect()
        list_len = len(profit_recd_list)
        for i in range(0, list_len):
            sql = ProfitRecdTable.gen_insert_sql(profit_recd_list[i])
            try:
                conn.execute(sql)
            except Exception:
                pass
        conn.commit()

    @staticmethod
    def gen_insert_sql(profit_recd):
        str_sql = ('insert into ProfitRecd(codeId,year,season,value,recdTypeId)values('
                   + profit_recd.codeId + ","
                   + str(profit_recd.year) + ","
                   + str(profit_recd.season) + ","
                   + str(profit_recd.value) + ","
                   + str(profit_recd.recd_type_id)
                   + ');')
        return str_sql
