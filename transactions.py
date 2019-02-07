import datetime

from db import db_session
from models import Company, Transaction, Account
from helpers.intuit import ask_quickbooks, transaction_endpoint, query_endpoint

def parse_transactions(company, jres):
    transaction_rows = jres['Rows']['Row']
    for tr in transaction_rows:
        data = tr['ColData']
        tx_date = data[0]['value']
        txn_type = data[1]['value']
        intuit_id = int(data[1]['id']) if data[1]['value'] else None
        doc_num = data[2]['value'] if data[2]['value'] else None
        is_no_post = True if data[3]['value'] == 'Yes' else False
        name = data[4]['value']
        memo = data[5]['value']
        credit_account_intuit_id = int(data[6]['id']) if data[6]['id'] else None
        credit_account = db_session.query(Account).filter(Account.intuit_id==credit_account_intuit_id).first()
        debit_account_intuit_id = int(data[7]['id']) if data[6]['id'] else None
        debit_account = db_session.query(Account).filter(Account.intuit_id==debit_account_intuit_id).first()
        account_name = data[7]['value']
        amount = float(data[8]['value']) if data[8]['value'] else 0
        transaction = db_session.query(Transaction).filter(Transaction.intuit_id==intuit_id).first()
        if not transaction:
            print('No transaction with intuit id', intuit_id)
            transaction = Transaction(intuit_id=intuit_id, created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
        else:
            print('Already a transaction with intuit id', intuit_id, '. Still updating.')
        values = dict(company_id=company.id, tx_date=tx_date, txn_type=txn_type, doc_num=doc_num, is_no_post=is_no_post, name=name, memo=memo, credit_account=credit_account, debit_account=debit_account, amount=amount)
        print(values)
        for key, value in values.items():
            setattr(transaction, key, value)
        print(transaction)
        db_session.add(transaction)
    db_session.commit()

def gather_transactions(company_id, start_date=None, end_date=None):
    company = db_session.query(Company).filter(Company.id==company_id).first()
    endpoint = transaction_endpoint(start_date=start_date, end_date=end_date)
    res = ask_quickbooks(company, endpoint)
    jres = res.json()
    parse_transactions(company, jres)

