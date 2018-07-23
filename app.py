from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask_rq2 import RQ
from datetime import timedelta



app = Flask(__name__)

app.config['RQ_REDIS_URL'] = 'redis://localhost:6379/0'

app.config['RQ_QUEUES'] = ['default']
app.config['RQ_ASYNC'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edyst.sqlite3'
app.config['SECRET_KEY'] = "banana"
db = SQLAlchemy(app)
rq = RQ(app)

class sites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    count = db.Column(db.Integer)

    def __init__(self, url):
        self.url = url
        self.count = 0


@app.route('/insert_url/<url>', methods=['POST'])
def insert_url(url):
    site = sites(url)
    db.session.add(site)
    db.session.commit()
    add.queue(site.id)
    return 'inserted %s' % url


@app.route('/stats', methods=['GET'])
def stats():
    return render_template('stats.html', all_sites = sites.query.all())

@rq.job
def add(id):
    site = sites.query.get(id)
    resp = requests.get(site.url)
    site.count = len(resp.text.split())
    db.session.commit()

if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)
