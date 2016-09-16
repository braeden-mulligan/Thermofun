from control_panel import db

# Temperatures should be stored rounded to nearest tenth

class Profile(db.Model):
	__tablename__="profiles"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True, nullable=False)
	active = db.Column(db.Boolean, nullable=False)
	temperature = db.Column(db.Float)
	schedules = db.relationship('Schedule', backref='profile', lazy='dynamic')
	def __init__(self, name, temp):
		self.name = name
		self.active = False
		if not temp:
			self.temperature = 20
		else:
			self.temperature = temp
	def __repr__(self):
		return '<Profile %r>' % self.name

class Schedule(db.Model):
	__tablename__="schedules"
	id = db.Column(db.Integer, primary_key=True)
	temperature = db.Column(db.Float)
	time = db.Column(db.Integer, unique=True)
	profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'))
	def __init__(self, temperature, time):
		self.temperature = temperature
# Avoid check-at-00:00 bugs in hardware controller.
		if not time:
			time = 1
		else:
			self.time = time
	def __repr__(self):
		return '<Associated Profile %r>' % self.profile_id
