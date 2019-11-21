from conf.conf import app
from flasgger import Swagger
from flask_login import login_required
from flask import jsonify
from modelOp import login_manager
from modelOp.authOP import auth
from modelOp.resourceOP import resource
from modelOp.bookOP import book


login_manager.setup_app(app)
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(resource, url_prefix='/resource')
app.register_blueprint(book, url_prefix='/book')

swagger = Swagger(app)


@app.route('/secret')
@login_required
def secret():
    return "you have log"


@app.route('/')
def hello_world():
    # print(app.url_map)
    return "hello"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
