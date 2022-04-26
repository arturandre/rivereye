service postgresql start

echo "Waiting for db.."
/root/miniconda3/bin/python manage.py check --database default
until [ $? -eq 0 ];
do
  sleep 2
  /root/miniconda3/bin/python manage.py check --database default
done
echo "Connected."

/root/miniconda3/bin/python manage.py runserver 0:8000 --noreload