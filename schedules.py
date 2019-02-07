#! /home/ubuntu/venvs/maio/bin/python

import threading
import time
import schedule

from run import run_gather_etherscan_transactions, run_gather_intuit_accounts, run_gather_intuit_reports, run_analyze_eth_transactions, run_gather_intuit_transactions

def run_threaded(job_func, options):
    job_thread = threading.Thread(target=job_func, args=(options,))
    job_thread.start()

#schedule.every(45).seconds.do(run_gather_intuit_accounts, None)
schedule.every(1).minutes.do(run_gather_intuit_accounts, None)
schedule.every(1).minutes.do(run_gather_etherscan_transactions, None)
schedule.every(1).minutes.do(run_analyze_eth_transactions, None)
schedule.every(1).minutes.do(run_gather_intuit_transactions, None)
schedule.every(1).minutes.do(run_gather_intuit_reports, None)
#schedule.every(1).minutes.do(seed_auditchain)

#running them all now first becuase we'd be waiting a minute
#for the first function to run
run_gather_intuit_accounts(None)
run_gather_etherscan_transactions(None)
run_analyze_eth_transactions(None)
run_gather_intuit_transactions(None)
run_gather_intuit_reports(None)
#seed_auditchain()

'''
#TODO leaving this here to see if we want to run threaded
schedule.every(1).minutes.do(run_threaded, run_gather_intuit_accounts, None)
schedule.every(1).minutes.do(run_threaded, run_gather_etherscan_transactions, None)
schedule.every(1).minutes.do(run_threaded, run_analyze_eth_transactions, None)
schedule.every(1).minutes.do(run_threaded, run_gather_intuit_transactions, None)
schedule.every(1).minutes.do(run_threaded, run_gather_intuit_reports, None)
#schedule.every(1).minutes.do(run_threaded, seed_auditchain)
'''

while 1:
    schedule.run_pending()
    time.sleep(1)







