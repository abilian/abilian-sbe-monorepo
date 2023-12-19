worker: ./pre_start.sh && flask worker --processes 4 --threads 1
scheduler: flask scheduler
web: gunicorn extranet.wsgi:app -b :8000 --workers 2 --log-level debug --log-file -
