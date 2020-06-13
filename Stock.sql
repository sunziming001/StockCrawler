CREATE TABLE if not exists StockBrief(
	codeId TEXT primary key NOT NULL,
	name TEXT NOT NULL
);

CREATE table if not exists ProfitRecdType
(
	recdTypeID integer primary key,
	desc TEXT NOT NULL
);

CREATE table if not exists ProfitRecd(
	id integer primary key AUTOINCREMENT,
	codeId TEXT NOT NULL,
	year integer NOT NULL,
	season integer NOT NULL,
	value integer NOT NULL,
	recdTypeId integer NOT NULL
);

CREATE table if not exists CashFlowRecdType(
	recdTypeID integer primary key,
	desc TEXT NOT NULL
);

CREATE table if not exists CashFlowRecd(
	id integer primary key AUTOINCREMENT,
	codeId TEXT NOT NULL,
	year integer NOT NULL,
	season integer NOT NULL,
	value integer NOT NULL,
	recdTypeId integer NOT NULL
);

CREATE table if not exists DayKLineTable(
	id integer primary key AUTOINCREMENT,
	codeId TEXT NOT NULL,
	year integer NOT NULL,
	month integer NOT NULL,
	day integer NOT NULL,
	open real NOT NULL,
	close real NOT NULL,
	high real NOT NULL,
	low real NOT NULL,
	takeover real NOT NULL
);

CREATE table if not exists WeekKLineTable(
	id integer primary key AUTOINCREMENT,
	codeId TEXT NOT NULL,
	year integer NOT NULL,
	month integer NOT NULL,
	day integer NOT NULL,
	open real NOT NULL,
	close real NOT NULL,
	high real NOT NULL,
	low real NOT NULL,
	takeover real NOT NULL
);

CREATE table if not exists MonthKLineTable(
	id integer primary key AUTOINCREMENT,
	codeId TEXT NOT NULL,
	year integer NOT NULL,
	month integer NOT NULL,
	day integer NOT NULL,
	open real NOT NULL,
	close real NOT NULL,
	high real NOT NULL,
	low real NOT NULL,
	takeover real NOT NULL
);



Insert into CashFlowRecdType(recdTypeID,desc)values(0,"经营活动产生的现金流量净额");
Insert into CashFlowRecdType(recdTypeID,desc)values(1,"投资活动产生的现金流量净额");
Insert into CashFlowRecdType(recdTypeID,desc)values(2,"筹资活动产生的现金流量净额");

Insert into ProfitRecdType(recdTypeID,desc)values(0,"营业收入");
Insert into ProfitRecdType(recdTypeID,desc)values(1,"营业成本");
Insert into ProfitRecdType(recdTypeID,desc)values(2,"营业利润");
Insert into ProfitRecdType(recdTypeID,desc)values(3,"利润总额");
Insert into ProfitRecdType(recdTypeID,desc)values(4,"所得税");
Insert into ProfitRecdType(recdTypeID,desc)values(5,"净利润");






















select CashFlowRecd.codeId, CashFlowRecd.value, CashFlowRecd.season, ProfitRecd.value,ProfitRecd.season from ProfitRecd inner join CashFlowRecd 
	on CashFlowRecd.codeId=ProfitRecd.codeId 
	and CashFlowRecd.season=ProfitRecd.season 
	and CashFlowRecd.year=ProfitRecd.year 
	and CashFlowRecd.recdTypeId=0 
	and ProfitRecd.recdTypeId =5 
	and CashFlowRecd.season = 4
	and CashFlowRecd.year = 2018
	and CashFlowRecd.codeId = 2887;
	
