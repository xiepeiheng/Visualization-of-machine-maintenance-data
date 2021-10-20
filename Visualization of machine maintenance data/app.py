from flask import Flask 

# 引入蓝图
# 引入根页面
from view.main.main import _main

# 故障和停机
from view.down_and_fault.stoppage import _stoppage
from view.down_and_fault.down import _down
from view.down_and_fault.parse import _parse
from view.down_and_fault.contrast import _contrast

# 测试
from view.test.test1 import _test1
from view.test.test2 import _test2

app = Flask(__name__)

# 注册蓝图

# 根目录入口
app.register_blueprint(_main)

# 故障与停机部分
app.register_blueprint(_stoppage)
app.register_blueprint(_down)
app.register_blueprint(_parse)
app.register_blueprint(_contrast)

# 测试部分
app.register_blueprint(_test1)
app.register_blueprint(_test2)

if __name__ == '__main__':
    app.run(debug='on')


