import sqlite3

con = sqlite3.connect(r'C:\Users\谢佩恒\Desktop\维修数据可视化项目\zhongtong.db')
cur = con.cursor()

sql = '''
    create table repair
    (
        日期 text,
        机组 text,
        工序 text,
        设备 text,
        故障部位 text,
        是否停车 text,
        开始时间 text,
        结束时间 text,
        停车时长分 numeric,
        故障描述 text,
        故障原因 numeric,
        故障处理结果 text,
        维修部门 text
    );
'''

cur.execute(sql)

cur.close()
con.close()

print('repair表创建完成')

