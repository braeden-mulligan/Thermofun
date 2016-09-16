import sys, os
from control_panel import db, models

def dbSeed():
	profile_default = models.Profile('DEFAULT', 20.5)
	profile_default.active = True
	db.session.add(profile_default)
	db.session.commit()

if '--force' in sys.argv:
	DBFILE = 'control_panel/mlan.db'
	if os.path.exists(DBFILE):
		os.remove(DBFILE)

db.create_all()

if '--seed' in sys.argv:
	dbSeed()
