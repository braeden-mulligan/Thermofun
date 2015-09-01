# Thermofun

## Run

1. Install prerequisites `pip install -r requirements.txt`
2. Run uwsgi -s /tmp/uwsgi.sock --module app --callable app --http :9090 --check-static /static
3. Connect via port 9090
