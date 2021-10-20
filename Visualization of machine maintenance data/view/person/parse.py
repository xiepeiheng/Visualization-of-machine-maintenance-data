from flask import Blueprint, render_template, request
from function.sqlite_function import *
import sqlite3
from settings import DATABASE_PATH

_person = Blueprint('person', __name__, url_prefix='/')


@_parse.route('/parse', defaults={'time': '2021-06-292021-07-29'})
@_parse.route('/parse/<time>')
def parse1(time):
    start_time = time[0:10]
    stop_time = time[10:]

    table = zfh(start_time, stop_time)

    time = [start_time, stop_time]

    return render_template('down_and_fault/parse/template_parse.html', time=time, table=table)


@_parse.route('/parse/ajax', methods=['POST'])
def parse2():
    start_time = request.form['start']
    stop_time = request.form['stop']
    table = zfh(start_time, stop_time)

    return render_template('down_and_fault/parse/parse.html', table=table)


def zfh(start_time, stop_time):
    con, cur = db_open()

    # 日期范围限制
    hxy_r = f'''日期 >= "{start_time}" and 日期 <= "{stop_time}"'''

    # 返回日期横坐标数组
    time = sqliteObject_to_list_a(cur, f'''
        select distinct 日期 from parse where {hxy_r}
    ''')
    # 返回机组数据
    crew = sqliteObject_to_list_a(cur, f'''
        select distinct 机组 from parse where {hxy_r}
    ''')

    # 表格内容顺序，机组编号，成材率，人均吨钢，吨电耗，单位产量，吨备件

    table = sqliteObject_to_list_h(cur, f'''
        select 机组,ifnull(ROUND(sum(正品)/sum(原料),2),''),ifnull(ROUND(sum(正品)/sum(人数),2),''),ifnull(ROUND(sum(耗电)/sum(正品),2),''),ifnull(ROUND(sum(正品)/sum(开机),2),''),ifnull(ROUND(sum(备件金额)/sum(正品),2),'')
        from parse2
        where {hxy_r}
        GROUP BY 机组
    ''')

    # # 图表内容顺序 人均吨钢，吨电耗，单位产量 吨备件和成材率不显示趋势，直接看最上面的总量即可
    # # 图表的title文字,同时也可用于搜索
    # pic_name = ['人均吨钢', '吨电耗', '单位产量']
    # for i in pic_name:
    #     temp = sqliteObject_to_list_h(cur, f'''
    #     select 机组,{i}
    #     from parse1
    #     where {hxy_r}
    #     GROUP BY 机组
    # ''')
    #
    #
    #
    #
    #
    # hxy1 = sqliteObject_to_list_h(cur, f'''
    #     select 机组,ROUND(sum(人均吨钢),2),ROUND(sum(吨电耗),2),ROUND(sum(单位产量),2),ROUND(sum(吨备件),2)
    #     from parse1
    #     where {hxy_r}
    #     GROUP BY 机组
    # ''')
    #
    # hxy2 = sqliteObject_to_list_a(cur, f'''
    #     select 机组,ROUND(sum(正品)/sum(原料),2)
    #     from parse
    #     where {hxy_r}
    #     GROUP BY 机组
    # ''')


    # 每日趋势区域

    db_close(con, cur)
    return table
