from flask import Flask, jsonify
from blockchain.rpcutils import rpcconnection
import os

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
host = os.environ.get('IP', '0.0.0.0')
port = int(os.environ.get('PORT', 5000))

def get_current_blocks():
    rpc_getinfo = rpcconnection.getinfo()
    return rpc_getinfo['blocks']

def get_small_block():
    current_blocks = get_current_blocks()
    return f"0-{current_blocks}"

@app.route('/')
def index():
    rpc_getinfo = rpcconnection.getinfo()
    return jsonify(rpc_getinfo), 200

@app.route('/getpeerinfo')
def getpeerinfo():
    rpc_getpeerinfo = rpcconnection.getpeerinfo()
    return jsonify(rpc_getpeerinfo), 200

@app.route('/getaddresses')
def getaddresses():
    rpc_getaddresses = rpcconnection.getaddresses()
    return jsonify(rpc_getaddresses), 200

@app.route('/listassets')
def listassets():
    rpc_listassets = rpcconnection.listassets()
    return jsonify(rpc_listassets), 200

@app.route('/listblocks')
def listblocks():
    small_block = get_small_block()
    rpc_listblocks = rpcconnection.listblocks(small_block)
    return jsonify(rpc_listblocks), 200

@app.route('/bareblocks')
def bareblocks():
    small_block = get_small_block()
    rpc_listblocks = rpcconnection.listblocks(small_block)
    block_hash_array = []
    for item in rpc_listblocks:
        block_hash_array.append(item['hash'])
    current_blocks = get_current_blocks()
    testarray = list(range(0, current_blocks+1))
    rpc_bareblocks = list(zip(testarray, block_hash_array))
    return jsonify(rpc_bareblocks), 200

@app.route('/multibalances')
def multibalances():
    rpc_multibalances = rpcconnection.getmultibalances("*", "USD")
    return jsonify(rpc_multibalances), 200

@app.route('/liststreamkeyitems')
def liststreamkeyitems():
	rpc_liststreamkeyitems = rpcconnection.liststreamkeyitems("Quickbooks Online", "1636")
	return jsonify(rpc_liststreamkeyitems), 200

if __name__ == '__main__':
    app.run(host=host, port=port)




