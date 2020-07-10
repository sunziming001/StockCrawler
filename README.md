# StockCrawler
获取美股和a股的历史交易数据，并提供web服务展示macd高位金叉的股票


## 环境 ##
Python3.8 及以上<br>
sqlite3

## 使用方法(工作路径为项目根目录) ##
1. 在项目更目录下使用sqlite3 创建文件stock.db，并且执行Stock.sql中的数据库语句，美股需要使用sqlite3创建文件 nysdaq_stock.db, nyse_stock.db, amex_stock.db,并且执行Stock.sql中的数据库语句

2. 初始化股票代码 
python main.py --init<br>
初始化a股股票代码<br>
<br>
python main.py --initus<br>
初始化美股股票代码<br>

3. 日频k线获取
python main.py --initdl<br>
初始化a股日频k线<br>
<br>
python main.py --initusdl<br>
初始化美股日频k线<br>

4. python main.py --apnv 50 --season 4<br>
获取第四季度净现比排名前50的股票，打印在终端上（只适用于a股）

5. 查询金叉 <br>
python main.py --adcostprofit<br>
查询高位macd金叉的A股股票<br>
<br>
python main.py --aduscostprofit<br>
查询高位macd金叉的美股股票<br>

6. 每日运行脚本<br>
python main.py --dailyrun<br>
每日更新a股k线记录，提供网页数据给web端<br>
<br>
python main.py --dailyrun<br>
每日更新美股k线记录，提供网页数据给web端<br>

7. 启动web服务(端口在7351，可以自定义)<br>
python server.py 7351

## 更新方法 ##
1. 下载 [A股列表下载地址](http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110x&TABKEY=tab1&random=0.14377080499757255 "A股列表下载地址")，将其重命名为A_stock_list.xlsx,覆盖./data路径下的文件
2. 在项目根路径下执行“python main.py --init”