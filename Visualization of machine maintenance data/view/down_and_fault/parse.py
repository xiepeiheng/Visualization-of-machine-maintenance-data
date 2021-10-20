from flask import Blueprint, render_template, request
from function.sqlite_function import *
import sqlite3
from settings import DATABASE_PATH

_parse = Blueprint('parse', __name__, url_prefix='/')


@_parse.route('/parse')
def parse1():
    start_time = initial_time()
    stop_time = initial_time()

    table, pic_name, cmy, crew_length = zfh(start_time, stop_time)

    time = [start_time, stop_time]

    return render_template('down_and_fault/parse/template_parse.html', time=time, table=table, pic_name=pic_name,
                           cmy=cmy, crew_length=crew_length)


@_parse.route('/parse/ajax', methods=['POST'])
def parse2():
    start_time = request.form['start']
    stop_time = request.form['stop']
    table, pic_name, cmy, crew_length = zfh(start_time, stop_time)

    return render_template('down_and_fault/parse/parse.html', table=table, pic_name=pic_name,
                           cmy=cmy, crew_length=crew_length)


def zfh(start_time, stop_time):
    con, cur = db_open()

    # 日期范围限制
    hxy_r = f'''日期 >= "{start_time}" and 日期 <= "{stop_time}"'''

    crew = sqliteObject_to_list_a(cur, f'''
            select distinct 机组 from parse_down where {hxy_r}
    ''')

    # 表格内容顺序，机组编号，成材率，人均吨钢，吨电耗，单位产量，吨备件
    table = []
    for i in crew:
        temp = sqliteObject_to_list_h(cur, f'''
            select 机组,ifnull(ROUND(sum(正品)*100/sum(原料),3)||'%',''),IFNULL(round(IFNULL(sum(当日生产),0)/(select sum(人数) from parse_down where 当日生产 != '' and {hxy_r} and 机组 = {i}),3),''), ifnull(ROUND(sum(耗电)/sum(当日生产),3),''),ifnull(ROUND(sum(当日生产)/sum(开机),3),''),ifnull(ROUND(sum(备件金额)/sum(当日生产),3),''),ifnull(ROUND(sum(当日生产),3),'')
            from parse_down
            where {hxy_r} and 机组 = {i}
        ''')
        table.append(temp[0])

    # 返回总计数据
    # 机组成材率,人均吨钢,吨电耗,单位产量,吨备件
    temp = sqliteObject_to_list_h(cur, f'''
        select ifnull(ROUND(sum(正品)*100/sum(原料),3)||'%',''),IFNULL(round(IFNULL(sum(当日生产),0)/(select sum(人数) from parse_down where 当日生产 != '' and {hxy_r}),3),''),ifnull(ROUND(sum(耗电)/sum(当日生产),3),''),ifnull(ROUND(sum(当日生产)/sum(开机),3),''),ifnull(ROUND(sum(备件金额)/sum(当日生产),3),''),ifnull(ROUND(sum(当日生产),3),'')
        from parse_down                                       
        where {hxy_r}
    ''')
    table.append(['总计']+temp[0])

    # 返回日期横坐标数组
    time = sqliteObject_to_list_a(cur, f'''
        select distinct 日期 from parse1 where {hxy_r}
    ''')

    # 返回机组数据
    crew = sqliteObject_to_list_a(cur, f'''
        select distinct 机组 from parse1 where {hxy_r}
    ''')
    # 机组个数，在echarts中有用
    crew_length = len(crew)

    # ['product', '127机组', '114机组', '128机组'],
    # ['2021-08-01', 43.3, 85.8, 93.7],
    # ['2021-08-02', 83.1, 73.4, 55.1],

    # 图表内容顺序 人均吨钢，吨电耗，单位产量 吨备件和成材率不显示趋势，直接看最上面的总量即可
    # 图表的title文字,同时也可用于搜索
    pic_name = ['人均吨钢', '吨电耗', '单位产量', '成材率']

    # 构造dataset数据存储库,分别是cmy[0]到cmy[3]
    cmy = [[['product']], [['product']], [['product']], [['product']]]
    for y in cmy:
        for m in time:
            y.append([m])
    num = 0
    for i in pic_name:
        for j in crew:
            temp = sqliteObject_to_list_a(cur, f'''
                    select {i}
                    from parse1
                    where {hxy_r} and 机组 = {j}
                ''')
            cmy[num][0].append(j)
            for k in range(len(temp)):
                cmy[num][k + 1].append(temp[k])
        num = num + 1


    db_close(con, cur)
    return table, pic_name, cmy, crew_length


def initial_time():
    con, cur = db_open()
    time = sqliteObject_to_list_n(cur, f'''
        select max(日期) from parse
    ''')
    db_close(con, cur)
    return time