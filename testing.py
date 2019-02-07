from db import db_session
from helpers.intuit import create_purchase_params, query_endpoint
from models import Company, Account
from jobs.etherscan import gather_transactions_for_company

'''
company = db_session.query(Company).filter(Company.id==9).first()
paccount_name = "Cryptocurrencies"
paccount = db_session.query(Account).filter(Account.name==paccount_name).first()
ptaccount_name = "Meals & Entertainment"
ptaccount = db_session.query(Account).filter(Account.name==ptaccount_name).first()
print(company, paccount, ptaccount)

amount = 10.0

params = create_purchase_params(company, paccount, ptaccount, amount)
print(params)
'''

company = db_session.query(Company).filter(Company.id==9).first()
gather_transactions_for_company(company)
#print(company.crypto_wallets)

print(query_endpoint(company, 'select * from purchase'))

