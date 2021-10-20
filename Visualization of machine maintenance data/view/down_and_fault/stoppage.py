from flask import Blueprint, render_template, request
import sqlite3
from function.sqlite_function import sqliteObject_to_list_s, sqliteObject_to_list_a, sqliteObject_to_list_h, \
    sqliteObject_to_list_n, db_open, db_close
from settings import DATABASE_PATH

_stoppage = Blueprint('stoppage', __name__, url_prefix='/')


@_stoppage.route('/stoppage')
def stoppage1():
    start_time = initial_time()
    stop_time = initial_time()
    cmy1, cmy2 = zfh(start_time, stop_time)

    time = [start_time, stop_time]
    # basic = [['down_and_fault/stoppage.html'], ['stoppage.stoppage2', 'stoppage.stoppage4'], '../../static/down_and_fault/css/stoppage.css']

    # 数据透视表初始化
    love = init(start_time, stop_time)

    return render_template('down_and_fault/stoppage/template-stoppage.html', time=time, cmy1=cmy1, cmy2=cmy2, love=love)


# 树图更新
@_stoppage.route('/stoppage/ajax', methods=['POST'])
def stoppage2():
    start_time = request.form['start']
    stop_time = request.form['stop']
    cmy1, cmy2 = zfh(start_time, stop_time)
    return render_template('down_and_fault/stoppage/stoppage-tree.html', cmy1=cmy1, cmy2=cmy2)


# 数据透视表
@_stoppage.route('/stoppage/ajax1', methods=['POST'])
def stoppage4():
    crew = request.form['a']
    procedure = request.form['b']
    device = request.form['c']
    fault = request.form['d']
    start_time = request.form['e']
    stop_time = request.form['f']
    cmy_r = f"日期 >= '{start_time}' and 日期 <= '{stop_time}' and 工序 <> '换型'"
    jsk = []
    if crew != '':
        jsk.append(f"机组 = '{crew}'")
    if procedure != '':
        jsk.append(f"工序 = '{procedure}'")
    if device != '':
        jsk.append(f"设备 = '{device}'")
    if fault != '':
        jsk.append(f"故障部位 = '{fault}'")
    jsk_r = ""
    for i in jsk:
        jsk_r = jsk_r + i + ' and '
    jsk_r = jsk_r + cmy_r

    # 打开数据库
    con, cur = db_open()

    # 返回时间序列
    time = get_time(cur, start_time, stop_time)

    # 根据配置好的条件查询数据
    xph = zzy(cur, jsk_r)

    # 关闭数据库
    db_close(con, cur)
    love = [time, xph]

    return render_template('down_and_fault/stoppage/stoppage-bar.html', love=love)


# 弹出的列表页
@_stoppage.route('/stoppage_data/', methods=['GET'])
def stoppage3():
    start_time = request.values.get("a")
    stop_time = request.values.get("b")
    crew = request.values.get("c")
    procedure = request.values.get("d")
    device = request.values.get("e")
    fault = request.values.get("f")
    cmy_r = f"日期 >= '{start_time}' and 日期 <= '{stop_time}' and 工序 <> '换型'"
    jsk = []
    if crew != '':
        jsk.append(f"机组 = '{crew}'")
    if procedure != '':
        jsk.append(f"工序 = '{procedure}'")
    if device != '':
        jsk.append(f"设备 = '{device}'")
    if fault != '':
        jsk.append(f"故障部位 = '{fault}'")
    jsk_r = ""
    for i in jsk:
        jsk_r = jsk_r + i + ' and '
    jsk_r = jsk_r + cmy_r
    con, cur = db_open()
    datalist = sqliteObject_to_list_h(cur, f'''
        select 日期,机组,工序,设备,故障部位,开始时间,结束时间,停车时长分,故障描述,故障处理结果,维修部门 
        from repair 
        where {jsk_r}
    ''')
    db_close(con, cur)
    return render_template('down_and_fault/stoppage/stoppage_data.html', datalist=datalist)


# 数据透视表初始化
def init(start_time, stop_time):
    cmy_r = f"日期 >= '{start_time}' and 日期 <= '{stop_time}' and 工序 <> '换型'"
    con, cur = db_open()

    cmy1 = get_time(cur, start_time, stop_time)
    cmy2 = f0(cur, cmy_r)

    db_close(con, cur)
    return [cmy1, cmy2]


def dict_factory(zfh, hxy):
    for i in hxy:
        zfh.append({"name": i[0], "value": str(i[1]) + '-' + str(i[2]), "children": [], 'collapsed': False})
    return zfh


# 规定哪些机组展开哪些机组不展开
def dict_factory1(zfh, hxy):
    for j in hxy:
        zfh.append({"name": j[0], "value": str(j[1]) + '-' + str(j[2]), "children": []})
        break
    for i in hxy[1:]:
        zfh.append({"name": i[0], "value": str(i[1]) + '-' + str(i[2]), "children": [], 'collapsed': True})
    return zfh


def zfh(start_time, stop_time):
    hxy_r = f"日期 >= '{start_time}' and 日期 <= '{stop_time}' and 工序 <> '换型'"
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()

    # 输入sql语句，返回数组 如果查询结果为空就返回[]
    # 你以为要处理可能返回查询结果为0的问题，笑死，根本不用解决，直接返回空数组。for中的变量尽量不要相同

    total = sqliteObject_to_list_a(cur, f'''SELECT cast(sum(停车时长分) as int) FROM repair where {hxy_r}''')
    number = sqliteObject_to_list_a(cur, f'''SELECT count(*) FROM repair where {hxy_r}''')
    # print(type(total[0]), type(number[0]))
    cmy1 = [{"name": '全部机组', "value": str(total[0]) + '-' + str(number[0]), "children": []}]

    # 先调查有几个机组 ['502', '601', '761', '114', '127', '165', '219', '273', '762', '764']
    crew_total = sqliteObject_to_list_h(cur, f'''
        SELECT 机组,cast(sum(停车时长分) as int),count(*)
        FROM repair 
        where {hxy_r} 
        group by 机组 
        order by cast(sum(停车时长分) as int) desc 
    ''')
    # 在这里将所有机组都装入对象，只有第一个机组在展示时需要展开，所以使用特制函数dict_factory1
    cmy1[0]['children'] = dict_factory1(cmy1[0]['children'], crew_total)
    # 结果 [{'name': '127', 'value': 0.477, 'children': []}......]

    # 逐个机组轮询 在这个循环中机组名称为crew
    for crew in cmy1[0]['children']:
        procedure_total = sqliteObject_to_list_h(cur, f'''
            select 工序,cast(sum(停车时长分) as int),count(*)
            from repair 
            where {hxy_r} and 机组 = {crew['name']} 
            group by 工序 
            order by cast(sum(停车时长分) as int) desc  
        ''')
        crew['children'] = dict_factory(crew['children'], procedure_total)
        for device in crew['children']:
            device_total = sqliteObject_to_list_h(cur, f'''
                select 设备,cast(sum(停车时长分) as int),count(*)
                from repair 
                where {hxy_r} and 机组 = '{crew['name']}' and 工序 = '{device['name']}' 
                group by 设备 
                order by cast(sum(停车时长分) as int) desc 
            ''')
            device['children'] = dict_factory(device['children'], device_total)
            for failure in device['children']:
                failure_total = sqliteObject_to_list_h(cur, f'''
                    select 故障部位,cast(sum(停车时长分) as int),count(*)
                    from repair 
                    where {hxy_r} and 机组 = '{crew['name']}' and 工序 = '{device['name']}' and 设备 = '{failure['name']}' 
                    group by 故障部位 
                    order by cast(sum(停车时长分) as int) desc  
                ''')
                failure['children'] = dict_factory(failure['children'], failure_total)

    # 改进型
    cmy2 = {"name": '全部故障', "value": 0, "children": []}
    total = sqliteObject_to_list_a(cur, f'''SELECT cast(sum(停车时长分) as int) FROM repair where {hxy_r}''')
    number = sqliteObject_to_list_a(cur, f'''SELECT count(*) FROM repair where {hxy_r}''')
    cmy2['value'] = str(total[0]) + '-' + str(number[0])
    gongxu = sqliteObject_to_list_h(cur,
                                    f'''SELECT 工序,cast(sum(停车时长分) as int),count(*) 
        from repair 
        where {hxy_r} 
        GROUP BY 工序 
        order by cast(sum(停车时长分) as int) desc
    ''')
    # print(gongxu)
    dict_factory1(cmy2['children'], gongxu)
    # print(cmy2)
    for gong_xu in cmy2["children"]:
        # print(gong_xu)
        shebei = sqliteObject_to_list_h(cur, f'''
            SELECT 设备,cast(sum(停车时长分) as int),count(*)
            from repair 
            where {hxy_r} and 工序 = '{gong_xu['name']}' 
            GROUP BY 设备 
            order by cast(sum(停车时长分) as int) desc 
        ''')
        gong_xu['children'] = dict_factory(gong_xu['children'], shebei)
        for she_bei in gong_xu['children']:
            guzhangbuwei = sqliteObject_to_list_h(cur, f'''
                SELECT 故障部位,cast(sum(停车时长分) as int),count(*)
                from repair 
                where {hxy_r} and 工序 = '{gong_xu['name']}' and 设备 = '{she_bei['name']}' 
                GROUP BY 故障部位 
                order by cast(sum(停车时长分) as int) desc 
            ''')
            # print('-------------')
            # print(she_bei['children'])
            she_bei['children'] = dict_factory(she_bei['children'], guzhangbuwei)

    cur.close()
    con.close()

    return cmy1, cmy2


# 使用此代码用于检查
# select *
# from repair
# where 生产线 = '219' and 日期 >= '2021-07-01' and 日期 <= '2021-07-30' and 工序 = '下料' and 设备 = '打包' and 故障部位 = '电磁阀'

# 函数区域
def get_time(cur, start_time, stop_time):
    cmy = sqliteObject_to_list_a(cur, f'''
        select distinct 日期 
        from repair
        where 日期 >= '{start_time}' and 日期 <= '{stop_time}'
    ''')
    return cmy


def zzy(cur, jsk_r):
    cmy = sqliteObject_to_list_h(cur, f'''
        select 日期 ,cast(sum(停车时长分) as int)
        from repair 
        where {jsk_r}
        GROUP BY 日期''')
    return cmy


# 仅用于页面初始化
def f0(cur, cmy_r):
    cmy = sqliteObject_to_list_h(cur, f'''
        select 日期 ,cast(sum(停车时长分) as int)
        from repair 
        where {cmy_r}
        GROUP BY 日期''')
    return cmy


# 获取数据库中最新的数据的日期作为开始和结束日期
def initial_time():
    con, cur = db_open()
    time = sqliteObject_to_list_n(cur, f'''
        select max(日期) from repair
    ''')
    db_close(con, cur)
    return time
