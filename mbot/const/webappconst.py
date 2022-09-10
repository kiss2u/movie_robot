import os

from mbot.register.config_register import get_jwt_secret_key


class WebAppConst:
    def __init__(self, workdir, db_type=None, db_uri=None):
        if not db_type:
            db_type = 'sqlite'
        self.WORKDIR = workdir
        dbpath = os.path.join(workdir, "db")
        self.JSON_AS_ASCII = False
        self.JWT_TOKEN_LOCATION = ["headers", "query_string"]
        self.JWT_SECRET_KEY = get_jwt_secret_key()
        self.JWT_QUERY_STRING_NAME = 'token'
        self.SWAGGER = {
            "title": "Movie Robot API",
            "uiversion": 3,
        }
        self.SCHEDULER_API_ENABLED = False
        if db_type == 'sqlite':
            self.SQLALCHEMY_DATABASE_URI = f'sqlite:////{dbpath}/main.db?check_same_thread=False&timeout=60'
            self.SQLALCHEMY_BINDS = {
                'memory': 'sqlite://',
                'freedownload': f'sqlite:////{dbpath}/free_download.db?check_same_thread=False',
                'notify': f'sqlite:////{dbpath}/notify.db?check_same_thread=False',
                'site_data': f'sqlite:////{dbpath}/site_data.db?check_same_thread=False&timeout=60'
            }
        else:
            if not db_uri:
                raise RuntimeError(
                    '使用mysql连接方式时，需要指定数据库连接串：mysql+pymysql://<username>:<password>@<host>/<dbname>?charset=utf8')
            self.SQLALCHEMY_DATABASE_URI = db_uri
            self.SQLALCHEMY_BINDS = {
                'memory': 'sqlite://',
                'freedownload': self.SQLALCHEMY_DATABASE_URI,
                'notify': self.SQLALCHEMY_DATABASE_URI,
                'site_data': self.SQLALCHEMY_DATABASE_URI
            }
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
