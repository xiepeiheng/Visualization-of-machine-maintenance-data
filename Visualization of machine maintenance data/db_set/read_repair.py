import csv
import sqlite3


# 读取文件并以数组形式返回[[第一行],[第二行]...]
def read_csv(readpath):
    cmy = []
    with open(readpath, "rt") as myFile:
        d = csv.reader(myFile)
        for i in d:
            cmy.append(list(map(lambda x: x.strip(), i)))
        return cmy


def savedata(cmy):
    con = sqlite3.connect(r'C:\Users\谢佩恒\Desktop\维修数据可视化项目\zhongtong.db')
    cur = con.cursor()
    for i in cmy:
        sql = '''
            insert into repair(
            日期,
            机组,
            工序,
            设备,
            故障部位,
            是否停车,
            开始时间,
            结束时间,
            停车时长分,
            故障描述,
            故障原因,
            故障处理结果,
            维修部门
            )
        values(
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )
        '''
        cur.execute(sql,(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[12]))
        cur.execute("DELETE from repair where 工序 = '飞锯' and 设备 = '锯车' and 故障部位 = '锯片'")

    con.commit()
    cur.close()
    con.close()


csvpath = r'C:\Users\谢佩恒\Desktop\维修数据可视化项目\原始表格\故障与停机\故障.csv'
fault = read_csv(csvpath)
savedata(fault)

print('repair表录入完成')

# DELETE from repair where 工序 = '飞锯' and 设备 = '锯车' and 故障部位 = '锯片'