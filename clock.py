from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue
from worker import conn
from seed import seed_auditchain
from intuit import gather_transactions

import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

sched = BlockingScheduler()

q = Queue(connection=conn)

def gather_intuit_transactions():
    company_id = 9
    start_date = '2018-12-01'
    end_date = '2019-01-01'
    q.enqueue(gather_transactions, company_id, start_date=start_date, end_date=end_date)

def process_transactions():
    q.enqueue(seed_auditchain)

sched.add_job(gather_intuit_transactions)
sched.add_job(gather_intuit_transactions, 'interval', seconds=20)
sched.add_job(process_transactions)
sched.add_job(process_transactions, 'interval', seconds=20)
sched.start()

