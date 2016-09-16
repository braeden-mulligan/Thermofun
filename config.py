import os
basedir = os.path.abspath(os.path.dirname(__name__))

class BaseConfig(object):
	SQLALCHEMY_DATABASE_URI = 'sqlite:///mlan.db'
# Supress v2.1 warnings.
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	DEBUG = True

