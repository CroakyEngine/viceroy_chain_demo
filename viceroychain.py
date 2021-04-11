# z5317289, Jiayi (Tony) Lu

from time import time
import hashlib
import json
import requests

from flask import Flask, jsonify, request
from urllib.parse import urlparse

viceroy_block_size_limit = 100
monarch_block_size_limit = 1000

class BlockChain(object):
    def __init__(self):
        self.monarch_chain = []
        self.viceroy_chain = []

        self.pending_DNS_records = []
        self.pending_transactions = []
        
        self.new_block(proof=100, previous_hash="3730A52D0459C3165262F7A003062834DC2F1D77CAFD24E61B86B89896913354")
        self.nodes = set()

    def new_block():
        pass
    
    def new_record():
        pass
    
    def new_transaction():
        pass
    
    @staticmethod
    def hash():
        pass
    
    @staticmethod
    def valid_proof():
        pass

    def register_node(self, address):
        pass

    def valid_chain():
        pass

    def resolve_conflicts(self):
        pass

    def retrieve_record(self):
        pass


app = Flask(__name__)

viceroychain = BlockChain()

# Mines the next block and upon success transfers block rewards to node address
@app.route('/mine', methods=['GET'])

# Displays the entire current chain
@app.route('/chain', methods=['GET'])

# TODO: DEBUG ONLY! REMOVE AFTER FINISHED
@app.route('/nodes', methods=['POST'])

# Registers other nodes in the network
@app.route('/nodes/register', methods=['POST'])

# Allows a user to use the blockchain to acquire IP addresses
@app.route('/records/retrieve', methods=['GET'])
