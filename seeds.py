import json, os, pprint, re
from models import Account, Transaction
from blockchain.rpcutils import rpcconnection
from addresses import ACTIVE_ADDRESSES
from db import db_session
from flask import Flask, jsonify

def seed_blockchain_transactions():

    print('Seeding Auditchain')

    qbo_acct_names_unique = []

    #checks for and adds all accounts with unique debit account ids to the array
    for d in db_session.query(Transaction).distinct(Transaction.debit_account_id).all():
        debits = (d.__dict__)
        quickbooks_online = (debits['debit_account_id'])
        qbo_acct_names_unique.append(quickbooks_online)

    #checks for and adds all accounts with unique credit account ids to the array  
    for c in db_session.query(Transaction).distinct(Transaction.credit_account_id).all():
        credits = (c.__dict__)
        quickbooks = (credits['credit_account_id'])
        qbo_acct_names_unique.append(quickbooks)

    #removes duplicates and inserts unique account names into an array
    qbo_unique = list(set(qbo_acct_names_unique))
    acccout_set = db_session.query(Account).all()

    #loads all active node addresses on multichain populated painstakingly by hand in ACTIVE_ADDRESSES to match syntax perfectly, into the modified_addresses
    loaded_r = ACTIVE_ADDRESSES
    print(loaded_r)
    #resp_dict = loaded_r['Suspense']

    company_id=9 #TODO hard coding company id
    transactions = db_session.query(Transaction).filter(Transaction.company_id==company_id, Transaction.debit_account_id != None, Transaction.credit_account_id != None, Transaction.tx_date>='2013-12-21').all()
    num_transactions = db_session.query(Transaction).filter(Transaction.company_id==company_id, Transaction.debit_account_id != None, Transaction.credit_account_id != None, Transaction.tx_date>='2013-12-21').count()
    print("Number of DB Transactions:", num_transactions)


    #transaction id's which are used as stream keys are coalesced into the transaction_id_array

    stream_keys = rpcconnection.liststreamkeys("Quickbooks Online")
    '''
    print (stream_keys)
    transaction_id_array = []
    print ("database populating with transaction_ids...")
    for key in stream_keys:
        print(key)
        if len(key['key']) < 5:
            transaction_id_array.append(key['key'])
    '''

    print ("database populating with transaction_ids...")
    #print(stream_keys)
    current_transactions = [key['key'] for key in stream_keys] 
    print(len(current_transactions))
    #print(current_transactions)

    # if condition ensures only new transactions are written to the blockchain by checking whether the incoming 'transaction id' from quickbooks
    # already exists as key for a previosuly published stream item

    blockchain_transaction_data = []
    num_in_blockchain = sum([1 if str(val.id) in current_transactions else 0 for val in transactions])
    print('Num transactions in blockchain:', num_in_blockchain)
    print ("Checking if Transactions qualifies as New")
    for transaction in transactions:
        transaction_id_str = str(transaction.id)
        in_id_array = transaction_id_str in current_transactions 
        f'Transaction Confirmed to Not be on Blockchain? {in_id_array}'
        if not in_id_array:
            print(transaction.credit_account)
            blockchain_staging = {}
            blockchain_staging['company'] = transaction.company_id
            blockchain_staging['transaction_id'] = transaction.id
            blockchain_staging['transactionDate'] = transaction.tx_date.date()
            blockchain_staging['transactionType'] = transaction.txn_type
            blockchain_staging['documentNumber'] = transaction.doc_num
            blockchain_staging['isPosting'] = transaction.is_no_post
            blockchain_staging['name'] = transaction.name
            blockchain_staging['description'] = transaction.memo
            blockchain_staging['accountCredited'] = transaction.credit_account.fully_qualified_name
            #blockchain_staging['addressCredited'] = loaded_r[transaction.credit_account.fully_qualified_name] 
            blockchain_staging['addressCredited'] = transaction.credit_account.wallet_address
            blockchain_staging['accountDebited'] = transaction.debit_account.fully_qualified_name
            #blockchain_staging['addressDebited'] = loaded_r[transaction.debit_account.fully_qualified_name] 
            blockchain_staging['addressDebited'] = transaction.debit_account.wallet_address
            blockchain_staging['amount'] = transaction.amount
            #blockchain_transaction_data.append(blockchain_staging)
            #outer_dict.update({transaction.id : blockchain_staging})
            print ("Metadata added to Python Dictionary")
            add_transction_to_blockchain(blockchain_staging)
    return

#for dict_page in outer_dict:
def add_transction_to_blockchain(data):
    from_address = data['addressCredited']
    to_address = data['addressDebited']
    asset = "USD"
    amount = data['amount']
    stream = "Quickbooks Online"
    key1 = (data['transactionDate']).strftime('%m/%d/%Y')
    key2 = str(round((data['transaction_id']), 1))
    company = "Auditchain"
    transaction_id = str(round((data['transaction_id']), 1)) 
    transaction_date = (data['transactionDate']).strftime('%m/%d/%Y')
    transaction_type = data['transactionType']
    if data['documentNumber']:
        s = (data['documentNumber'])
        if isinstance(s, str):
            document_number = s
        else:
            document_number = str(round(s, 1))
    else:
        document_number = ''
    is_posting = str(data['isPosting'])
    name = data['name'].replace("'", "")
    memo = re.sub(' +', ' ',((data['description']).replace(" ", "").replace("'","")).upper())
    account_credited = (data['accountCredited'].replace(" ", ""))
    account_debited = (data['accountDebited'].replace(" ", ""))
    if amount < 0:
        print ("negative amount detected, but still deposited")
        absolute_amount = abs(amount)
        blockchain_timestamp_swapped = f"sudo /usr/local/bin/multichain-cli auditchain sendwithdatafrom {from_address} {to_address} '{{\"{asset}\":{absolute_amount}}}' '{{\"for\":\"{stream}\", \"keys\":[\"{key2}\",\"{key1}\"], \"data\":{{\"json\":{{\"company\":\"{company}\",\"transaction_id\":\"{transaction_id}\",\"transaction_date\":\"{transaction_date}\",\"transaction_type\":\"{transaction_type}\",\"document_number\":\"{document_number}\",\"is_posting\":\"{is_posting}\",\"name\":\"{name}\",\"memo\":\"{memo}\",\"account_credited\":\"{account_credited}\",\"account_debited\":\"{account_debited}\"}}}}}}'"
        print (blockchain_timestamp_swapped)
        os.system(blockchain_timestamp_swapped)
        print ("accounts swapped succesfully")
    else:
        print ("positive amount detected")
        blockchain_timestamp = f"sudo /usr/local/bin/multichain-cli auditchain sendwithdatafrom {to_address} {from_address} '{{\"{asset}\":{amount}}}' '{{\"for\":\"{stream}\", \"keys\":[\"{key2}\",\"{key1}\"], \"data\":{{\"json\":{{\"company\":\"{company}\",\"transaction_id\":\"{transaction_id}\",\"transaction_date\":\"{transaction_date}\",\"transaction_type\":\"{transaction_type}\",\"document_number\":\"{document_number}\",\"is_posting\":\"{is_posting}\",\"name\":\"{name}\",\"memo\":\"{memo}\",\"account_credited\":\"{account_debited}\",\"account_debited\":\"{account_credited}\"}}}}}}'"
        print (blockchain_timestamp)
        os.system(blockchain_timestamp)
        print ("new non-swapped transaction timestamped to blockchain")


if __name__ == '__main__':
    print('Seeding from python file')
    seed_blockchain_transactions()



    '''
    #for dict_page in outer_dict:
    for data in blockchain_transaction_data:
        from_address = data['addressCredited']
        to_address = data['addressDebited']
        asset = "USD"
        amount = outer_dict[dict_page]['amount']
        stream = "Quickbooks Online"
        key1 = (outer_dict[dict_page]['transactionDate']).strftime('%m/%d/%Y')
        key2 = str(round((outer_dict[dict_page]['transaction_id']), 1))
        company = "Auditchain"
        transaction_id = str(round((outer_dict[dict_page]['transaction_id']), 1)) 
        transaction_date = (outer_dict[dict_page]['transactionDate']).strftime('%m/%d/%Y')
        transaction_type = outer_dict[dict_page]['transactionType']
        if outer_dict[dict_page]['documentNumber']:
            s = (outer_dict[dict_page]['documentNumber'])
            if isinstance(s, str):
                document_number = s
            else:
                document_number = str(round(s, 1))
        else:
            document_number = ''
        is_posting = str(outer_dict[dict_page]['isPosting'])
        name = outer_dict[dict_page]['name']
        memo = re.sub(' +', ' ',((outer_dict[dict_page]['description']).replace(" ", "")).upper())
        account_credited = (outer_dict[dict_page]['accountCredited'].replace(" ", ""))
        account_debited = (outer_dict[dict_page]['accountDebited'].replace(" ", ""))
        if amount < 0:
            print ("negative amount detected")
            absolute_amount = abs(amount)
            blockchain_timestamp_swapped = f"/usr/local/bin/multichain-cli auditchain sendwithdatafrom {from_address} {to_address} '{{\"{asset}\":{absolute_amount}}}' '{{\"for\":\"{stream}\", \"keys\":[\"{key2}\",\"{key1}\"], \"data\":{{\"json\":{{\"company\":\"{company}\",\"transaction_id\":\"{transaction_id}\",\"transaction_date\":\"{transaction_date}\",\"transaction_type\":\"{transaction_type}\",\"document_number\":\"{document_number}\",\"is_posting\":\"{is_posting}\",\"name\":\"{name}\",\"memo\":\"{memo}\",\"account_credited\":\"{account_credited}\",\"account_debited\":\"{account_debited}\"}}}}}}'"
            print (blockchain_timestamp_swapped)
            #os.system(blockchain_timestamp_swapped)
            print ("accounts swapped succesfully")
        else:
            blockchain_timestamp = f"/usr/local/bin/multichain-cli auditchain sendwithdatafrom {to_address} {from_address} '{{\"{asset}\":{amount}}}' '{{\"for\":\"{stream}\", \"keys\":[\"{key2}\",\"{key1}\"], \"data\":{{\"json\":{{\"company\":\"{company}\",\"transaction_id\":\"{transaction_id}\",\"transaction_date\":\"{transaction_date}\",\"transaction_type\":\"{transaction_type}\",\"document_number\":\"{document_number}\",\"is_posting\":\"{is_posting}\",\"name\":\"{name}\",\"memo\":\"{memo}\",\"account_credited\":\"{account_debited}\",\"account_debited\":\"{account_credited}\"}}}}}}'"
            print (blockchain_timestamp)
            #os.system('echo -e' blockchain_timestamp)
            #os.system(blockchain_timestamp)
            print ("new non-swapped transaction timestamped to blockchain")
    '''


