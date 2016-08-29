from os import path
from config import config
from sqlalchemy import create_engine, Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

db = create_engine('mysql+mysqldb://' + config['database_user'] + ':' + config['database_password'] + '@' + config['database_host'] + '/' + config['database_name'], pool_recycle = 3600, echo = False)
Base = declarative_base()

class All_IPs(Base):
    """
    @description: This table contain all ips, challenged or banned at least once by Daroyan.
    """

    __tablename__ = 'all_ips'

    id = Column(Integer, primary_key = True)
    ip = Column(String(20))

    def __init__(self, ip):
        self.ip = ip

class Banned_IPs(Base):
    """
    @description: This table contains all banned ips.
    @
    """

    __tablename__ = 'banned_ips'

    id = Column(Integer, primary_key = True)
    ip = Column(String(20))
    identifier = Column(String(40))

    def __init__(self, ip, identifier):
        self.ip = ip
        self.identifier = identifier

class Challenged_IPs(Base):
    """
    @description: This table contains all challenged ips.
    @
    """

    __tablename__ = 'challenged_ips'

    id = Column(Integer, primary_key = True)
    ip = Column(String(20))
    count = Column(Integer)
    identifier = Column(String(40))

    def __init__(self, ip, count, identifier):
        self.ip = ip
        self.count = count
        self.identifier = identifier

class UnBan_Schedule(Base):
    """
    @description: This table contains time when an IP will be unbanned.
    """

    __tablename__ = 'unban_schedule'

    id = Column(Integer, primary_key = True)
    ip = Column(String(20))
    time = Column(Float)
    identifier = Column(String(40))

    def __init__(self, ip, time, identifier):
        self.ip = ip
        self.time = time
        self.identifier = identifier

def create_database():
    parent_dir = path.dirname(path.abspath(__file__))
    database_location = path.join(parent_dir, 'daroyan.db')

    # We will check whether the database exists or not. If not, then we will create a new database.
    if not path.isfile(database_location):
        #Base.metadata.drop_all(db)
        Base.metadata.create_all(db)
    else:
        pass