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
            insert into down(
            日期,
            机组,
            机修,
            电修,
            待料,
            换辊,
            自修,
            单位天,
            备注
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
            ?
        )
        '''
        cur.execute(sql, (
        i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8]))

    con.commit()
    cur.close()
    con.close()


csvpath = r'C:\Users\谢佩恒\Desktop\维修数据可视化项目\原始表格\故障与停机\停机.csv'
down = read_csv(csvpath)
savedata(down)


print('down表录入完成')

