import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.BaseConfig')

db = SQLAlchemy(app)

temp_current = 0.0
temp_target = 0.0

from control_panel import models
profile_active = models.Profile.query.filter_by(active=True).first()
temp_target = profile_active.temperature
#TODO: inital poll for current temp

from control_panel import views
