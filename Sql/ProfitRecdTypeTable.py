from Sql.Connect import stockConnect


class ProfitRecdTypeTable:
    oper_income = 0
    oper_cost = 1
    oper_profit = 2
    total_profit = 3
    profit_tax = 4
    pure_profit = 5

    @staticmethod
    def get_type_id_2_name():
        ret = {}
        conn = stockConnect.get_connect()
        cursor = conn.execute('select recdTypeID, desc from ProfitRecdType;')
        for row in cursor:
            type_id = row[0]
            name = row[1]
            ret[type_id] = name

        return ret

    @staticmethod
    def get_id_by_type_name(type_name):
        id_2_name = ProfitRecdTypeTable.get_type_id_2_name()
        for k, v in id_2_name.items():
            if v == type_name:
                return k
        return -1

    @staticmethod
    def get_type_name_by_id(type_id):
        id_2_name = ProfitRecdTypeTable.get_type_id_2_name()
        for k, v in id_2_name.items():
            if k == type_id:
                return v
        return ''
