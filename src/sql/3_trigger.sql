CREATE OR REPLACE TRIGGER tbcellBeforeUpdate
AFTER INSERT ON "tbCell"
REFERENCING NEW TABLE AS inserted
FOR EACH STATEMENT EXECUTE PROCEDURE trg_test_beforeinsert();

drop TRIGGER tbcellBeforeUpdate on "tbCell";

CREATE OR REPLACE FUNCTION trg_test_beforeinsert()
RETURNS trigger AS $func$
BEGIN
	INSERT INTO TEMP_INSERT VALUES ((inserted)."SECTOR_ID");
	-- INSERT INTO TEMP_UPDATE 
   	-- 	SELECT TEMP_INSERT."SECTOR_ID" FROM "tbCell" TEMP_INSERT ;

   RETURN NEW;
END
$func$  LANGUAGE plpgsql;

DROP FUNCTION trg_test_beforeinsert

delete from temp_insert;DELETE from "tbCell";
SELECT * from temp_insert;