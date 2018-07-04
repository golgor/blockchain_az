# -*- coding: utf-8 -*-
"""
Created on Sun Jul  1 11:15:27 2018

@author: Golgafrincham
"""

# Module 2 -Create a Cryptocurrency (RobannaCoin)

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Part 1 - Building a Blockchain

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.createBlock(proof = 1, previousHash = '0')
        self.nodes = set()

    def createBlock(self, proof, previousHash):
        block = {'index' : len(self.chain) + 1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof' : proof,
                 'previousHash' : previousHash,
                 'transactions' : self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    def getPreviousBlock(self):
        return self.chain[-1]

    def proofOfWork(self, previousProof):
        newProof = 1
        checkProof = False
        while(checkProof is False):
            hashOperation = hashlib.sha256(str(newProof**2 - previousProof**2).encode()).hexdigest()
            if(hashOperation[:4] == '0000'):
                checkProof = True
            else:
                newProof += 1
        return newProof

    def hash(self, block):
        encodedBlock = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encodedBlock).hexdigest()

    def isChainValid(self,chain):
        previousBlock = chain[0]
        blockIndex = 1
        while(blockIndex < len(chain)):
            block = chain[blockIndex]

            #Check that the 'previous hash' actually matches the hash of the previous block
            if block['previousHash'] != self.hash(previousBlock):
                return False

            # Check validity of proofs, make sure 4 leading zeroes.
            previousProof =  previousBlock['proof']
            proof = block['proof']
            hashOperation = hashlib.sha256(str(proof**2 - previousProof**2).encode()).hexdigest()

            if(hashOperation[:4] != '0000'):
                return False

            previousBlock = block
            blockIndex += 1

        return True
    
    def addTransaction(self, sender, receiver, amount):
        self.transactions.append({'sender' : sender,
                                  'receiver' : receiver,
                                  'amount' : amount})
        previousBlock = self.getPreviousBlock()
        return (previousBlock['index'] + 1)
    
    def addNode(self, address):
        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)
        
    def replaceChain(self):
        network = self.nodes
        longestChain = None
        maxLength = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/getChain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > maxLength and self.isChainValid(chain):
                    maxLength = length
                    longestChain = chain
        if longestChain:
            self.chain = longestChain
            return True
        return False
        
        
# Part 2 - Mining our Blockchain

# Creating a Web App

app = Flask(__name__)

# Creating an address for the node on Port 5000
nodeAddress = str(uuid4()).replace('-','')

# Creating a Blockchain

blockchain = Blockchain()

# Mining a block
@app.route('/mineBlock', methods = ['GET'])
def mineBlock():
    previousBlock = blockchain.getPreviousBlock()
    previousProof = previousBlock['proof']
    proof = blockchain.proofOfWork(previousProof)
    previousHash = blockchain.hash(previousBlock)
    blockchain.addTransaction(sender = nodeAddress, receiver = 'Messi', amount = '10')
    block = blockchain.createBlock(proof, previousHash)

    response = {'message' : 'Super duper awesome, you just mined a block!',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previousHash' : block['previousHash'],
                'transactions' : block['transactions']}
    return (jsonify(response), 200)

# Getting the full Blockchain
@app.route('/getChain', methods = ['GET'])
def getChain():
    response = {'chain':blockchain.chain,
                'length':len(blockchain.chain)}
    return (jsonify(response), 200)

@app.route('/checkValidity', methods = ['GET'])
def checkValidity():
    isValid = blockchain.isChainValid(blockchain.chain)
    if(isValid is True):
        response = {'message':'Everything looking ok!'}
    else:
        response = {'message':'We need to talk, something has happened!'}

    return (jsonify(response), 200)

# Adding a new transaction to the Blockchain
@app.route('/addTransaction', methods = ['POST'])
def addTransaction():
    json = request.get_json()
    transactionKeys = ['sender','receiver','amount']
    if not all (key in json for key in transactionKeys):
        return 'Some elements are missing!', 400
    index = blockchain.addTransaction(json['sender'], json['receiver'], json['amount'])
    response = {'message' : f'This transaction will be included in block {index}'}
    return jsonify(response), 201

# Decentralizing our Blockchain

# Connection new nodes
@app.route('/connectNode', methods = ['POST'])
def connectNode():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No nodes", 400
    for node in nodes:
        blockchain.addNode(node)
    response = {'message' : 'All the nodes are now connected, the chain now contains the following nodes:',
                 'totalNodes' : list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replaceChain', methods = ['GET'])
def replaceChain():
    isChainReplaced = blockchain.replaceChain()
    if(isChainReplaced is True):
        response = {'message':'The chain was replaced by the longest one!',
                    'newChain' : blockchain.chain}
    else:
        response = {'message':'The chain was the longest one!',
                    'oldChain' : blockchain.chain}

    return (jsonify(response), 200)

# Running the app
app.run(host = '0.0.0.0', port = 5003)
