from flask_login import LoginManager
from conf.conf import app
from model.model import User


login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


login_manager.setup_app(app)
