-- CREATE OR REPLACE TRIGGER tbcellBeforeUpdate
-- AFTER INSERT ON "tbCell"
-- REFERENCING NEW TABLE AS inserted
-- FOR EACH STATEMENT EXECUTE PROCEDURE trg_test_beforeinsert();

-- drop TRIGGER tbcellBeforeUpdate on "tbCell";

-- CREATE OR REPLACE FUNCTION trg_test_beforeinsert()
-- RETURNS trigger AS $func$
-- BEGIN
-- 	INSERT INTO TEMP_INSERT VALUES ((inserted)."SECTOR_ID");

--    RETURN NEW;
-- END
-- $func$  LANGUAGE plpgsql;

-- DROP FUNCTION trg_test_beforeinsert

-- delete from temp_insert;DELETE from "tbCell";
-- SELECT * from temp_insert;


CREATE OR REPLACE PROCEDURE update_tbprb_new()
LANGUAGE SQL
AS $$
	DROP VIEW if exists tbPRBnew;
	CREATE VIEW tbPRBnew AS
        SELECT (timestamp '2000-1-1' + interval '1 year' * (year-2000) + interval '1 month' * (month-1) + interval '1 day' * (day-1)+interval '1 hour' * hour) as "StartTime",
        "ENODEB_NAME",
        "AvgNoise0","AvgNoise1","AvgNoise2","AvgNoise3","AvgNoise4","AvgNoise5","AvgNoise6","AvgNoise7","AvgNoise8","AvgNoise9","AvgNoise10","AvgNoise11","AvgNoise12","AvgNoise13","AvgNoise14","AvgNoise15","AvgNoise16","AvgNoise17","AvgNoise18","AvgNoise19","AvgNoise20","AvgNoise21","AvgNoise22","AvgNoise23","AvgNoise24","AvgNoise25","AvgNoise26","AvgNoise27","AvgNoise28","AvgNoise29","AvgNoise30","AvgNoise31","AvgNoise32","AvgNoise33","AvgNoise34","AvgNoise35","AvgNoise36","AvgNoise37","AvgNoise38","AvgNoise39","AvgNoise40","AvgNoise41","AvgNoise42","AvgNoise43","AvgNoise44","AvgNoise45","AvgNoise46","AvgNoise47","AvgNoise48","AvgNoise49","AvgNoise50","AvgNoise51","AvgNoise52","AvgNoise53","AvgNoise54","AvgNoise55","AvgNoise56","AvgNoise57","AvgNoise58","AvgNoise59","AvgNoise60","AvgNoise61","AvgNoise62","AvgNoise63","AvgNoise64","AvgNoise65","AvgNoise66","AvgNoise67","AvgNoise68","AvgNoise69","AvgNoise70","AvgNoise71","AvgNoise72","AvgNoise73","AvgNoise74","AvgNoise75","AvgNoise76","AvgNoise77","AvgNoise78","AvgNoise79","AvgNoise80","AvgNoise81","AvgNoise82","AvgNoise83","AvgNoise84","AvgNoise85","AvgNoise86","AvgNoise87","AvgNoise88","AvgNoise89","AvgNoise90","AvgNoise91","AvgNoise92","AvgNoise93","AvgNoise94","AvgNoise95","AvgNoise96","AvgNoise97","AvgNoise98","AvgNoise99"
        FROM
        (
        SELECT 
        extract(year from "StartTime") as year,
        extract(month from "StartTime") as month, 
        extract(day from "StartTime") as day, 
        extract(hour from "StartTime") as hour,
        "ENODEB_NAME",
        avg("AvgNoise0") as "AvgNoise0",avg("AvgNoise1") as "AvgNoise1",avg("AvgNoise2") as "AvgNoise2",avg("AvgNoise3") as "AvgNoise3",avg("AvgNoise4") as "AvgNoise4",avg("AvgNoise5") as "AvgNoise5",avg("AvgNoise6") as "AvgNoise6",avg("AvgNoise7") as "AvgNoise7",avg("AvgNoise8") as "AvgNoise8",avg("AvgNoise9") as "AvgNoise9",avg("AvgNoise10") as "AvgNoise10",avg("AvgNoise11") as "AvgNoise11",avg("AvgNoise12") as "AvgNoise12",avg("AvgNoise13") as "AvgNoise13",avg("AvgNoise14") as "AvgNoise14",avg("AvgNoise15") as "AvgNoise15",avg("AvgNoise16") as "AvgNoise16",avg("AvgNoise17") as "AvgNoise17",avg("AvgNoise18") as "AvgNoise18",avg("AvgNoise19") as "AvgNoise19",avg("AvgNoise20") as "AvgNoise20",avg("AvgNoise21") as "AvgNoise21",avg("AvgNoise22") as "AvgNoise22",avg("AvgNoise23") as "AvgNoise23",avg("AvgNoise24") as "AvgNoise24",avg("AvgNoise25") as "AvgNoise25",avg("AvgNoise26") as "AvgNoise26",avg("AvgNoise27") as "AvgNoise27",avg("AvgNoise28") as "AvgNoise28",avg("AvgNoise29") as "AvgNoise29",avg("AvgNoise30") as "AvgNoise30",avg("AvgNoise31") as "AvgNoise31",avg("AvgNoise32") as "AvgNoise32",avg("AvgNoise33") as "AvgNoise33",avg("AvgNoise34") as "AvgNoise34",avg("AvgNoise35") as "AvgNoise35",avg("AvgNoise36") as "AvgNoise36",avg("AvgNoise37") as "AvgNoise37",avg("AvgNoise38") as "AvgNoise38",avg("AvgNoise39") as "AvgNoise39",avg("AvgNoise40") as "AvgNoise40",avg("AvgNoise41") as "AvgNoise41",avg("AvgNoise42") as "AvgNoise42",avg("AvgNoise43") as "AvgNoise43",avg("AvgNoise44") as "AvgNoise44",avg("AvgNoise45") as "AvgNoise45",avg("AvgNoise46") as "AvgNoise46",avg("AvgNoise47") as "AvgNoise47",avg("AvgNoise48") as "AvgNoise48",avg("AvgNoise49") as "AvgNoise49",avg("AvgNoise50") as "AvgNoise50",avg("AvgNoise51") as "AvgNoise51",avg("AvgNoise52") as "AvgNoise52",avg("AvgNoise53") as "AvgNoise53",avg("AvgNoise54") as "AvgNoise54",avg("AvgNoise55") as "AvgNoise55",avg("AvgNoise56") as "AvgNoise56",avg("AvgNoise57") as "AvgNoise57",avg("AvgNoise58") as "AvgNoise58",avg("AvgNoise59") as "AvgNoise59",avg("AvgNoise60") as "AvgNoise60",avg("AvgNoise61") as "AvgNoise61",avg("AvgNoise62") as "AvgNoise62",avg("AvgNoise63") as "AvgNoise63",avg("AvgNoise64") as "AvgNoise64",avg("AvgNoise65") as "AvgNoise65",avg("AvgNoise66") as "AvgNoise66",avg("AvgNoise67") as "AvgNoise67",avg("AvgNoise68") as "AvgNoise68",avg("AvgNoise69") as "AvgNoise69",avg("AvgNoise70") as "AvgNoise70",avg("AvgNoise71") as "AvgNoise71",avg("AvgNoise72") as "AvgNoise72",avg("AvgNoise73") as "AvgNoise73",avg("AvgNoise74") as "AvgNoise74",avg("AvgNoise75") as "AvgNoise75",avg("AvgNoise76") as "AvgNoise76",avg("AvgNoise77") as "AvgNoise77",avg("AvgNoise78") as "AvgNoise78",avg("AvgNoise79") as "AvgNoise79",avg("AvgNoise80") as "AvgNoise80",avg("AvgNoise81") as "AvgNoise81",avg("AvgNoise82") as "AvgNoise82",avg("AvgNoise83") as "AvgNoise83",avg("AvgNoise84") as "AvgNoise84",avg("AvgNoise85") as "AvgNoise85",avg("AvgNoise86") as "AvgNoise86",avg("AvgNoise87") as "AvgNoise87",avg("AvgNoise88") as "AvgNoise88",avg("AvgNoise89") as "AvgNoise89",avg("AvgNoise90") as "AvgNoise90",avg("AvgNoise91") as "AvgNoise91",avg("AvgNoise92") as "AvgNoise92",avg("AvgNoise93") as "AvgNoise93",avg("AvgNoise94") as "AvgNoise94",avg("AvgNoise95") as "AvgNoise95",avg("AvgNoise96") as "AvgNoise96",avg("AvgNoise97") as "AvgNoise97",avg("AvgNoise98") as "AvgNoise98",avg("AvgNoise99") as "AvgNoise99"
        from tbPRB 
        GROUP BY year, month, day, hour,"ENODEB_NAME") as TMP
$$;

-- CREATE TRIGGER trigger_update_tbprb_new AFTER INSERT OR UPDATE OR DELETE
-- ON "tbPRB"
-- FOR EACH ROW
-- EXECUTE PROCEDURE update_tbprb_new();

CREATE OR REPLACE FUNCTION trg_tbcell() RETURNS trigger AS $trg_tbcell$
    BEGIN
        DELETE FROM tbcell
        WHERE "SECTOR_ID"= NEW."SECTOR_ID";
        return NEW;
    END;
$trg_tbcell$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER tbcellBeforeInsertOrUpdate
BEFORE INSERT ON tbcell
FOR EACH ROW 
EXECUTE FUNCTION trg_tbcell();

CREATE OR REPLACE FUNCTION trg_tbprb() RETURNS trigger AS $trg_tbprb$
    BEGIN
        DELETE FROM "tbPRB"
        WHERE "StartTime" = NEW."StartTime" and "SECTOR_NAME"= NEW."SECTOR_NAME";
        return NEW;
    END;
$trg_tbprb$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER tbprbBeforeInsertOrUpdate
BEFORE INSERT ON "tbPRB"
FOR EACH ROW 
EXECUTE FUNCTION trg_tbprb();

CREATE OR REPLACE FUNCTION trg_tbkpi() RETURNS trigger AS $trg_tbkpi$
    BEGIN
        DELETE FROM "tbKPI"
        WHERE "StartTime" = NEW."StartTime" and "SECTOR_NAME"= NEW."SECTOR_NAME";
        return NEW;
    END;
$trg_tbkpi$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER tbkpiBeforeInsertOrUpdate
BEFORE INSERT ON "tbKPI"
FOR EACH ROW 
EXECUTE FUNCTION trg_tbkpi();

CREATE OR REPLACE FUNCTION trg_tbmrodata() RETURNS trigger AS $trg_tbmrodata$
    BEGIN
        DELETE FROM tbMROData
        WHERE "TimeStamp"= NEW."TimeStamp" and "ServingSector"=NEW."ServingSector" and "InterferingSector"=NEW."InterferingSector";
        return NEW;
    END;
$trg_tbmrodata$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER tbmrodataBeforeInsertOrUpdate
BEFORE INSERT ON tbMROData
FOR EACH ROW 
EXECUTE FUNCTION trg_tbmrodata();

CREATE OR REPLACE FUNCTION trg_tbmroexternal() RETURNS trigger AS $trg_tbmroexternal$
    BEGIN
        DELETE FROM tbMROData
        WHERE "TimeStamp"= NEW."TimeStamp" and "ServingSector"=NEW."ServingSector" and "InterferingSector"=NEW."InterferingSector";
        return NEW;
    END;
$trg_tbmroexternal$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER tbmroexternalBeforeInsertOrUpdate
BEFORE INSERT ON tbMRODataExternal
FOR EACH ROW 
EXECUTE FUNCTION trg_tbmroexternal();

CREATE OR REPLACE FUNCTION trg_tbc2i() RETURNS trigger AS $trg_tbc2i$
    BEGIN
        DELETE FROM tbC2I
        WHERE "SCELL"= NEW."SCELL" and "NCELL"=NEW."NCELL";
        return NEW;
    END;
$trg_tbc2i$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER tbc2iBeforeInsertOrUpdate
BEFORE INSERT ON tbC2I
FOR EACH ROW 
EXECUTE FUNCTION trg_tbc2i();


-- -- 外部导入的tbmro表的触发器
-- CREATE OR REPLACE FUNCTION trg_tbmroexternal() RETURNS trigger AS $trg_tbmroexternal$
--     BEGIN
--         new."ServingSector"
--         DELETE FROM "tbMROData"
--         WHERE "TimeStamp"= NEW."TimeStamp" and "ServingSector"=NEW."ServingSector" and "InterferingSector"=NEW."InterferingSector";
--         return NEW;
--     END;
-- $trg_tbmroexternal$ LANGUAGE plpgsql;

-- CREATE OR REPLACE TRIGGER tbmroexternalBeforeInsertOrUpdate
-- BEFORE INSERT ON "tbMROData"
-- FOR EACH ROW 
-- EXECUTE FUNCTION trg_tbmroexternal();
