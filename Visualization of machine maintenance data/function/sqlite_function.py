import sqlite3
from settings import DATABASE_PATH

# 这是为了防止在路由中查询到结果之后还需要一个for循环读取数据搞得很麻烦所以写的
# 在收到语句之后，进行查询
# 假如查询的数据格式是((a,b),(c,d),(e,f))
# 如果需要[[a,b],[c,d],[e,f]]格式的数据，那么函数就是 'h'
# 如果需要[[a,c,e],[b,d,f]]格式的数据，那么函数就是 's'
# 如果只是查单项数据，返回的数据格式是((a,),(b,),(c,)) 需要变成[a,b,c] 那么函数是 'a'


def sqliteObject_to_list_h(cur, SQLsatement):
    hxy = cur.execute(SQLsatement)
    cmy = []
    for i in hxy:
        temp1 = []
        for ii in i:
            temp1.append(ii)
        cmy.append(temp1)
    return cmy


def sqliteObject_to_list_s(cur, r, SQLsatement):
    hxy = cur.execute(SQLsatement)
    cmy = []
    for i in range(r):
        cmy.append([])
    for i in hxy:
        num = 0
        for ii in i:
            cmy[num].append(ii)
            num = num + 1
    return cmy


def sqliteObject_to_list_a(cur, SQLsatement):
    hxy = cur.execute(SQLsatement)
    cmy = []
    for i in hxy:
        cmy.append(i[0])
    return cmy


def sqliteObject_to_list_n(cur, SQLsatement):
    hxy = cur.execute(SQLsatement)
    cmy = ''
    for i in hxy:
        cmy = i[0]
    return cmy


def db_open():
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    return con, cur


def db_close(con, cur):
    cur.close()
    con.close()
