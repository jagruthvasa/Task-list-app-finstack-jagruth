class Config:
    DB_USERNAME = 'root'
    DB_PASSWORD = 'password'
    DB_HOST = 'localhost'
    DB_PORT = '3306'
    DB_NAME = 'task_list_finstack'

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
