from function.sqlite_function import sqliteObject_to_list_s, sqliteObject_to_list_a, sqliteObject_to_list_h, \
    sqliteObject_to_list_n, db_open, db_close
import sqlite3
import flask

from flask import Blueprint, render_template, request, flash

_test1 = Blueprint('test1', __name__, url_prefix='/')


# 得到时间条件返回机组数据
def get_crew(cur, r):
    crew = sqliteObject_to_list_a(cur, f'''
            select distinct 机组 from down where {r}
    ''')
    return crew

# 返回机电自对比表
def down_table1(time):
    con, cur = db_open()
    # 查看所选日期内有几个机组
    r = f'''日期 >= "{time[0][0]}" and 日期 <= "{time[-1][1]}"'''
    crew = get_crew(cur, r)
    # 以cmy = [[761,762,763], [[1,2,3],[1,2,3],[1,2,3]], [[1,2,3],[1,2,3],[1,2,3]]]输出
    cmy = [crew]
    for i in time:
        r = f'''日期 >= "{i[0]}" and 日期 <= "{i[1]}"'''
        temp1 = [[], [], []]
        for j in crew:
            # 这里不知为何无法使用sqliteObject_to_list_a函数。具体原因待查
            temp = sqliteObject_to_list_h(cur, f'''
                SELECT cast(sum(机修) as int), cast(sum(电修) as int), cast(sum(自修) as int) 
                FROM down 
                where {r} and 机组 = "{j}"
            ''')
            # 分别将机电自加入对应的数组中
            temp1[0].append(temp[0][0])
            temp1[1].append(temp[0][1])
            temp1[2].append(temp[0][2])
        cmy.append(temp1)
    db_close(con, cur)
    return cmy

# 返回故障率对比表
def down_table2(time):
    con, cur = db_open()
    # 查看所选日期内有几个机组
    r = f'''日期 >= "{time[0][0]}" and 日期 <= "{time[-1][1]}"'''
    crew = get_crew(cur, r)
    # 以cmy = [[761,762,763], [[1,2,3],[1,2,3],[1,2,3]], [[1,2,3],[1,2,3],[1,2,3]]]输出
    cmy = [crew]
    for i in time:
        r = f'''日期 >= "{i[0]}" and 日期 <= "{i[1]}"'''
        temp1 = [[], [], []]
        for j in crew:
            # 这里不知为何无法使用sqliteObject_to_list_a函数。具体原因待查
            temp = sqliteObject_to_list_h(cur, f'''
                SELECT cast(sum(机修)+sum(电修)+sum(自修) as int),cast(sum(开机) as int),round(((sum(机修)+sum(电修)+sum(自修))*100)/sum(开机),2)||'%' 
                FROM down 
                where {r} and 机组 = "{j}"
            ''')
            # 分别将机电自加入对应的数组中
            temp1[0].append(temp[0][0])
            temp1[1].append(temp[0][1])
            temp1[2].append(temp[0][2])
        cmy.append(temp1)
    db_close(con, cur)
    return cmy


@_test1.route('/test', defaults={'time': '2021-07-262021-08-08'})
@_test1.route('/test/<time>')
def test1(time):
    # a = time[:10]
    # b = time[10:]
    # print(a, b)
    a = '2021-07-26'
    b = '2021-08-01'
    c = '2021-08-02'
    d = '2021-08-08'
    time = [['2021-05-29', '2021-'],['2021-07-26', '2021-08-01'], ['2021-08-02', '2021-08-08']]
    cmy1 = down_table1(time)
    cmy2 = down_table2(time)
    return render_template('test/test1.html', cmy1=cmy1, cmy2=cmy2)


@_test1.route('/testabc', methods=['POST'])
def test2():
    return render_template('test/test1-1.html')
