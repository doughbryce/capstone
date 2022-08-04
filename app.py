from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate  import Migrate
from sqlalchemy import create_engine

app = Flask(__name__)

engine = create_engine('postgresql://brycedoughman:mit12@localhost:5432/capstonedb')

@app.route('/')
def index():
    return render_template('index.html')




if __name__ == "__main__":
    app.run(debug=True)