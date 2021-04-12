# Jiayi (Tony) Lu, 12th of April, 2021
# Viceroy Chain - a demonstration blockchain solution to DNS records keeping in python3

from time import time
import hashlib
import json
import requests

from flask import Flask, jsonify, request
from urllib.parse import urlparse
from uuid import uuid4

viceroy_block_size_limit = 100
monarch_block_size_limit = 1000
mining_reward = 30
minting_cost = 5
hash_difficulty = 6

class BlockChain(object):
    def __init__(self):
        self.monarch_chain = []
        self.viceroy_chain = []
        self.pending_records = []
        self.pending_transactions = []
        self.new_monarch_block(proof=100, previous_hash="3730A52D0459C3165262F7A003062834DC2F1D77CAFD24E61B86B89896913354")
        self.nodes = set()

    def new_monarch_block(self, proof, previous_hash=None, previous_viceroy_hash=None):
        # Collect transactions up to block limit
        buffer = [t for i, t in enumerate(self.pending_transactions) if i <= monarch_block_size_limit]

        # Chain last viceroy block to Monarch block if exists
        last_viceroy_ind = 0
        prev_vice_hash = "0"
        if len(self.viceroy_chain) > 0:
            last_viceroy_ind = self.last_viceroy_block['index']
            prev_vice_hash = self.hash(self.last_viceroy_block())

        block = {
            'index': len(self.monarch_chain) + 1,
            'timestamp': time(),
            'records': buffer,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.monarch_chain[-1]),
            'last_viceroy_block_index': last_viceroy_ind,
            'last_viceroy_block_hash': prev_vice_hash
        }

        # Remove transactions added to block from pending_transactions
        self.pending_transactions = [i for i in self.pending_transactions[monarch_block_size_limit:]]
        self.monarch_chain.append(block)

    def new_viceroy_block(self, proof, previous_hash=None, monarch_hash=None):
        # Collect records up to block limit
        buffer = [t for i, t in enumerate(self.pending_records) if i <= viceroy_block_size_limit]

        block = {
            'index': len(self.viceroy_chain) + 1,
            'timestamp': time(),
            'records': buffer,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.viceroy_chain[-1]),
            'authorised_monarch_block_index': self.last_monarch_block['index'],
            'authorised_monarch_hash': monarch_hash or self.hash(self.monarch_chain[-1])
        }

        # Remove records added to block from pending_records
        self.pending_records = [i for i in self.pending_records[viceroy_block_size_limit:]]
        self.viceroy_chain.append(block)
    
    def new_transaction(self, sender, recipient, amount):
        self.pending_transactions.append({
            'sender' : sender,
            'recipient' : recipient,
            'amount' : amount
        })

        return self.last_monarch_block['index'] + 1

    # Adds new DNS records into the blockchain
    def new_record(self, r_type, hostname, IP_address, TTL, auth_signature):
        live_date = time() + TTL

        self.pending_records.append({
            'record_type' : r_type,
            'hostname' : hostname,
            'IP_address' : IP_address,
            'live_date' : live_date,
            'domain_owner_signature' : auth_signature
        })
        
        return self.last_viceroy_block['index'] + 1
    
    # Checks if conditions satisfy for new DNS record to be added
    def record_minting(self, address):
        if self.check_balance(address) >= minting_cost:
            viceroychain.new_transaction(node_identifier, "0", minting_cost)
            return True
        return False
    
    # TODO: Checks the balance of the local node address as acknowledged on the chain
    def check_balance(self, address):
        return 1000

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def proof_of_work(self, last_monarch_proof, last_viceroy_proof):
        proof = 0
        while self.valid_proof(last_monarch_proof, last_viceroy_proof, proof) is False:
            proof += 1
        
        return proof

    # Only hashes the proof of work value rather than entire block
    @staticmethod
    def valid_proof(last_proof1, last_proof2, proof):
        guess = f'{last_proof1}{last_proof2}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:hash_difficulty] ==  '0' * hash_difficulty
    
    @property
    def last_monarch_block(self):
        return self.monarch_chain[-1]
    
    @property
    def last_viceroy_block(self):
        try:
            return self.viceroy_chain[-1]
        except:
            return None

    # Add new nodes' IP addresses to nodes set
    def register_node(self, address):
        parsed_url = urlparse(address)
        # Ensures only the base net address is used, and not paths
        self.nodes.add(parsed_url.netloc)

    # Checks for the validity of the monarch chain
    def valid_monarch_chain(self, monarch_chain, viceroy_chain):
        last_block = monarch_chain[0]
        current_index = 1
        vice_cha_len = len(viceroy_chain)

        while current_index < len(monarch_chain):
            block = monarch_chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n=-=-=-=-=-=-=-=-=-=-=\n")
            # * Check if monarch chain's hashes are correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            # * Check if linked viceroy block is also valid
            elif vice_chain_len > 0 and block['last_viceroy_block_hash'] != self.hash(viceroy_chain[block['last_viceroy_block_hash']]):
                return False
            
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            
            last_block = block
            current_index += 1
    
        return True
    
    # Requires the monarch chain to be validated first as it's linked to monarch chain
    def valid_viceroy_chain(self, chain):
        pass

    def resolve_conflicts(self):
        """
            Resolves conflicts between local node's chain and other registered chains
        """
        neighbours = self.nodes
        new_monarch_chain = None
        new_viceroy_chain = None

        max_monarch_chain = len(self.monarch_chain)
        max_viceroy_chain = len(self.viceroy_chain)

        # Compares length of monarch chain
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                monarch_length = response.json()['monarch_length']
                viceroy_length = response.json()['viceroy_length']
                monarch_chain = response.json()['monarch_chain']
                vice_chain = response.json()['viceroy_chain']

                # Replace chain if new monarch chain greater
                if monarch_length > max_monarch_chain and self.valid_monarch_chain(monarch_chain):
                    max_monarch_chain = monarch_length
                    max_viceroy_chain = viceroy_length
                    new_monarch_chain = monarch_chain
                    new_viceroy_chain = vice_chain
                # Replace chain if monarch chain equal, but greater viceroy chain
                elif monarch_length == max_monarch_chain and self.valid_monarch_chain(monarch_chain):
                    if viceroy_length > max_viceroy_length:
                        max_monarch_chain = monarch_length
                        max_viceroy_chain = viceroy_length
                        new_monarch_chain = monarch_chain
                        new_viceroy_chain = vice_chain
        
        # If new chain has authority, replaces old chain
        if new_monarch_chain:
            self.monarch_chain = new_monarch_chain
            self.viceroy_chain = new_viceroy_chain
            return True

        return False

    # Searches through records to find matching hostname and check if service is currently live
    # Loops from the end of the list so the most recent version of the record will be used
    def retrieve_record(self, hostname):
        curr_time = time()
        iter_len = len(self.viceroy_chain)

        for i in range(iter_len - 1, -1, -1):
            record = self.viceroy_chain[i]
            if record.get("hostname") == hostname and record.get("live_date") <= curr_time:
                return record
            
        return None


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
# * Address '0' belongs to the blockchain

viceroychain = BlockChain()

# Adding new record would automatically incur a fee of x monarchs.
# After checking the balance of current node address, upon sufficient funds
# the addition of a new record will be allowed.
# Both transactions and records list will be added to.
# TODO: 
@app.route('/records/new', methods=['POST'])
def new_record():
    values = request.get_json()
    required = ["r_type", "hostname", "IP_address", "TTL", "auth_signature"]
    if not all(k in values for k in required):
        return 'Missing values', 400
    
    address = node_identifier
    if viceroychain.record_minting(address):
        index = viceroychain.new_record(values['r_type'], values['hostname'], values['IP_address'], values['TTL'], values['auth_signature'])
        response = {'message': f'Record will be added to Block {index} authorised by {minting_cost} Monarchs'}
        return jsonify(response), 201
    else:
        response = {'message': f'Insufficient funds under current node address. {minting_cost} Monarchs required to authorise a new record.'}
        return jsonify(response), 200

# TODO: 
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    
    index = viceroychain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Record will be added to Block {index}'}
    return jsonify(response), 201

# Mines the next block and upon success transfers block rewards to node address
# TODO: 
@app.route('/mine', methods=['GET'])
def mine():
    last_monarch = viceroychain.last_monarch_block
    last_viceroy = viceroychain.last_viceroy_block
    monarch_proof = last_monarch['proof']
    viecroy_proof = last_viceroy['proof']
    proof = viceroychain.proof_of_work(monarch_proof, viecroy_proof)

    viceroychain.new_transaction("0", node_identifier, mining_reward)

    # Compares length of viceroy chain and monarch chain
    # If both exceeds max_block_size, monarch chain takes precedence
    # Otherwise, mine block for largest amount of data
    monarch_len = len(viceroychain.monarch_chain)
    viceroy_len = len(viceroychain.viceroy_chain)

    previous_hash = viceroychain.hash(last_monarch)
    previous_viceroy_hash = viceroychain.hash(last_viceroy)
    block = {}
    
    if monarch_len >= monarch_block_size_limit:
        block = viceroychain.new_monarch_block(proof, previous_hash, previous_viceroy_hash)
    elif viceroy_len >= viceroy_block_size_limit:
        block = viceroychain.new_viceroy_block(proof, previous_viceroy_hash, previous_hash)
    elif monarch_len >= viceroy_len:
        block = viceroychain.new_monarch_block(proof, previous_hash, previous_viceroy_hash)
    else:
        block = viceroychain.new_viceroy_block(proof, previous_viceroy_hash, previous_hash)

    # Return summary of block
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'records': block['records'],
        'proof': block['proof'],
        'previous_hash': block.get('previous_hash') or block.get('previous_viceroy_hash'),
        'previous_secondary_hash': block.get('previous_hash') or block.get('previous_viceroy_hash')
    }
    return jsonify(response), 200

# Displays the entire current viceroy chain (DNS records)
# Displays the entire current monarch chain (Monarch coin transaction)
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'monarch_chain': viceroychain.monarch_chain,
        'viceroy_chain': viceroychain.viceroy_chain,
        'monarch_length': len(viceroychain.monarch_chain),
        'viceroy_length': len(viceroychain.viceroy_chain),
    }
    return jsonify(response), 200

# TODO: DEBUG ONLY! REMOVE AFTER FINISHED
@app.route('/nodes', methods=['GET'])
def get_nodes():
    response = {
        'total_nodes': list(viceroychain.nodes),
    }
    return jsonify(response), 200

# Registers other nodes in the network
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    
    for node in nodes:
        viceroychain.register_node(node)
    
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(viceroychain.nodes),
    }
    return jsonify(response), 201
    
# Monarch chain takes precedence, then Viceroy chain
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = viceroychain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_monarch_chain': viceroychain.monarch_chain,
            'new_viceroy_chain': viceroychain.viceroychain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'monarch_chain': viceroychain.monarch_chain,
            'viceroy_chain': viceroychain.viceroychain
        }
    return jsonify(response), 200

# Allows a user to use the blockchain to acquire IP addresses
@app.route('/records/retrieve', methods=['GET'])
def retrieval():
    values = request.get_json()
    hostname = values.get('hostname')
    result = viceroychain.retrieve_record(hostname)
    
    if result is not None:
        record = {
            'record_type' : result['record_type'],
            'hostname' : result['hostname'],
            'IP_address' : result['IP_address'],
            'live_date' : result['live_date'],
            'domain_owner_signature' : result['domain_owner_signature']
        }
        response = {
            'message' : 'Your hostname has been successfully found!',
            'IP_address' : result['IP_address'],
            'record' : record
        }
    else:
        response = {
            'message' : 'Your hostname could not be found :(',
            'IP_address' : '0.0.0.0',
            'record' : {}
        }
    
    return jsonify(response), 200

if __name__=='__main__':
    # TODO: CHANGE PORT TO 0
    app.run(port=33767)