Fyyur
-----

## Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.
full crud system for venues and artists and shows .

## Development Setup

1. **Initialize and activate a virtualenv and flask migrate using:**

* first create a database called fyyur in your postgres version
* then run command : `python -m virtualenv env`
* then run command :`source env/bin/activate`
* then run command :`pip install -r requirements.txt` to Install the dependencies
* then run command :`flask db init`
* then :`flask db migrate`
* then  :`flask db upgrade` to create the tables in database.

>**Note** - In Windows, the `env` does not have a `bin` directory. Therefore, you'd use the analogous command shown below:
```
source env/Scripts/activate
```

2. **Run the development server:**
```
export FLASK_APP=run.py
export FLASK_ENV=development # enables debug mode
flask run
'''
or just run:
'''
python run.py
```

3. **Verify on the Browser**<br>
Navigate to project homepage [http://127.0.0.1:5000/](http://127.0.0.1:5000/) or [http://localhost:5000](http://localhost:5000) 

