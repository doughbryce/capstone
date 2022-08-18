import random
import datetime
from app import Questions, AskedQuestions, db
import schedule
import time


def random_question():
    q = (random.choice(Questions.query.all()))
    asked_q = AskedQuestions(question=q.question, original_id=q.question_id)
    now = datetime.datetime.now()
    q.date_asked = now
    db.session.add(asked_q)
    db.session.commit()
    print('new question updated')

schedule.every().day.at("05:00").do(random_question)
# schedule.every(10).seconds.do(random_question)

while True:
    schedule.run_pending()
    time.sleep(10)