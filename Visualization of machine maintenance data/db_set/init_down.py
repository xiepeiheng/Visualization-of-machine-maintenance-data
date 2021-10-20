from function.sqlite_function import db_open, db_close

con, cur = db_open()

sql = '''
    create table down
    (
        日期 text,
        机组 text,
        机修 numeric,
        电修 numeric,
        待料 numeric,
        换辊 numeric,
        自修 numeric,
        单位天 numeric,
        备注 text
    );
'''

cur.execute(sql)

db_close(con, cur)

print('down表创建完成')
