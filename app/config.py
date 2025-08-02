class Config:
    SECRET_KEY = 'your-secret-key'
    # 在localhost后添加:3330指定端口
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3330/water_rain_data'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
