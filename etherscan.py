import requests
from lxml import html
import datetime
import re

from models import Company, CryptoTransaction
from db import db_session

main_endpoint = 'https://etherscan.io%s'
transactions_endpoint = main_endpoint % '/txs?a=%s'

def gather_transactions_for_company(company_id):
    company = db_session.query(Company).filter(Company.id==company_id).first()
    for wallet in company.crypto_wallets:
        print(wallet)
        gather_transactions_for_wallet(wallet)

def gather_transactions_for_wallet(wallet):
    '''

    '''
    endpoint = transactions_endpoint % wallet.address #TODO we're only on ethereum now, which is why we're using etherscan

    print(endpoint)

    res = requests.get(endpoint)
    doc = html.fromstring(res.content)

    els = doc.xpath("//td//span[@class='address-tag']/a")
    txn_refs = []
    for el in els:
        href = el.attrib['href']
        if href[0:3] == '/tx':
            txn_refs.append(href)

    for ref in txn_refs:
        #search to see if we have a cryptotransaction currently in the database
        tx_hash = ref.split('/')[-1]
        ct = db_session.query(CryptoTransaction).filter(CryptoTransaction.tx_hash == tx_hash, CryptoTransaction.crypto_wallet_id==wallet.id).first()
        print(ct)
        if not ct:
            tinfo = gather_info_from_transaction(ref, es_doc=doc)
            out = True if tinfo['from'] == wallet.address else False
            ct = CryptoTransaction(crypto_wallet_id=wallet.id, tx_hash=tinfo['tx_hash'], timestamp=tinfo['timestamp'], amount=tinfo['value'][0], usd_amount=tinfo['value'][1], to_account=tinfo['to'], from_account=tinfo['from'], out=out, block_num=tinfo['block_height'], tx_cost=tinfo['actual_tx_cost'], created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
            print(ct)
            print(tinfo)
            db_session.add(ct)
            db_session.commit()

def eth_to_usd(value, **kwargs):
    '''
    Value is number of ethers
    '''
    txhash = kwargs['txhash']
    #Yeah, we're doing the dumb thing of reasking for the transaction data
    endpoint = main_endpoint % txhash
    res = requests.get(endpoint)
    old_price_re = r'LitOldPrice = "\(\$(.*?)\ \)'
    estimated_dollas_search = re.search(old_price_re, res.text)#.group(1)
    if estimated_dollas_search:
        estimated_dollas_str = estimated_dollas_search.group(1)
    else:
        #grab from the "normal" price
        price_re = r'Ether \(\$(.*?)\)'
        estimated_dollas_str = re.search(price_re, res.text).group(1)
    estimated_dollas = float(estimated_dollas_str.replace(',', ''))
    print(estimated_dollas)
    return estimated_dollas

def clean_timestamp(value, **kwargs):
    '''
    Has format of: 33 days 14 hrs ago (Dec-05-2018 05:19:40 AM +UTC)
    '''
    timestamp_string = value.text_content()
    ts = timestamp_string.split('(')[1][:-1] #-1 chops off the closing )
    tsformat = '%b-%d-%Y %H:%M:%S %p +UTC'
    return datetime.datetime.strptime(ts, tsformat)

def first_str(value, **kwargs):
    '''
      Lots of the time we just want the first part of the string
    '''
    val_text = value.text_content()
    return val_text.strip().split(' ')[0]

def first_int(value, **kwargs):
    val_text = value.text_content()
    return int(val_text.strip().split(' ')[0])

def first_float(value, **kwargs):
    val_text = value.text_content()
    return float(val_text.strip().split(' ')[0])

def costs(value, **kwargs):
    '''
    '''
    val_text = value.text_content()
    eths = float(val_text.strip().split(' ')[0])
    usds = eth_to_usd(eths, **kwargs)
    return eths, usds

def addresses(value, **kwargs):
    val_text = value.text_content()
    return val_text.strip().split(' ')[0]

label_conversion_map = {
        'TxHash': 'tx_hash',
        'TxReceipt Status': 'tx_receipt_status',
        'Block Height': 'block_height',
        'TimeStamp': 'timestamp',
        'From': 'from',
        'To': 'to',
        'Value': 'value',
        'Gas Limit': 'gas_limit',
        'Gas Used By Transaction': 'gas_used_by_transaction',
        'Gas Price': 'gas_price',
        'Actual Tx Cost/Fee': 'actual_tx_cost',
        'Nonce & ': 'nonce_position',
       }

cleaning_function_map = {
        'tx_hash': first_str,
        'tx_receipt_status': first_str,
        'block_height': first_int,
        'timestamp': clean_timestamp,
        'from': addresses,
        'to': addresses,
        'value': costs,
        'gas_limit': first_int,
        'gas_used_by_transaction': first_int,
        'gas_price': first_float,
        'actual_tx_cost': first_float,
        'nonce_position': first_int,
        }

def gather_info_from_transaction(txhash, **kwargs):
    retval = {}
    endpoint = main_endpoint % txhash
    print(endpoint)
    res = requests.get(endpoint)
    doc = html.fromstring(res.content)
    els = doc.xpath("//div[@id='ContentPlaceHolder1_maintable']/div")
    for label, value in zip(els[::2], els[1::2]):
        clean_label = label.text.strip().replace(':','')
        if clean_label in label_conversion_map.keys():
            retval_label = label_conversion_map[clean_label]
            #vtext = value.text_content()
            if retval_label in cleaning_function_map.keys():
                full_value = cleaning_function_map[retval_label](value, txhash=txhash)
            else:
                full_value = value
            retval[retval_label] = full_value
    return retval

if __name__ == '__main__':
    ttt = '33 days 14 hrs ago (Dec-05-2018 05:19:40 AM +UTC)'
    #print(clean_time_stamp(ttt))
    print(gather_transactions())
