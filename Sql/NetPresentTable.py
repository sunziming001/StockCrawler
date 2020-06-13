from Sql.Connect import stockConnect


class NetPresentValue:
    stock_id = ''
    season = -1
    year = -1
    profit_value = -1
    cash_flow_value = -1
    net_present_value = -1.0


class NetPresentValueTable:


    @staticmethod
    def select_net_present_value(stock_id, season):
        conn = stockConnect.get_connect()
        ret_list = []

        str_sql = NetPresentValueTable.gen_net_present_value_sql(stock_id, season)
        try:
            cursor = conn.execute(str_sql)

            for row in cursor:
                net_present_item = NetPresentValue()
                net_present_item.stock_id = row[0]
                net_present_item.year = row[1]
                net_present_item.season = row[2]
                net_present_item.cash_flow_value = row[3]
                net_present_item.profit_value = row[4]

                if net_present_item.profit_value <= 0 or net_present_item.cash_flow_value <= 0:
                    net_present_item.net_present_value = -100.0
                else:
                    net_present_item.net_present_value = 1.0 *  net_present_item.cash_flow_value / net_present_item.profit_value

                ret_list.append(net_present_item)
        except Exception:
            pass

        return ret_list

    @staticmethod
    def gen_net_present_value_sql(stock_id, season):
        str_sql = ('select '
                   ' CashFlowRecd.codeId, '
                   ' CashFlowRecd.year, '
                   ' CashFlowRecd.season, '
                   ' CashFlowRecd.value, '
                   ' ProfitRecd.value  '
                   ' from ProfitRecd  inner join CashFlowRecd '
                   ' on CashFlowRecd.codeId=ProfitRecd.codeId'
                   ' and CashFlowRecd.season=ProfitRecd.season'
                   ' and CashFlowRecd.year=ProfitRecd.year'
                   ' and CashFlowRecd.recdTypeId=0'
                   ' and ProfitRecd.recdTypeId =5 '
                   ' and ProfitRecd.season = ' + str(season) +
                   # ' and ProfitRecd.year = 2018 '
                   # ' and ProfitRecd.year = ' + str(year) +
                   # ' and ProfitRecd.season = ' + str(season) +
                   ' and ProfitRecd.codeId = ' + stock_id +
                   ' order by ProfitRecd.year ')
        return str_sql
