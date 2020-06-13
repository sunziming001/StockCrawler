from Sql.Connect import stockConnect


class CashFlowRecd:
    codeId = ''
    year = -1
    season = -1
    value = -1
    recd_type_id = -1


class CashFlowRecdTable:

    @staticmethod
    def clear_cash_flow_recd_table():
        conn = stockConnect.get_connect()
        sql = 'delete from CashFlowRecd'
        conn.execute(sql)
        conn.commit()

    @staticmethod
    def select_net_present_average(code_id):
        cash_flow_recd = CashFlowRecd()
        cash_flow_recd.codeId = code_id

    @staticmethod
    def select_records(cash_flow_recd):
        cash_flow_recd_list = []
        conn = stockConnect.get_connect()
        str_sql = CashFlowRecdTable.gen_select_sql(cash_flow_recd)
        cursor = conn.execute(str_sql)
        for row in cursor:
            item = CashFlowRecd()
            item.codeId = row[0]
            item.year = row[1]
            item.season = row[2]
            item.value = row[3]
            item.recd_type_id = row[4]
            cash_flow_recd_list.append(item)
        return cash_flow_recd_list

    @staticmethod
    def gen_select_sql(cash_flow_recd):
        str_sql = "select codeId, year, season, value, recdTypeId from CashFlowRecd "
        str_cmds = []
        str_cond = ''

        if cash_flow_recd.codeId != '':
            str_cmds.append('codeId = ' + cash_flow_recd.codeId)
        if cash_flow_recd.year != -1:
            str_cmds.append('year = ' + str(cash_flow_recd.year))
        if cash_flow_recd.season != -1:
            str_cmds.append('season = ' + str(cash_flow_recd.season))
        if cash_flow_recd.value != -1:
            str_cmds.append('value = ' + str(cash_flow_recd.value))
        if cash_flow_recd.recd_type_id != -1:
            str_cmds.append('recdTypeId = ' + str(cash_flow_recd.recd_type_id))

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
    def insert_cash_flow_recd_list(cash_flow_recd_list):
        conn = stockConnect.get_connect()
        list_len = len(cash_flow_recd_list)
        for i in range(0, list_len):
            sql = CashFlowRecdTable.gen_insert_sql(cash_flow_recd_list[i])
            try:
                conn.execute(sql)
            except Exception:
                pass
        conn.commit()

    @staticmethod
    def gen_insert_sql(cash_flow_recd):
        str_sql = ('insert into CashFlowRecd(codeId,year,season,value,recdTypeId)values('
                   + cash_flow_recd.codeId + ","
                   + str(cash_flow_recd.year) + ","
                   + str(cash_flow_recd.season) + ","
                   + str(cash_flow_recd.value) + ","
                   + str(cash_flow_recd.recd_type_id)
                   + ');')
        return str_sql
