import datetime

from db import db_session
from models import Company, Transaction, OAuth2Token, Account, CryptoTransaction, CryptoWallet
from helpers.intuit import get_refresh_token, ask_quickbooks, tell_quickbooks, query_endpoint, purchase_endpoint

def calc_doc_num(ct):
    '''
    It's our go to of the
    Max 21 characters
    First 8 are the blocknum, leading 0s
    Remaining 13 are from transaction id, removing the 0x
    '''
    doc_num = str(ct.block_num).zfill(8) + ct.tx_hash[2:15]
    return doc_num


def create_purchase_params(ct, to_account, from_account):

    '''
        {
          "AccountRef": {
            "value": "107",
            "name": "0xblah"
          },
          "PaymentType": "Cash",
          "Line": [
            {
              "Amount": 10.00,
              "DetailType": "AccountBasedExpenseLineDetail",
              "AccountBasedExpenseLineDetail": {
                "AccountRef": {
                  "value": "3"
                }
              }
            }
          ]
        }
    '''
    retval = {}
    retval["PaymentType"] = "Cash"
    account_ref = {}
    account_ref["value"] = str(from_account.intuit_id)
    retval["AccountRef"] = account_ref
    lines = []
    line0 = {}
    line0["Amount"] = ct.purchase_cost()
    line0["DetailType"] = "AccountBasedExpenseLineDetail"
    line0["Description"] = "TxHash: %s" % ct.tx_hash
    abeld = {}
    abeld["AccountRef"] = {"value": str(to_account.intuit_id)}
    line0["AccountBasedExpenseLineDetail"] = abeld
    lines.append(line0)
    retval["Line"] = lines
    retval["DocNumber"] = calc_doc_num(ct)

    return retval


def query_purchase_by_doc_num(company, doc_num, token):
    qstatement = "select count(*) from purchase where docnumber='%s'" % doc_num
    qendpoint = query_endpoint(company, qstatement)
    print(qendpoint)
    res = ask_quickbooks(company, qendpoint, token=token)
    jres = res.json()
    print(jres)
    return jres

def find_or_create_purchase_transaction(ct, to_account, from_account, token=None):
    '''
    We're assuming here that the from account is ours, and the to account is not
    '''
    company = ct.crypto_wallet.company
    if not token:
        token = get_refresh_token(company)
    print('Checking for Purchase')
    doc_num = calc_doc_num(ct)
    print('doc_num:', doc_num)
    #querying for transaction by block num, tx hash, and amount
    poss_trans = db_session.query(Transaction).filter(Transaction.doc_num==doc_num, Transaction.amount==ct.usd_amount*-1.0).first()
    qres = query_purchase_by_doc_num(company, doc_num, token)
    if qres['QueryResponse']['totalCount'] == 0:
        print('No associated Transaction from qb')
        #put on qb
        params = create_purchase_params(ct, to_account, from_account)
        endpoint = purchase_endpoint()
        print(company)
        print(endpoint)
        print(params)
        res = tell_quickbooks(company, endpoint, params, token=token)
        print(res)
        print(res.json())

def analyze_eth_transactions(company_id):
    company = db_session.query(Company).filter(Company.id==company_id).first()
    token = get_refresh_token(company) #we're getting a token here so we don't have to get a token for each query
    company_id = 9 #TODO again, hardcoding this for now
    #ct = db_session.query(CryptoTransaction).filter(CryptoTransaction.tx_id==tx_id).first()
    wallets = db_session.query(CryptoWallet).filter(CryptoWallet.company_id==company_id).all()
    print(wallets)
    for wallet in wallets:
        cts = db_session.query(CryptoTransaction).filter(CryptoTransaction.crypto_wallet_id==wallet.id).order_by(CryptoTransaction.timestamp).all()
        print(len(cts))
        for ct in cts:
            #try to find the from account, try to find the to account. One needs to be owned by us, the other an outsider
            print(ct.to_account, ct.from_account)
            #print("%%%s%%" % ct.to_account)
            #work to see if there's a quickbooks transaction associated with this ct. Based on the docnum
            to_address = ct.to_account
            to_address_like = "%%%s%%" % to_address
            from_address = ct.from_account
            from_address_like = "%%%s%%" % from_address
            #to_account = db_session.query(Account).filter(Account.name.ilike(to_address_like), Account.account_type=='Bank').first()
            #from_account = db_session.query(Account).filter(Account.name.ilike(from_address_like), Account.account_type=='Bank').first()
            to_account = db_session.query(Account).filter(Account.name.ilike(to_address_like)).first()
            from_account = db_session.query(Account).filter(Account.name.ilike(from_address_like)).first()
            print(to_account)
            print(from_account)
            if from_account and to_account:
                if from_account.account_type == 'Bank' and to_account.account_type == 'Expense': #PURCHASE
                    find_or_create_purchase_transaction(ct, to_account, from_account, token=token)
            if to_account and not from_account: #DEPOSIT
                pass
            if to_account and from_account: #TRANSFER
                pass

            #if there is, continue
            #otherwise, create that on qb
