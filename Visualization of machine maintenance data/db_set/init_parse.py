import sqlite3

con = sqlite3.connect(r'C:\Users\谢佩恒\Desktop\维修数据可视化项目\zhongtong.db')
cur = con.cursor()

sql = '''
    create table parse
    (
        日期 text,
        机组 text,
        耗电 numeric,
        备件金额 numeric,
        正品 numeric,
        原料 numeric,
        人数 numeric,
        成品规格 text,
        当日生产 numeric
    );
'''

cur.execute(sql)
cur.close()
con.close()

print('parse表创建完成')