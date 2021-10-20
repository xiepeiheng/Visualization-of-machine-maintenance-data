from flask import Blueprint, render_template, request
import sqlite3
from function.sqlite_function import *

# 这东西暂时还不知道正规的弄应该怎么弄，先这么凑合一下
from settings import DATABASE_PATH

_down = Blueprint('down', __name__, url_prefix='/')


@_down.route('/down')
def down1():
    start_time = initial_time()
    stop_time = initial_time()

    cmy1, cmy2, cmy3 = zfh(start_time, stop_time)

    time = [start_time, stop_time]



    return render_template('down_and_fault/down/template-down.html', time=time, cmy1=cmy1, cmy2=cmy2, cmy3=cmy3)


@_down.route('/down/ajax', methods=['POST'])
def down2():
    data = request.data.decode('utf-8')

    start_time = request.form['start']
    stop_time = request.form['stop']
    cmy1, cmy2, cmy3 = zfh(start_time, stop_time)

    return render_template('down_and_fault/down/down.html', cmy1=cmy1, cmy2=cmy2, cmy3=cmy3)


def zfh(start_time, stop_time):
    cmy_r = f"日期 >= '{start_time}' and 日期 <= '{stop_time}'"

    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()

    # 数据区域1：表格 开始---------------------------------------------------------------------
    cmy1 = []  # 数据区域1的总数组
    # 数据表格区域，顺序是机组，维修，换辊，待料
    # cmy1 = [[机组，维修，换辊，待料],[机组，维修，换辊，待料]...]
    sql1 = f'''
            select 机组,cast(sum(机修) as int),cast(sum(电修) as int),cast(sum(自修) as int),cast(sum(换辊) as int),cast(sum(待料) as int),cast(sum(开机) as int),cast(sum(当日生产) as int)
            from down_parse  
            where {cmy_r}
            GROUP BY 机组
            order by round(sum(开机),3) desc 
        '''
    data1 = cur.execute(sql1)
    for i in data1:
        cmy1.append([i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]])


    # 数据区域2 重写
    # 坐标轴的机组和时间数据
    # crew = ['761', '762'...]
    # time = ['2021-06-01' ,'2021-06-02'...]
    # [机组,时间,[故障名,[机组名,[数据]],[机组名,[数据]]]...]]
    # 柱状图的种类 ['761', '762'...]
    data2_crew = sqliteObject_to_list_a(cur, f'''select DISTINCT 机组 from down1 where {cmy_r}''')

    # 图表横坐标 ['2021-06-01' ,'2021-06-02'...]
    data2_time = sqliteObject_to_list_a(cur, f'''select DISTINCT 日期 from down1 where {cmy_r}''')

    # 显示图表名称的数组
    picture_name = ['机修时间', '电修时间', '自修时间', '换辊时间', '待料时间', '开机时间']

    # 用于轮询搜索数据的数组
    col = ['机修天', '电修天', '自修天', '换辊天', '待料天', '开机天']

    cmy2 = [data2_crew, data2_time]
    for i in picture_name:
        cmy2.append([i])

    # temp1 = [故障名,[机组名,[数据]],[机组名,[数据]]...]
    num = 0
    for i in cmy2[2:]:
        for j in data2_crew:
            data1 = sqliteObject_to_list_a(cur, f'''select {col[num]} from down1 where {cmy_r} and 机组 = "{j}" ''')
            i.append([j, data1])
        num = num + 1
    # 数据区域2：折线图 结束---------------------------------------------------------------------

    # 数据区域3：柱状图和环形饼图 开始---------------------------------------------------------------------
    # 数组内容：[[机组，停车天数，机修，电修，自修，换辊，待料，运行天数]...]
    cmy3 = [['机组', '停车天数', '机修', '电修', '自修', '换辊', '待料', '运行天数']]
    data3 = cur.execute(
        f'''
                select 机组,round(sum(1.0-开机天),3),round(sum(机修天),3),round(sum(电修天),3),round(sum(自修天),3),round(sum(换辊天),3),round(sum(待料天),3),round(sum(开机天),3)
                from down1
                where 日期 >= '{start_time}' and 日期 <= '{stop_time}'
                GROUP BY 机组 
            '''
    )
    for i in data3:
        cmy3.append([i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]])

    cur.close()
    con.close()

    return cmy1, cmy2, cmy3

# 返回未选择日期时的初始时间
def initial_time():
    con, cur = db_open()
    time = sqliteObject_to_list_n(cur, f'''
        select max(日期) from parse
    ''')
    db_close(con, cur)
    return time