# -*- codeing = utf-8 -*-
from flask import Blueprint, render_template, request
import sqlite3
from function.sqlite_function import *
import time
import calendar
import datetime

_contrast = Blueprint('contrast', __name__, url_prefix='/')


# 本页面所具有的函数：
# 机电自表 cmy1=down_table1()
# 故障开机表 cmy2=down_table2()
# 成材吨钢等五种指标的表 cmy3=parse_table()
# 超过120分钟表(现在是90分钟了) cmy4=higher_than_120()

# 故障率图 cmy5=failure_rate_pic()
# 机电自图 cmy6=down_pic()
# 故障时间图 cmy7=failure_time_pic()

# 注意，要修改故障时间小于几分钟时要修改两个地方的数字

@_contrast.route('/contrast')
def contrast1():
    date_type = '星期'
    start = '2021-07-26'
    stop = '2021-08-08'
    if date_type == '星期':
        time = week(start, stop)
        unit = '周'
    else:
        time = month(start, stop)
        unit = '月'
    # 机电自表
    cmy1 = down_table1(time)
    # 故障开机表
    cmy2 = down_table2(time)

    # 在页面上可以自行选择需要参与对比的数据是什么。先假定需要返回的是全部数据
    # 但是这个计划最终取消，默认显示全部数据
    num = ['成材率', '人均吨钢', '吨电耗', '单位产量', '吨备件']
    cmy3 = parse_table(time, num)
    preset = ['2021-06', '2021-08', '2021-07-26', '2021-08-08', '']

    # 机电自和故障率对比表。预设是273机组
    crew = '273'
    cmy4 = down_pic(time, crew, unit)
    cmy5 = failure_rate(time, crew, unit)
    # 单个机组故障时长对比图
    cmy7 = failure_time(time, crew, unit)

    # 120分钟
    cmy6, cmy6_crew = higher_than_120(time)
    # 120分钟列表
    # cmy7 = higher_than_120_list(time)

    # preset 页面第一次打开时的预置时间
    # unit 单位是周还是月
    return render_template('down_and_fault/contrast/template-contrast.html', preset=preset, cmy1=cmy1, cmy2=cmy2,
                           cmy6=cmy6, cmy6_crew=cmy6_crew, cmy3=cmy3, cmy4=cmy4, cmy5=cmy5, unit=unit, cmy7=cmy7)


@_contrast.route('/contrast/ajax1', methods=['POST'])
def contrast2():
    date_type = request.form['date_type']
    start = request.form['start']
    stop = request.form['stop']
    if date_type == '星期':
        time = week(start, stop)
        unit = '周'
    else:
        time = month(start, stop)
        unit = '月'
    # down页面对比表1
    cmy1 = down_table1(time)
    # down页面对比表2
    cmy2 = down_table2(time)
    num = ['成材率', '人均吨钢', '吨电耗', '单位产量', '吨备件']
    cmy3 = parse_table(time, num)
    cmy6, cmy6_crew = higher_than_120(time)
    return render_template('down_and_fault/contrast/contrast-table.html', cmy1=cmy1, cmy2=cmy2, cmy3=cmy3, unit=unit,
                           cmy6=cmy6, cmy6_crew=cmy6_crew)


@_contrast.route('/contrast/ajax2', methods=['POST'])
def contrast3():
    date_type = request.form['date_type']
    start = request.form['start']
    stop = request.form['stop']
    crew = request.form['crew']
    if date_type == '星期':
        time = week(start, stop)
        unit = '周'
    else:
        time = month(start, stop)
        unit = '月'
    cmy4 = down_pic(time, crew, unit)
    cmy5 = failure_rate(time, crew, unit)
    # 单个机组故障时长对比图
    cmy7 = failure_time(time, crew, unit)
    return render_template('down_and_fault/contrast/contrast-picture.html', cmy4=cmy4, cmy5=cmy5, cmy7=cmy7)


@_contrast.route('/contrast/ajax3', methods=['GET'])
def contrast4():
    start = request.values.get("a")
    stop = request.values.get("b")
    date_type = request.values.get("c")
    crew = request.values.get("d")
    if date_type == '星期':
        time = week(start, stop)
        unit = '周'
    else:
        time = month(start, stop)
        unit = '月'
    cmy = higher_than_120_table(time, crew)
    # title = ['日期', '工序', '设备', '故障部位', '开始时间', '结束时间', '停车时长分', '故障描述', '故障处理结果', '维修部门']
    return render_template('down_and_fault/contrast/contrast_data.html', cmy=cmy)


# 点击机组按钮之后弹出机组数据
# 返回时间的格式[ [[时间],[[故障1],[故障2]]],[[时间],[[故障1],[故障2]]] ]
def higher_than_120_table(time, crew):
    cmy = []
    con, cur = db_open()
    for i in time:
        r = f'''日期 >= "{i[0]}" and 日期 <= "{i[1]}"'''
        temp = sqliteObject_to_list_h(cur, f'''
            SELECT 日期,工序,设备,故障部位,开始时间,结束时间,停车时长分,故障描述,故障处理结果,维修部门
            FROM repair
            where 停车时长分>=90 and {r} and 工序 <> '换型' and 机组 = {crew}
        ''')
        cmy.append([i,temp])
    db_close(con, cur)
    return cmy


# 故障时间对比柱状图
def failure_time(time, crew, unit):
    if crew == '':
        cmy = [['product', '故障时间']]
        num = 1
        con, cur = db_open()
        for i in time:
            temp = []
            temp.append(f'第{num}{unit}')
            temp1 = sqliteObject_to_list_n(cur, f'''
                    SELECT ifnull(sum(机修)+sum(电修)+sum(自修),' ')
                    FROM down_parse
                    where 日期 >= '{i[0]}' and 日期 <= '{i[1]}'
                ''')

            temp.append(temp1)
            num = num + 1
            cmy.append(temp)
        db_close(con, cur)
        return cmy
    else:
        cmy = [['product', '故障时间']]
        num = 1
        con, cur = db_open()
        for i in time:
            temp = []
            temp.append(f'第{num}{unit}')
            temp1 = sqliteObject_to_list_n(cur, f'''
                    SELECT ifnull(sum(机修)+sum(电修)+sum(自修),' ')
                    FROM down_parse
                    where 日期 >= '{i[0]}' and 日期 <= '{i[1]}' and 机组 = "{crew}"
                ''')
            temp.append(temp1)
            num = num + 1
            cmy.append(temp)
        db_close(con, cur)
        return cmy


# 挑选单次超过120分钟的机组
# 实在不行就所有机组写上去挨个找
# [[['761', '273', '127'], [485, 277, 535], [3, 2, 2]], [['764', '762', '601', '501', '219', '127'], [295, 230, 155, 160, 190, 135], [2, 1, 1, 1, 1, 1]]]
def higher_than_120(time):
    cmy = []
    con, cur = db_open()
    for i in time:
        r = f'''日期 >= "{i[0]}" and 日期 <= "{i[1]}"'''
        temp = sqliteObject_to_list_s(cur, 3, f'''
            SELECT 机组,sum(停车时长分),count(*)
            FROM repair
            where 停车时长分>=90 and {r} and 工序 <> '换型'
            GROUP BY 机组
        ''')
        cmy.append(temp)
    db_close(con, cur)
    # print(cmy)
    crew = {'114': False, '127': False, '165': False, '219': False, '273': False, '501': False, '502': False,
            '503': False, '601': False, '761': False, '762': False, '763': False, '764': False}
    for i in cmy:
        a = i[0]
        for b in a:
            crew[b] = True
    crew1 = []
    for i in crew:
        if crew[i] == True:
            crew1.append(i)
    return cmy, crew1


# 机电自对比柱状图的数据 数据格式如下
# ['时间', '机修', '电修', '自修'],
# ['第一月', 43.3, 85.8, 93.7],
# ['第二月', 83.1, 73.4, 55.1],
# ['第三月', 86.4, 65.2, 82.5],
# ['第四月', 72.4, 53.9, 39.1]
def down_pic(time, crew, unit):
    if crew == '':
        cmy = [['product', '机修', '电修', '自修']]
        con, cur = db_open()
        num = 1
        for i in time:
            temp = sqliteObject_to_list_h(cur, f'''
                select cast(sum(机修) as int),cast(sum(电修) as int),cast(sum(自修) as int)
                from down1
                where 日期 >= '{i[0]}' and 日期 <= '{i[1]}'
            ''')
            temp1 = [f'第{num}{unit}']
            num = num + 1
            temp1 = temp1 + temp[0]
            cmy.append(temp1)
        db_close(con, cur)
        return cmy
    else:
        cmy = [['product', '机修', '电修', '自修']]
        con, cur = db_open()
        num = 1
        for i in time:
            temp = sqliteObject_to_list_h(cur, f'''
                select cast(sum(机修) as int),cast(sum(电修) as int),cast(sum(自修) as int)
                from down1
                where 日期 >= '{i[0]}' and 日期 <= '{i[1]}' and 机组 = '{crew}'
            ''')
            temp1 = [f'第{num}{unit}']
            num = num + 1
            temp1 = temp1 + temp[0]
            cmy.append(temp1)
        db_close(con, cur)
        return cmy


# 故障率对比的数据格式
# [['product', '故障率'],['第1周', 43.3],['第2周', 83.1]]
def failure_rate(time, crew, unit):
    if crew == '':
        cmy = [['product', '故障率']]
        num = 1
        con, cur = db_open()
        for i in time:
            temp = []
            temp.append(f'第{num}{unit}')
            temp1 = sqliteObject_to_list_n(cur, f'''
                SELECT 
                ifnull(round(((sum(机修)+sum(电修)+sum(自修))*100)/(sum(开机)+sum(机修)+sum(电修)+sum(自修)),2),' ')
                FROM down1 
                where 日期 >= '{i[0]}' and 日期 <= '{i[1]}'
            ''')
            temp.append(temp1)
            num = num + 1
            cmy.append(temp)
        db_close(con, cur)
        return cmy
    else:
        cmy = [['product', '故障率']]
        num = 1
        con, cur = db_open()
        for i in time:
            temp = []
            temp.append(f'第{num}{unit}')
            temp1 = sqliteObject_to_list_n(cur, f'''
                SELECT 
                ifnull(round(((sum(机修)+sum(电修)+sum(自修))*100)/(sum(开机)+sum(机修)+sum(电修)+sum(自修)),2),' ')
                FROM down1 
                where 日期 >= '{i[0]}' and 日期 <= '{i[1]}' and 机组 = "{crew}"
            ''')
            temp.append(temp1)
            num = num + 1
            cmy.append(temp)
        db_close(con, cur)
        return cmy


# 将时间以星期为单位分割
def week(start, stop):
    start = time.strptime(start, "%Y-%m-%d")
    stop = time.strptime(stop, "%Y-%m-%d")

    start_date = datetime.date(start.tm_year, start.tm_mon, start.tm_mday)
    stop_date = datetime.date(stop.tm_year, stop.tm_mon, stop.tm_mday)

    week_num = ((stop_date - start_date + datetime.timedelta(days=1)) / 7).days

    cmy = []

    # 将起始日期倒退一天方便接下来计算
    start_date = start_date - datetime.timedelta(days=1)

    for i in range(week_num):
        a1 = start_date + datetime.timedelta(days=1)
        a2 = start_date + datetime.timedelta(days=7)
        cmy.append([a1.isoformat(), a2.isoformat()])
        start_date = start_date + datetime.timedelta(days=7)
    return cmy


# 将时间以月份为单位分割
def month(start, stop):
    start = start + '-01'
    stop = stop + '-28'
    start = time.strptime(start, "%Y-%m-%d")
    stop = time.strptime(stop, "%Y-%m-%d")

    start_date = datetime.date(start.tm_year, start.tm_mon, start.tm_mday)
    stop_date = datetime.date(stop.tm_year, stop.tm_mon, stop.tm_mday)

    temp = datetime.timedelta(days=1)
    start_month = start_date - temp
    start_month = datetime.date(start_month.year, start_month.month, 1)

    zfh = []
    # 将起始日期(cmy2)倒退一天方便接下来计算
    cmy2 = start_month + datetime.timedelta(days=27)
    while cmy2 != stop_date:
        if (calendar.isleap(cmy2.year) == True) and (cmy2.month == 2):
            cmy1 = cmy2 + datetime.timedelta(days=1)
        elif (calendar.isleap(cmy2.year) == False) and (cmy2.month == 2):
            cmy1 = cmy2.replace(month=cmy2.month + 1, day=1)
        else:
            cmy1 = cmy2 + datetime.timedelta(days=1)
        if cmy1.month == 12:
            cmy2 = cmy2.replace(year=cmy2.year + 1, month=1, day=28)
        else:
            cmy2 = cmy2.replace(month=cmy2.month + 1, day=28)
        zfh.append([cmy1, cmy2])
    return zfh


# 得到时间条件返回机组数据(只允许得到包含日期的sql语句后使用)
def get_crew(cur, r):
    crew = sqliteObject_to_list_a(cur, f'''
            select distinct 机组 from parse_down where {r}
    ''')
    return crew


# 返回机电自对比表
def down_table1(time):
    con, cur = db_open()
    # 查看所选日期内有几个机组
    r = f'''日期 >= "{time[0][0]}" and 日期 <= "{time[0][1]}"'''
    crew = get_crew(cur, r)
    # 以cmy = [[761,762,763], [[1,2,3],[1,2,3],[1,2,3]], [[1,2,3],[1,2,3],[1,2,3]]]输出
    cmy = [crew]
    for i in time:
        r = f'''日期 >= "{i[0]}" and 日期 <= "{i[1]}"'''
        temp1 = [[], [], []]
        for j in crew:
            # 这里不知为何无法使用sqliteObject_to_list_a函数。具体原因待查
            temp = sqliteObject_to_list_h(cur, f'''
                SELECT 
                ifnull(cast(sum(机修) as int),' '), 
                ifnull(cast(sum(电修) as int),' '), 
                ifnull(cast(sum(自修) as int),' ') 
                FROM down1 
                where {r} and 机组 = "{j}"
            ''')
            # 分别将机电自加入对应的数组中
            temp1[0].append(temp[0][0])
            temp1[1].append(temp[0][1])
            temp1[2].append(temp[0][2])
        cmy.append(temp1)
        # 计算总和
        temp5 = sqliteObject_to_list_h(cur, f'''
                SELECT 
                ifnull(cast(sum(机修) as int),' '), 
                ifnull(cast(sum(电修) as int),' '), 
                ifnull(cast(sum(自修) as int),' ') 
                FROM down1 
                where {r}
            ''')
        cmy[-1][0].append(temp5[0][0])
        cmy[-1][1].append(temp5[0][1])
        cmy[-1][2].append(temp5[0][2])

    db_close(con, cur)
    cmy[0].append('总计')
    return cmy


# 按照最后一个时间段的故障率情况对机组进行排序
def get_crew1(cur, time):
    r = f'''日期 >= "{time[-1][0]}" and 日期 <= "{time[-1][1]}"'''
    cmy = sqliteObject_to_list_a(cur, f'''
        SELECT 机组 
        FROM down1 
        where {r}
        GROUP BY 机组 
        ORDER BY round(((sum(机修)+sum(电修)+sum(自修))*100)/(sum(开机)+sum(机修)+sum(电修)+sum(自修)),2) DESC
    ''')
    return cmy


# 返回故障率对比表
def down_table2(time):
    con, cur = db_open()
    # 查看所选日期内有几个机组
    crew = get_crew1(cur, time)
    # 以cmy = [[761,762,763], [[1,2,3],[1,2,3],[1,2,3]], [[1,2,3],[1,2,3],[1,2,3]]]输出
    cmy = [crew]
    for i in time:
        r = f'''日期 >= "{i[0]}" and 日期 <= "{i[1]}"'''
        temp1 = [[], [], []]
        for j in crew:
            # 这里不知为何无法使用sqliteObject_to_list_a函数。具体原因待查
            # 这里的故障率应该是(故障/(故障+开机))
            temp = sqliteObject_to_list_h(cur, f'''
                SELECT 
                ifnull(cast(sum(机修)+sum(电修)+sum(自修) as int),' '),
                ifnull(cast(sum(开机) as int),' '),
                ifnull(round(((sum(机修)+sum(电修)+sum(自修))*100)/(sum(开机)+sum(机修)+sum(电修)+sum(自修)),2)||'%',' ')
                FROM down1 
                where {r} and 机组 = "{j}"
            ''')
            # 分别将机电自加入对应的数组中
            temp1[0].append(temp[0][0])
            temp1[1].append(temp[0][1])
            temp1[2].append(temp[0][2])
        cmy.append(temp1)
        # 计算总和
        temp6 = sqliteObject_to_list_h(cur, f'''
                SELECT 
                ifnull(cast(sum(机修)+sum(电修)+sum(自修) as int),' '),
                ifnull(cast(sum(开机) as int),' '),
                ifnull(round(((sum(机修)+sum(电修)+sum(自修))*100)/(sum(开机)+sum(机修)+sum(电修)+sum(自修)),2)||'%',' ')
                FROM down1 
                where {r}
            ''')
        cmy[-1][0].append(temp6[0][0])
        cmy[-1][1].append(temp6[0][1])
        cmy[-1][2].append(temp6[0][2])

    db_close(con, cur)
    cmy[0].append('总计')
    return cmy


def parse_table(time, num):
    con, cur = db_open()
    # 以下逻辑本来是五种数据中手动选择想看的然后只显示想看的。但后台逻辑写好之后取消了计划

    # 确认检查条件看看五个里面要查哪几个
    r = ''
    # 每周究竟有几项数据不确定，所以需要一个数组
    label = []
    # 确认一共选了几个条件以便确定单个日期的行数
    day = 0
    num = ['成材率', '人均吨钢', '吨电耗', '单位产量', '吨备件']
    if '成材率' in num:
        # r = r + ",ifnull(round(sum(正品)*100/sum(原料),2)||'%',' ')"
        label.append('成材率')
        day = day + 1
    if '人均吨钢' in num:
        # r = r + f",IFNULL(round(IFNULL(sum(当日生产), 0) / (select sum(人数) from parse_down where 当日生产 != '' and {r_1}), 2), ' ')"

        label.append('人均吨钢')
        day = day + 1
    if '吨电耗' in num:
        # r = r + ",ifnull(round(sum(耗电)/sum(当日生产),2),' ')"
        label.append('吨电耗')
        day = day + 1
    if '单位产量' in num:
        # r = r + ",ifnull(round(sum(当日生产)/sum(开机),2),' ')"
        label.append('单位产量')
        day = day + 1
    if '吨备件' in num:
        # r = r + ",ifnull(round(sum(备件金额)/sum(当日生产),2),' ')"
        label.append('吨备件')
        day = day + 1
    # r = r[1:]  # 消除语句最前端的逗号
    # print(r)
    # 查看所选日期内有几个机组
    r1 = f'''日期 >= "{time[0][0]}" and 日期 <= "{time[-1][1]}"'''
    crew = get_crew(cur, r1)
    # 以cmy = [[761,762,763], [[吨钢,1,2,3],[成材,1,2,3],[电耗,1,2,3]], [[吨钢,1,2,3],[成材,1,2,3],[电耗,1,2,3]]]输出
    cmy3 = [crew, day + 1]
    # print(label, day)
    for i in time:
        r_1 = f'''日期 >= "{i[0]}" and 日期 <= "{i[1]}"'''
        # 作为一周或者一个月的数组
        temp1 = []
        # 将每行的标签提前加入数组
        for i in label:
            temp1.append([i])
        for j in crew:
            # 这里不知为何无法使用sqliteObject_to_list_a函数。具体原因待查
            # 这里的故障率应该是(故障/(故障+开机))
            temp = sqliteObject_to_list_h(cur, f'''
                SELECT ifnull(round(sum(正品)*100/sum(原料),2)||'%',' '),IFNULL(round(IFNULL(sum(当日生产),0)/(select sum(人数) from parse_down where 当日生产 != '' and {r_1} and 机组 = "{j}"),2),' '),ifnull(round(sum(耗电)/sum(当日生产),2),' '),ifnull(round(sum(当日生产)/sum(开机),2),' '),ifnull(round(sum(备件金额)/sum(当日生产),2),' ')
                FROM parse_down                                         
                where {r_1} and 机组 = "{j}"
            ''')
            # 分别将机电自加入对应的数组中
            for m in range(len(temp1)):
                temp1[m].append(temp[0][m])
        cmy3.append(temp1)
        # 计算总和
        temp7 = sqliteObject_to_list_h(cur, f'''
                 SELECT ifnull(round(sum(正品)*100/sum(原料),2)||'%',' '),
                 IFNULL(round(IFNULL(sum(当日生产),0)/(select sum(人数) from parse_down where 当日生产 != '' and {r_1}),2),' '),
                 ifnull(round(sum(耗电)/sum(当日生产),2),' '),
                 ifnull(round(sum(当日生产)/sum(开机),2),' '),
                 ifnull(round(sum(备件金额)/sum(当日生产),2),' ')
                 FROM parse_down
                 where {r_1}
             ''')
        cmy3[-1][0].append(temp7[0][0])
        cmy3[-1][1].append(temp7[0][1])
        cmy3[-1][2].append(temp7[0][2])
        cmy3[-1][3].append(temp7[0][3])
        cmy3[-1][4].append(temp7[0][4])

    db_close(con, cur)
    cmy3[0].append('总计')
    return cmy3
