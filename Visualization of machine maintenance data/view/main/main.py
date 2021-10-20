from flask import Blueprint, render_template, request
from function.sqlite_function import sqliteObject_to_list_s, sqliteObject_to_list_a, sqliteObject_to_list_h, \
    sqliteObject_to_list_n
import sqlite3
from settings import DATABASE_PATH

_main = Blueprint('main', __name__, url_prefix='/')


# @_main.route('/main')
# def parse1():
#     return render_template('main/main.html')
#
#
# @_main.route('/parse/ajax', methods=['POST'])
# def parse2():
#     account = request.form['account']
#
#
#     return render_template('down_and_fault/parse.html',)