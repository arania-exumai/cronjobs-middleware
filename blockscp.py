import binascii, codecs, datetime, hashlib, logging, os, pprint, json, re, requests, subprocess
from base64 import b64encode
from sqlalchemy import BIGINT, Boolean, Column, create_engine, DateTime, desc, Float, ForeignKey, Integer, MetaData, or_, String, Table, update  
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.utils import secure_filename

from models import Account, Transaction
from rpcutils import api



#extract an element in the response
#current_blocks = (resp['blocks'])
current_blocks = rpc_getinfo['blocks']

#extracts the full range of blocks produced
small_block = f"0-{current_blocks}"

rpc_getpeerinfo = api.getpeerinfo()
rpc_listassets = api.listassets()
rpc_listblocks = api.listblocks(small_block)
rpc_getaddresses = api.getaddresses()
rpc_multibalances = api.getmultibalances("*", "USD")

block_hash_array = []
for item in rpc_listblocks:
    block_hash_array.append(item['hash'])

testarray = list(range(0, current_blocks+1))

rpc_bareblocks = list(zip(testarray, block_hash_array))

##########################################################3
#end of flask beginigng of sqlalchemy

app = Flask(__name__)
database_url = 'postgres://zpdwrilsgqlmiu:9cbfcf3caaff842ce01ff866557c744a24af18f5da1b091af4411d5f5499a09c@ec2-184-73-222-192.compute-1.amazonaws.com:5432/dch607fni9d68p'
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

engine = create_engine(database_url, convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()

Base.query = db_session.query_property()



qbo_acct_names_unique = []

for d in db_session.query(Transaction).distinct(Transaction.debit_account_id).all():
    debits = (d.__dict__)
    quickbooks_online = (debits['debit_account_id']) 
    qbo_acct_names_unique.append(quickbooks_online)

for c in db_session.query(Transaction).distinct(Transaction.credit_account_id).all():
    credits = (c.__dict__)
    quickbooks = (credits['credit_account_id']) 
    qbo_acct_names_unique.append(quickbooks)
 
qbo_acct_names_unique.pop()
qbo_unique = list(set(qbo_acct_names_unique))
acccout_set = db_session.query(Account).all()
outer_array1 = []

for q in qbo_unique:
	for a in acccout_set:
		if q == a.id:
			inner_circle1 = {}
			inner_circle1['id'] = q
			inner_circle1['accountName'] = a.name
			json_inner1 = json.dumps(inner_circle1, indent=4, sort_keys=True, default=str)
			outer_array1.append(json_inner1) 

l = 0
while l < len(outer_array1):
#	print(outer_array1[l])
	l = l+1

#print (f'Ending Array Length: {len(outer_array1)}')

modified_addresses = json.dumps(active_addresses)
loaded_r = json.loads(modified_addresses)
resp_dict = loaded_r['Suspense (Debit)'] 

dirty_mod_accts = json.dumps(dirty_accounts)
load_r = json.loads(dirty_mod_accts)
dict_item = load_r['BTC Wallet']

entire_sets = db_session.query(Transaction).filter(Transaction.debit_account_id != None, Transaction.credit_account_id != None).all()
#largest_amount = db_session.query(Transaction).order_by(desc(Transaction.amount).limit(1)
ranked_amounts = db_session.query(Transaction).order_by(desc(Transaction.amount))

#silly_array = []
#for rnk in ranked_amounts:
#	inner_ti = {}
#	inner_ti['amount'] = rnk.amount
#	ranked_insiders = json.dumps(inner_ti, indent=4, sort_keys=True, default=str)
#	silly_array.append(ranked_insiders)
#timer = 0
#while timer < len(silly_array): 
#	print(silly_array[timer])
#	timer = timer + 1
#print (f'Transactions Ranked: {len(silly_array)}')

outer_array = []
outer_dict = {}

for key, val in outer_dict.iteritems():
for per_set in entire_sets:
	inner_circle = {}
	inner_circle['company'] = per_set.company_id
	inner_circle['transaction_id'] = per_set.id
	inner_circle['transactionDate'] = per_set.tx_date.date()
	inner_circle['transactionType'] = per_set.txn_type
	inner_circle['documentNumber'] = per_set.doc_num
	inner_circle['isPosting'] = per_set.is_no_post
	inner_circle['name'] = per_set.name
	inner_circle['description'] = per_set.memo
	inner_circle['accountCredited'] = per_set.credit_account.name
	inner_circle['addressCredited'] = load_r[per_set.credit_account.name] 
	inner_circle['accountDebited'] = per_set.debit_account.name
	inner_circle['addressDebited'] = load_r[per_set.debit_account.name] 
	inner_circle['amount'] = per_set.amount
	outer_dict.update({per_set.id : inner_circle})	
	outer_dict['per_set.id'] = inner_circle
	json_inner = json.dumps(inner_circle, indent=4, sort_keys=True, default=str)
	outer_array.append(json_inner)

for dict_page in outer_dict:
	from_address = outer_dict[dict_page]['addressCredited']
	to_address = outer_dict[dict_page]['addressDebited']
	asset = "USD"
	#amount2 = str(round((outer_dict[dict_page]['amount']), 2))
	amount = outer_dict[dict_page]['amount']
	stream = "Quickbooks Online"
	key = ((outer_dict[dict_page]['transactionDate']).strftime('%m/%d/%Y')) + "|" + (((outer_dict[dict_page]['description']).replace(" ", "")).lower()) + "|" + ((outer_dict[dict_page]['name']).replace(" ", ""))
	company = "Auditchain"
	transaction_id = str(round((outer_dict[dict_page]['transaction_id']), 1)) 
	transaction_date = (outer_dict[dict_page]['transactionDate']).strftime('%m/%d/%Y')
	transaction_type = outer_dict[dict_page]['transactionType']	
	document_number = str(round((outer_dict[dict_page]['documentNumber']), 1))
	is_posting = str(outer_dict[dict_page]['isPosting'])
	name = outer_dict[dict_page]['name']
	memo = re.sub(' +', ' ',((outer_dict[dict_page]['description']).replace(" ", "")).upper())
	account_credited = (outer_dict[dict_page]['accountCredited'].replace(" ", ""))
	account_debited = (outer_dict[dict_page]['accountDebited'].replace(" ", ""))
	if amount < 0:
		print ("negative amount detected")
		absolute_amount = abs(amount)
		blockchain_timestamp_swapped = f"multichain-cli auditchain sendwithdatafrom {from_address} {to_address} '{{\"{asset}\":{absolute_amount}}}' '{{\"for\":\"{stream}\", \"key\":\"{key}\", \"data\":{{\"json\":{{\"company\":\"{company}\",\"transaction_id\":\"{transaction_id}\",\"transaction_date\":\"{transaction_date}\",\"transaction_type\":\"{transaction_type}\",\"document_number\":\"{document_number}\",\"is_posting\":\"{is_posting}\",\"name\":\"{name}\",\"memo\":\"{memo}\",\"account_credited\":\"{account_credited}\",\"account_debited\":\"{account_debited}\"}}}}}}'"
		os.system(blockchain_timestamp_swapped)
		print ("accounts swapped succesfully")
	else: 
		blockchain_timestamp = f"multichain-cli auditchain sendwithdatafrom {to_address} {from_address} '{{\"{asset}\":{amount}}}' '{{\"for\":\"{stream}\", \"key\":\"{key}\", \"data\":{{\"json\":{{\"company\":\"{company}\",\"transaction_id\":\"{transaction_id}\",\"transaction_date\":\"{transaction_date}\",\"transaction_type\":\"{transaction_type}\",\"document_number\":\"{document_number}\",\"is_posting\":\"{is_posting}\",\"name\":\"{name}\",\"memo\":\"{memo}\",\"account_credited\":\"{account_debited}\",\"account_debited\":\"{account_credited}\"}}}}}}'"
		os.system(blockchain_timestamp)


