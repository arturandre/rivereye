# Instructions to start this

1 - Make sure the database 'rivereyedb' is created
-- Use the script 'create_rivereyedb.sh'

2 - Run:
python manage.py migrate

3 - Load the data into the database.
python manage.py shell
from userwebsite.models import load_database
load_database()
