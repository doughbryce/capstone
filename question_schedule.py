import random
import datetime
from app import Questions, db
import schedule
import time


def random_question():
    q = (random.choice(Questions.query.filter_by(date_asked=None).all()))
    q.date_asked = datetime.datetime.now()
    db.session.add(q)
    db.session.commit()
    print('new question updated')

schedule.every().day.at("06:45").do(random_question)
# schedule.every(10).seconds.do(random_question)

while True:
    schedule.run_pending()
    time.sleep(1)