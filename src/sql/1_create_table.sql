/*
User
*/
CREATE TABLE IF NOT EXISTS myuser (
	"id" SERIAL PRIMARY KEY,
	"username" VARCHAR(32) NOT NULL UNIQUE,
	"password" VARCHAR(64) NOT NULL,
	"is_active" BOOL NOT NULL DEFAULT FALSE,
	"is_admin" BOOL NOT NULL DEFAULT FALSE
);


/*
tbCell
CONSTRAINT TOTLETILT_VALUE CHECK("TOTLETILT" = "ELECTTILT" + "MECHTILT")

*/
CREATE TABLE IF NOT EXISTS tbcell ( 
"CITY" varchar(255),
"SECTOR_ID" varchar(50) PRIMARY KEY, 
"SECTOR_NAME" varchar(255) NOT NULL, 
"ENODEBID" int NOT NULL,  
"ENODEB_NAME" varchar(255) NOT NULL, 
"EARFCN" int, 
"PCI" int, 
"PSS" int, 
"SSS" int, 
"TAC" int, 
"VENDOR" varchar(255), 
"LONGITUDE" float NOT NULL, 
"LATITUDE" float, 
"STYLE" varchar(255), 
"AZIMUTH" float NOT NULL, 
"HEIGHT" float, 
"ELECTTILT" float, 
"MECHTILT" float, 
"TOTLETILT" float,
CONSTRAINT PCI_RANGE check("PCI" between 0 and 503),
CONSTRAINT LONGITUDE_RANGE check("LONGITUDE" BETWEEN -180 AND 180),
CONSTRAINT LATITUDE_RANGE check("LATITUDE" BETWEEN -90 AND 90)
); 

/*
tbMRO
*/
CREATE TABLE IF NOT EXISTS tbMROData (
"TimeStamp" varchar(30) ,
"ServingSector" varchar(50) ,
"InterferingSector" varchar(50) ,
"LteScRSRP" float ,
"LteNcRSRP" float ,
"LteNcEarfcn" int ,
"LteNcPci" smallint
);

/*
tbKPI
*/
CREATE TABLE IF NOT EXISTS tbKPI (    
"StartTime" date,
"ENODEB_NAME" varchar(255),
"SECTOR_DESCRIPTION" varchar(255) NOT NULL,
"SECTOR_NAME" varchar(255),
"RCCConnSUCC" INT,
"RCCConnATT" INT,
"RCCConnRATE" FLOAT
);

/*
tbPRB
*/
CREATE TABLE IF NOT EXISTS tbPRB
(
"StartTime" timestamp,
"ENODEB_NAME"  varchar(255),
"SECTOR_DESCRIPTION"  varchar(255) not null,
"SECTOR_NAME"  varchar(255),
"AvgNoise0" float,"AvgNoise1" float,"AvgNoise2" float,"AvgNoise3" float,"AvgNoise4" float,"AvgNoise5" float,"AvgNoise6" float,"AvgNoise7" float,"AvgNoise8" float,"AvgNoise9" float,"AvgNoise10" float,"AvgNoise11" float,"AvgNoise12" float,"AvgNoise13" float,"AvgNoise14" float,"AvgNoise15" float,"AvgNoise16" float,"AvgNoise17" float,"AvgNoise18" float,"AvgNoise19" float,"AvgNoise20" float,"AvgNoise21" float,"AvgNoise22" float,"AvgNoise23" float,"AvgNoise24" float,"AvgNoise25" float,"AvgNoise26" float,"AvgNoise27" float,"AvgNoise28" float,"AvgNoise29" float,"AvgNoise30" float,"AvgNoise31" float,"AvgNoise32" float,"AvgNoise33" float,"AvgNoise34" float,"AvgNoise35" float,"AvgNoise36" float,"AvgNoise37" float,"AvgNoise38" float,"AvgNoise39" float,"AvgNoise40" float,"AvgNoise41" float,"AvgNoise42" float,"AvgNoise43" float,"AvgNoise44" float,"AvgNoise45" float,"AvgNoise46" float,"AvgNoise47" float,"AvgNoise48" float,"AvgNoise49" float,"AvgNoise50" float,"AvgNoise51" float,"AvgNoise52" float,"AvgNoise53" float,"AvgNoise54" float,"AvgNoise55" float,"AvgNoise56" float,"AvgNoise57" float,"AvgNoise58" float,"AvgNoise59" float,"AvgNoise60" float,"AvgNoise61" float,"AvgNoise62" float,"AvgNoise63" float,"AvgNoise64" float,"AvgNoise65" float,"AvgNoise66" float,"AvgNoise67" float,"AvgNoise68" float,"AvgNoise69" float,"AvgNoise70" float,"AvgNoise71" float,"AvgNoise72" float,"AvgNoise73" float,"AvgNoise74" float,"AvgNoise75" float,"AvgNoise76" float,"AvgNoise77" float,"AvgNoise78" float,"AvgNoise79" float,"AvgNoise80" float,"AvgNoise81" float,"AvgNoise82" float,"AvgNoise83" float,"AvgNoise84" float,"AvgNoise85" float,"AvgNoise86" float,"AvgNoise87" float,"AvgNoise88" float,"AvgNoise89" float,"AvgNoise90" float,"AvgNoise91" float,"AvgNoise92" float,"AvgNoise93" float,"AvgNoise94" float,"AvgNoise95" float,"AvgNoise96" float,"AvgNoise97" float,"AvgNoise98" float,"AvgNoise99" float
);

/*
tbPRBnew
这里使用view
*/
-- create table "tbPRBnew"
-- (
-- "StartTime" timestamp,
-- "ENODEB_NAME"  varchar(255),
-- "AvgNoise0" float,"AvgNoise1" float,"AvgNoise2" float,"AvgNoise3" float,"AvgNoise4" float,"AvgNoise5" float,"AvgNoise6" float,"AvgNoise7" float,"AvgNoise8" float,"AvgNoise9" float,"AvgNoise10" float,"AvgNoise11" float,"AvgNoise12" float,"AvgNoise13" float,"AvgNoise14" float,"AvgNoise15" float,"AvgNoise16" float,"AvgNoise17" float,"AvgNoise18" float,"AvgNoise19" float,"AvgNoise20" float,"AvgNoise21" float,"AvgNoise22" float,"AvgNoise23" float,"AvgNoise24" float,"AvgNoise25" float,"AvgNoise26" float,"AvgNoise27" float,"AvgNoise28" float,"AvgNoise29" float,"AvgNoise30" float,"AvgNoise31" float,"AvgNoise32" float,"AvgNoise33" float,"AvgNoise34" float,"AvgNoise35" float,"AvgNoise36" float,"AvgNoise37" float,"AvgNoise38" float,"AvgNoise39" float,"AvgNoise40" float,"AvgNoise41" float,"AvgNoise42" float,"AvgNoise43" float,"AvgNoise44" float,"AvgNoise45" float,"AvgNoise46" float,"AvgNoise47" float,"AvgNoise48" float,"AvgNoise49" float,"AvgNoise50" float,"AvgNoise51" float,"AvgNoise52" float,"AvgNoise53" float,"AvgNoise54" float,"AvgNoise55" float,"AvgNoise56" float,"AvgNoise57" float,"AvgNoise58" float,"AvgNoise59" float,"AvgNoise60" float,"AvgNoise61" float,"AvgNoise62" float,"AvgNoise63" float,"AvgNoise64" float,"AvgNoise65" float,"AvgNoise66" float,"AvgNoise67" float,"AvgNoise68" float,"AvgNoise69" float,"AvgNoise70" float,"AvgNoise71" float,"AvgNoise72" float,"AvgNoise73" float,"AvgNoise74" float,"AvgNoise75" float,"AvgNoise76" float,"AvgNoise77" float,"AvgNoise78" float,"AvgNoise79" float,"AvgNoise80" float,"AvgNoise81" float,"AvgNoise82" float,"AvgNoise83" float,"AvgNoise84" float,"AvgNoise85" float,"AvgNoise86" float,"AvgNoise87" float,"AvgNoise88" float,"AvgNoise89" float,"AvgNoise90" float,"AvgNoise91" float,"AvgNoise92" float,"AvgNoise93" float,"AvgNoise94" float,"AvgNoise95" float,"AvgNoise96" float,"AvgNoise97" float,"AvgNoise98" float,"AvgNoise99" float
-- );

/*
tbC2i
*/
CREATE TABLE IF NOT EXISTS tbC2I
(
"CITY" varchar(255),
"SCELL" varchar(255),
"NCELL" varchar(255),
"PrC2I9" float,
"C2I_Mean" float,
"std" float,
"sampleCount" float,
"WeightedC2I" float,
PRIMARY KEY("SCELL","NCELL")
);

CREATE TABLE IF NOT EXISTS tbMRODataExternal
(
"TimeStamp" varchar(255) ,
"ServingSector" varchar(255) ,
"InterferingSector" varchar(255) ,
"LteScRSRP" FLOAT ,
"LteNcRSRP" FLOAT ,
"LteNcEarfcn" INT ,
"LteNcPci" INT
);
CREATE TABLE IF NOT EXISTS tbC2Inew
(
"SCELL" varchar(255),
"NCELL" varchar(255),
"C2I_Mean" float,
"std" float,
"PrbC2I9" float,
"PrbABS6" float,
PRIMARY KEY("SCELL","NCELL")
);

CREATE TABLE IF NOT EXISTS tbC2I3
(
"a" varchar(255),
"b" varchar(255),
"c" varchar(255),
PRIMARY KEY("a", "b", "c")
);