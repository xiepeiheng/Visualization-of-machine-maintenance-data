from flask import Blueprint, render_template, request, redirect, url_for, render_template_string
from function.sqlite_function import sqliteObject_to_list_s, sqliteObject_to_list_a, sqliteObject_to_list_h, \
    sqliteObject_to_list_n, db_open, db_close
import sqlite3

_test2 = Blueprint('test2', __name__, url_prefix='/')


# def zfh1(start_time, stop_time):
    # hxy_r = f"日期 >= '{start_time}' and 日期 <= '{stop_time}'"
    # con, cur = db_open()
    # cmy = sqliteObject_to_list_h(cur, f'''
    #     SELECT 日期,机修天 FROM down where {hxy_r} and 机组 = '761'
    # ''')
    # db_close(con, cur)
    # return cmy


# def zfh2(start_time, stop_time):
    # hxy_r = f"日期 >= '{start_time}' and 日期 <= '{stop_time}'"
    # con, cur = db_open()
    #
    # cmy = sqliteObject_to_list_a(cur, f'''
    #     select distinct 日期 from down where {hxy_r}
    # ''')
    #
    # db_close(con, cur)
    # return cmy


# @_test2.route('/test2', defaults={'1321321'})
@_test2.route('/test2')
def test1():
    # start_time = start
    # stop_time = stop
    # xph = zfh1(start_time, stop_time)
    # time = zfh2(start_time, stop_time)
    xph1 = 1321
    xph2 = 1965
    return render_template('test/test2.html', xph1=xph1, xph2=xph2)


@_test2.route('/test1/ajax', methods=['POST'])
def test2():
    # data = request.data.decode('utf-8')
    # start_time = data[0:10]
    # stop_time = data[10:]
    # cmy = zfh(start_time, stop_time)
    xph = [1, 2, 3]
    return render_template('test/extend.html', xph=xph)
