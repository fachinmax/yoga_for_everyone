from web3 import Web3
import json
import os
from dotenv import load_dotenv
from solcx import compile_standard, install_solc

load_dotenv()


class SmartContract:
    def __init__(self, product_name=None, duration=None, address=None):
        """create a SmartContract object that communicate with a specific smart contract deployed on ganache. If a smart contract wasn't deployed (hash = None) then I'm going to deploy"""
        self.__ADDRESS_SELLER = os.getenv('ADDRESS')
        self.__PRIVATE_KEY_SELLER = os.getenv('PRIVATE_KEY')
        self.__GANACHE = self.__inizialize_connection()
        abi = self.__get_smart_contract_abi()
        if address == None:
            bytecode = self.__get_smart_contract_bytecode()
            # product_name and duration parameters are smart contract parameters
            self.__SMART_CONTRACT_HASH = self.__deploy_smart_contract(abi, bytecode, product_name, duration)
        else:
            self.__SMART_CONTRACT_HASH = address
        # create object for connect with smart contract
        self.__SMART_CONTRACT = self.__GANACHE.eth.contract(abi=abi, address=self.__SMART_CONTRACT_HASH)

    def __inizialize_connection(self):
        """inizialize connection with ganache blockchain"""
        return Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

    def __get_smart_contract_abi(self):
        """fetch and return abi of the smart contract"""
        with open('../yogaAuctionSmartContract/build/contracts/YogaAuction.json') as file:
            smart_contract_file = file.read()
        smart_contract_json = json.loads(smart_contract_file)
        return smart_contract_json['abi']
    
    def __get_smart_contract_bytecode(self):
        """fetch and return bytecode of the smart contract"""
        with open('../yogaAuctionSmartContract/build/contracts/YogaAuction.json') as file:
            smart_contract_file = file.read()
        smart_contract_json = json.loads(smart_contract_file)
        return smart_contract_json['bytecode']

    def __deploy_smart_contract(self, abi, bytecode, product_name, duration):
        """deploy a smart contract and return its hash"""
        # Create the contract in Python
        smart_contract = self.__GANACHE.eth.contract(abi=abi, bytecode=bytecode)
        # build transaction
        transaction = smart_contract.constructor(product_name, duration).build_transaction(self.__get_transaction_parameters())
        transaction_receipt = self.__send_transaction(transaction)
        return transaction_receipt.contractAddress

    def __get_transaction_parameters(self):
        """return paramenter for build a new function"""
        return {
            'nonce': self.__GANACHE.eth.get_transaction_count(self.__ADDRESS_SELLER),
            'chainId': self.__GANACHE.eth.chain_id,
            'from': self.__ADDRESS_SELLER,
            'gasPrice': self.__GANACHE.eth.gas_price
        }

    def __send_transaction(self, transaction):
        """sign, send and return receipt transaction"""
        sign_transaction = self.__GANACHE.eth.account.sign_transaction(transaction, self.__PRIVATE_KEY_SELLER)
        hash_transaction = self.__GANACHE.eth.send_raw_transaction(sign_transaction.rawTransaction)
        return self.__GANACHE.eth.wait_for_transaction_receipt(hash_transaction)

    def start_auction(self):
        """start the auction"""
        transaction = self.__SMART_CONTRACT.functions.startedAuction().build_transaction(self.__get_transaction_parameters())
        self.__send_transaction(transaction)
    
    def bid(self):
        """send new bid"""
        transaction = self.__SMART_CONTRACT.functions.bid().build_transaction(self.__get_transaction_parameters())
        self.__send_transaction(transaction)
    
    def get_remainingTime(self):
        """return the remaining time of audience"""
        return self.__SMART_CONTRACT.functions.remainingTime().call({'from': self.__ADDRESS_SELLER})

    def withdraw(self):
        """send all ether to all user that have partecipated to auction"""
        transaction = self.__SMART_CONTRACT.functions.withdraw().build_transaction(self.__get_transaction_parameters())
        transaction_receipt = self.__send_transaction(transaction)

    def get_product_name(self):
        """return product name"""
        return self.__SMART_CONTRACT.functions.idName().call({'from': self.__ADDRESS_SELLER})

    def get_end(self):
        """return the end of audience"""
        return self.__SMART_CONTRACT.functions.end().call({'from': self.__ADDRESS_SELLER})

    def get_highest_bid(self):
        """return the higest bid"""
        return self.__SMART_CONTRACT.functions.highestBid().call({'from': self.__ADDRESS_SELLER})

    def get_highest_bidder(self):
        """return the address of the highest bidder"""
        return self.__SMART_CONTRACT.functions.highestBidder().call({'from': self.__ADDRESS_SELLER})

    def get_total_duration(self):
        """return the total duration of the auction"""
        return self.__SMART_CONTRACT.functions.duration().call({'from': self.__ADDRESS_SELLER})

    def get_bidders(self, position):
        """return the address of a bidder"""
        return self.__SMART_CONTRACT.functions.bidders(position).call({'from': self.__ADDRESS_SELLER})
    
    def get_amount_bid(self, address):
        """return the amount of ether that a specific user had bid"""
        amount_wei = self.__SMART_CONTRACT.functions.participantsBids(address).call({'from': self.__ADDRESS_SELLER})
        return Web3.from_wei(amount_wei, 'ether')

    def get_status(self):
        """return the status of the auction; it can be: NoReady, Start or End"""
        status = self.__SMART_CONTRACT.functions.status().call({'from': self.__ADDRESS_SELLER})
        if status == 0:
            return 'NoReady'
        elif status == 1:
            return 'Start'
        else:
            return 'End'
    
    def get_hash_address(self):
        """return the smart contract address hash"""
        return self.__SMART_CONTRACT_HASH

    def send_json_file(self, file):
        """get a json file and return the hash of transaction"""
        parameters = self.__get_transaction_parameters()
        parameters['to'] = self.__ADDRESS_SELLER
        parameters['gas'] = 42121
        parameters['data'] = file.encode()
        # not supported
        # parameters['maxPriorityFeePerGas'] = self.__GANACHE.eth.maxPriorityFeePerGas
        # parameters['maxFeePerGas'] = self.__GANACHE.eth.maxFeePerGas
        signed_transaction = self.__GANACHE.eth.account.sign_transaction(parameters, self.__PRIVATE_KEY_SELLER)
        hash_transaction = self.__GANACHE.eth.send_raw_transaction(signed_transaction.rawTransaction)
        return self.__GANACHE.to_hex(hash_transaction)
