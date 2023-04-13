from django.db import models
from address.models import Address
from image.models import Image
from web3 import Web3
import json
import os
from dotenv import load_dotenv

load_dotenv()


# Create your models here.

class Auction(models.Model):
    title = models.CharField(max_length=25)
    description = models.TextField()
    images = models.ManyToManyField(Image, blank=True, related_name='photos', default=None)
    start = models.DateTimeField()
    end = models.DateTimeField()
    # price in wei
    price = models.DecimalField(decimal_places=0, max_digits=99, blank=True, null=True, default=0)
    winner = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=True, null=True, default=None)
    participants = models.ManyToManyField(Address, blank=True, related_name='participants', default=None)
    hash_of_json_file = models.CharField(max_length=66, blank=True, null=True)
    hash_payment_receipt = models.CharField(max_length=66, blank=True, null=True)

    def __str__(self):
        return self.title

    def save_data(self, file):
        """save all auction informations on Ganache"""
        # take all data for connect to Ganache
        ADDRESS = os.getenv('ADDRESS')
        PRIVATE_KEY = os.getenv('PRIVATE_KEY')
        GANACHE = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
        tx_parameters = {
            'nonce': GANACHE.eth.get_transaction_count(ADDRESS),
            'chainId': GANACHE.eth.chain_id,
            'from': ADDRESS,
            'gasPrice': GANACHE.eth.gas_price,
            'to': ADDRESS,
            'gas': 42121,
            'data': file.encode()
            # not supported
            # parameters['maxPriorityFeePerGas'] = self.__GANACHE.eth.maxPriorityFeePerGas
            # parameters['maxFeePerGas'] = self.__GANACHE.eth.maxFeePerGas
        }
        # submit transaction to Ganache
        signed_transaction = GANACHE.eth.account.sign_transaction(tx_parameters, PRIVATE_KEY)
        hash_transaction = GANACHE.eth.send_raw_transaction(signed_transaction.rawTransaction)
        # save data on SQlite database
        self.hash_of_json_file = GANACHE.to_hex(hash_transaction)
        self.save()
