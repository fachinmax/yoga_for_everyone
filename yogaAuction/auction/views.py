from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from auction.models import Auction, Address, Image
from django.utils import timezone
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json
from web3 import Web3
import redis
import os


# functions
def from_wei_to(wei):
    """takes the amount in wei and converts it to the nearest unit"""
    units = ['wei', 'kwei', 'mwei', 'gwei', 'microether', 'milliether', 'ether']
    final_unit = units[0]
    final_amount = wei
    for unit in units:
        amount_converted = int(Web3.from_wei(wei, unit))
        if amount_converted < 1:
            break
        else:
            final_amount = amount_converted
            final_unit = unit
    return {'unit': final_unit, 'amount': final_amount}

def get_data_auction(private_key):
    """return all information saved on redis of an auction identified by private_key parameter"""
    bids = list()
    keys = REDIS_DATABASE.keys('*')
    for key in keys:
        list_information_bid = REDIS_DATABASE.hgetall(key)
        # all information were save in bytes
        pk = int(list_information_bid.get('auction'.encode()).decode())
        if pk == private_key:
            address = list_information_bid.get('address'.encode()).decode()
            amount_wei = list_information_bid.get('wei'.encode()).decode()
            dict_information_bid = {'address': address, 'wei': amount_wei}
            bids.append(dict_information_bid)
    bids = sorted(bids, key = lambda user: (int(user['wei']), user['address']), reverse=True)
    return bids

def get_data_for_user(auctions_pk, address):
    """function for return all information to display to user"""
    # create an address with all bid informations for show up to user
    auctions = list()
    for pk in auctions_pk:
        data = list()
        bids = get_data_auction(pk)
        for bid in bids:
            if bid.get('address') == address:
                bid['auction'] = auctions_pk.get(pk)
                value = from_wei_to(int(bid.get('wei')))
                bid['wei'] = {'amount': value.get('amount'), 'unit': value.get('unit')}
                data.append(bid)
        if data:
            auctions.append(data)
    return auctions

def get_data_for_admin(auctions_pk):
    """function for return all information to display to admin"""
    auctions = list()
    for pk in auctions_pk:
        data = list()
        bids = get_data_auction(pk)
        for bid in bids:
            bid['auction'] = auctions_pk.get(pk)
            value = from_wei_to(int(bid.get('wei')))
            bid['wei'] = {'amount': value.get('amount'), 'unit': value.get('unit')}
            data.append(bid)
        if data:
            auctions.append(data)
    return auctions

def generate_json_file(auction_obj):
    """return a json file with all information to save on blockchain"""
    file = dict()
    file['winner'] = str(auction_obj.winner)
    value = from_wei_to(auction_obj.price)
    file['price'] = {'amount': value.get('amount'), 'unit': value.get('unit')}
    file['product'] = auction_obj.title
    file['description'] = auction_obj.description
    file['start'] = auction_obj.start.strftime("%d/%m/%Y, %H:%M:%S")
    file['end'] = auction_obj.end.strftime("%d/%m/%Y, %H:%M:%S")
    all_bids = get_data_auction(auction_obj.pk)
    file['number_of_bids'] = len(all_bids)
    participants = list()
    for participant in auction_obj.participants.all():
        participants.append(str(participant))
    file['participants'] = participants
    return json.dumps(file)

def address_added_to_relationship(address, auction):
    """return true if the address is already saved on participants relationship otherwise return false"""
    for participant in auction.participants.all():
        if address == str(participant):
            return True
    return False

def image_added_to_relationship(img, auction):
    """return true if the image is already saved on images relationship otherwise return false"""
    for image in auction.images.all():
        if img.name == image.name:
            return True
    return False


# Create your views here.
def index(request):
    """function for fetch all auctions and select only the active to show up to users"""
    all_objects = Auction.objects.all()
    # filter only auction that wasn't end
    auction_objects = list()
    list_images = list()
    for obj in all_objects:
        today = datetime.datetime.today().strftime("%Y%m%d%H%M%S")
        if obj.start.strftime("%Y%m%d%H%M%S") <= today and obj.end.strftime("%Y%m%d%H%M%S") >= today:
            auction_objects.append(obj)
        # the audiction was end and I don't have submit the json file to Ganache then I'm going to do. If the hash of transaction for submit the json file is already saved I don't enter in the cycle since all information were saved.
        elif obj.end.strftime("%Y%m%d%H%M%S") < today and type(obj.hash_of_json_file) is type(None):
            # send a transaction to Ganache for register the result of auction
            json_file = generate_json_file(obj)
            obj.save_data(json_file)
    data = {'auction_objects': auction_objects}
    return render(request, 'home-page.html', data)

def auction_detail(request, pk):
    """function for show up all data of a specific auction"""
    data = dict()
    auction = get_object_or_404(Auction, pk=pk)
    # auction object
    data['auction'] = auction
    data['price'] = from_wei_to(auction.price)
    # end auction. Submit the end of auction to HTML file for create a coutdown by javascript
    end_time = int(round(auction.end.timestamp()))
    data['time'] = end_time
    return render(request, 'auction-detail.html', data)

@csrf_exempt
def save_bids(request, pk, bid, address):
    """save on redis the bid get by the HTTP request"""
    global private_key_for_redis
    auction = get_object_or_404(Auction, pk=pk)
    response = dict()
    if request.method == 'POST':
        if GANACHE.is_checksum_address(address):
            if auction.price < bid:
                if GANACHE.eth.get_balance(address) >= bid:
                    # save the bid on redis
                    bid_informations = {'address': address, 'wei': bid, 'auction': pk}
                    REDIS_DATABASE.hmset(private_key_for_redis, bid_informations)
                    private_key_for_redis += 1
                    # update the highest bid
                    auction.price = bid
                    # add address to participants relationship if not exist
                    if not address_added_to_relationship(address, auction):
                        addr = Address.objects.filter(address=address)
                        if not addr:
                            addr = Address(address=address)
                            addr.save()
                        else:
                            addr = addr[0]
                        auction.participants.add(addr)
                    else:
                        addr = get_object_or_404(Address, address=address)
                    # save the highest bid address as winner
                    auction.winner = addr
                    auction.save()
                    response = {'status': 'OK', 'response': 'bid saved'}
                else:
                    response = {'status': 'ERR', 'response': "You don't have enough Ether for send a bid."}
            else:
                response = {'status': 'ERR', 'response': 'You must send higher bid.'}
        else:
            response = {'status': 'ERR', 'response': 'Address wrong.'}
    else:
        response = {'status': 'ERR', 'response': "bid didn't save. Send an POST request"}
    return JsonResponse(response, safe=False)

def get_bids(request, pk):
    """function for return all bids for a specific auction indicated by the pk parameter"""
    data = dict()
    if request.method == 'GET':
        get_object_or_404(Auction, pk=pk)
        data['status'] = 'OK'
        bids = get_data_auction(pk)
        data['response'] = bids
    else:
        data['status'] = 'ERR'
        data['response'] = 'Only GET request'
    return JsonResponse(data, safe=False)

def get_history(request, address):
    """return all information of a user or admin"""
    informations = dict()
    # I get all auction private key for get all user's bids of all user's auction
    # get all auction objects
    auction_objects = Auction.objects.all()
    # take all auctions' private key and auctions' name
    auctions_pk = dict()
    for auction in auction_objects:
        auctions_pk[auction.pk] = str(auction)
    # get informations for user
    if os.getenv('ADDRESS') != address:
        # check if address exist
        get_object_or_404(Address, address=address)
        informations['user'] = 'user'
        auctions = get_data_for_user(auctions_pk, address)
        informations['auctions'] = auctions
    # if the user is admin then return differents informations
    else:
        informations['user'] = 'admin'
        auctions = get_data_for_admin(auctions_pk)
        informations['auctions'] = auctions
    informations['address'] = address
    return render(request, 'history.html', informations)

def get_price(request, pk):
    """function for return up to data highest price in wei for a specific auction"""
    data = dict()
    if request.method == 'GET':
        auction = get_object_or_404(Auction, pk=pk)
        data['status'] = 'OK'
        data['response'] = int(auction.price)
    else:
        data['status'] = 'ERR'
        data['response'] = 'Only GET request'
    return JsonResponse(data, safe=False)

def get_auctions_winned(request, address):
    """return all auciton which the user had win"""
    if GANACHE.is_checksum_address(address):
        informations = dict()
        auctions = list()
        all_auctions = Auction.objects.all()
        for auction in all_auctions:
            today = datetime.datetime.today().strftime("%Y%m%d%H%M%S")
            end_auction = auction.end.strftime("%Y%m%d%H%M%S")
            if str(auction.winner) == address and today > end_auction and auction.hash_payment_receipt is None:
                auctions.append(auction)
        informations['auctions'] = auctions
        informations['user'] = 'user'
        informations['address'] = address
    else:
        informations['status'] = 'ERR'
        informations['response'] = 'address wrong'
    return render(request, 'auction-winned.html', informations)

@csrf_exempt
def save_hash_payament(request, hash, pk):
    """function for save the hash of payament"""
    data = dict()
    if request.method == 'POST':
        auction = get_object_or_404(Auction, pk=pk)
        auction.hash_payment_receipt = hash
        auction.save()
        data['status'] = 'OK'
        data['response'] = 'hash saved'
    else:
        data['status'] = 'ERR'
        data['response'] = 'Only POST request'
    return JsonResponse(data, safe=False)

def get_images(request, address):
    """return all apen auction"""
    informations = dict()
    informations['address'] = address
    all_objects = Auction.objects.all()
    # filter only auction that wasn't end
    auction_objects = list()
    for obj in all_objects:
        today = datetime.datetime.today().strftime("%Y%m%d%H%M%S")
        if obj.end.strftime("%Y%m%d%H%M%S") >= today:
            auction_objects.append(obj)
    informations['auctions'] = auction_objects
    return render(request, 'upload-images.html', informations)

@csrf_exempt
def upload_images(request, address, pk):
    """function for upload new images for a specific auction"""
    auction = get_object_or_404(Auction, pk=pk)
    images = request.FILES.getlist('images')
    for image in images:
        # check if the image already exist. If not I create new one. Then I have the image I check if already added to photos relationship and I add if not
        img = Image.objects.filter(name=image)
        if img:
            img = img[0]
        else:
            img = Image(name=image)
            img.save()
        if not image_added_to_relationship(img, auction):
            auction.images.add(img)
            auction.save()
    return redirect(f"/images/{address}")


# create a connection to Redis database
REDIS_DATABASE = redis.Redis(host='localhost', port=6379, db=0)
GANACHE = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
# bring the last redis private key
keys = key = REDIS_DATABASE.keys('*')
if len(keys) != 0:
    max = max(keys).decode()
    max = int(max) + 1
else:
    max = 0
private_key_for_redis = max