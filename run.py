import sys

from jobs.etherscan import gather_transactions_for_company as gather_etherscan_transactions
from jobs.intuit.transactions import gather_transactions as gather_intuit_transactions
from jobs.intuit.crypto import analyze_eth_transactions
from jobs.intuit.accounts import gather_accounts as gather_intuit_accounts
from jobs.intuit.reports import gather_reports as gather_intuit_reports
from jobs.blockchain.seeds import seed_blockchain_transactions
from jobs.blockchain.accounts import create_and_label_wallets

from helpers.intuit import get_refresh_token
from db import db_session
from models import Company

def run_gather_etherscan_transactions(options):
    company_id = 9
    #gather_transactions_for_company(company_id)
    gather_etherscan_transactions(company_id)

def run_gather_intuit_accounts(options):
    company_id = 9
    gather_intuit_accounts(company_id)

def run_gather_intuit_reports(options):
    company_id = 9
    company = db_session.query(Company).filter(Company.id==company_id).first()
    token = get_refresh_token(company)
    start_date = '2019-01-01'
    end_date = '2020-01-01'
    report_types = ['BalanceSheet', 'ProfitAndLoss', 'CashFlow']
    for report_type in report_types:
        print('Gathering', report_type)
        gather_intuit_reports(company_id, report_type, start_date=start_date, end_date=end_date, token=token)

def run_analyze_eth_transactions(options):
    company_id = 9
    analyze_eth_transactions(company_id)

def run_gather_intuit_transactions(options):
    #TODO make these dynamic. Currently, we're hardcoding them.
    company_id = 9
    start_date = '2019-01-01'
    end_date = '2020-01-01'
    gather_intuit_transactions(company_id, start_date=start_date, end_date=end_date)

def run_seed_blockchain_transactions(options):
    seed_blockchain_transactions()

def run_create_and_label_wallets(options):
    create_and_label_wallets()

if __name__ == '__main__':
  print(sys.argv)
  command = sys.argv[1]
  options = sys.argv[2:]

  if command == 'gather_etherscan_transactions':
    run_gather_etherscan_transactions(options)
  elif command == 'gather_intuit_transactions':
    run_gather_intuit_transactions(options)
  elif command == 'gather_intuit_accounts':
    run_gather_intuit_accounts(options)
  elif command == 'gather_intuit_reports':
    run_gather_intuit_reports(options)
  elif command == 'analyze_crypto_transactions':
    run_analyze_eth_transactions(options)
  elif command == 'seed_blockchain_transactions':
    run_seed_blockchain_transactions(options)
  elif command == 'create_and_label_wallets':
    run_create_and_label_wallets(options)
  else:
    raise Exception('Unknown command {}'.format(command))

