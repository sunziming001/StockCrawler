# StockCrawler
获取我朝大A股每个股票的净现比排行


## 环境 ##
Python3.8 及以上<br>
sqlite3

## 使用方法(工作路径为项目根目录) ##
1. 在项目更目录下使用sqlite3 创建文件stock.db，并且执行Stock.sql中的数据库语句

2. python main.py --init<br>
初始化股票数据库

3. python main.py --initdl<br>
初始化股票a股日频k线（可选）

4. python main.py --apnv 50 --season 4<br>
获取第四季度净现比排名前50的股票，打印在终端上

5. python main.py --adcost 00001<br>
获取股票的价格成本曲线（依赖指令 --initdl）

6. python main.py --adcostall<br>
获取价格刚刚上传成本曲线的股票代码（依赖指令 --initdl）

## 更新方法 ##
1. 下载 [A股列表下载地址](http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110x&TABKEY=tab1&random=0.14377080499757255 "A股列表下载地址")，将其重命名为A_stock_list.xlsx,覆盖./data路径下的文件
2. 在项目根路径下执行“python main.py --init”