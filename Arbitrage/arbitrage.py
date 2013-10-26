import httplib
import urllib
import json
import hashlib
import hmac
import requests
from xml.etree import ElementTree
from datetime import datetime
import os
import time

from vircurex import Account
from vircurex import Pair
import btc_e_api
import mcxnowapi

def run():
    #data analysis
    order_book = {'buy':[],'sell':[]}
    #btce
    btce_ppc_btc_url = "https://btc-e.com/api/2/ppc_btc/depth"
    btce_depth_info = requests.get(btce_ppc_btc_url).json()
    for key, values in btce_depth_info.iteritems():
        if key == 'asks':
            for value in values:
                order_book['sell'].append({'price': float(value[0]), \
                    'ppc_volume': float(value[1]), \
                    'btc_volume': float(value[1]) * float(value[0]), \
                    'exchange': 'btce', \
                    'type' : 'sell'})
        elif key == 'bids':
            for value in values:
                order_book['buy'].append({'price': float(value[0]), \
                    'ppc_volume': float(value[1]), \
                    'btc_volume': float(value[1]) * float(value[0]), \
                    'exchange': 'btce', \
                    'type': 'buy'})

    #mcxnow
    mcxnow_ppc_btc_url = "https://mcxnow.com/orders?cur=PPC"
    mcxnow_depth_info = requests.get(mcxnow_ppc_btc_url)
    root = ElementTree.fromstring(mcxnow_depth_info.content)
    for child in root:
        if child.tag == 'buy':
            for element in child:
                try:
                    order_book['buy'].append({'price': float(element.find('p').text), \
                        'ppc_volume': float(element.find('c1').text), \
                        'btc_volume': float(element.find('c2').text), \
                        'exchange': 'mcxnow', \
                        'type': 'buy'})
                except:
                    pass
        if child.tag == 'sell':
            for element in child:
                try:
                    order_book['sell'].append({'price': float(element.find('p').text), \
                        'ppc_volume': float(element.find('c1').text), \
                        'btc_volume': float(element.find('c2').text), \
                        'exchange': 'mcxnow', \
                        'type': 'sell'})
                except:
                    pass

    #vircurex
    orderbook = Pair("ppc_btc").orderbook
    for key, values in orderbook.iteritems():
        if key == 'asks':
            for value in values:
                order_book['sell'].append({'price': float(value[0]), \
                    'ppc_volume': float(value[1]), \
                    'btc_volume': float(value[1]) * float(value[0]), \
                    'exchange': 'vircurex', \
                    'type' : 'sell'})
        if key == 'bids':
            for value in values:
                order_book['buy'].append({'price': float(value[0]), \
                    'ppc_volume': float(value[1]), \
                    'btc_volume': float(value[1]) * float(value[0]), \
                    'exchange': 'vircurex', \
                    'type': 'buy'})

    #compile arbitrage orders
    arbitrage_orders = {'to_buy':[], 'to_sell':[]}
    for order in order_book['sell']:
        arbitrage = False
        for other_order in order_book['buy']:
            if order['price'] < other_order['price']:
                arbitrage_orders['to_sell'].append(other_order)
                arbitrage = True
        if arbitrage:
            arbitrage_orders['to_buy'].append(order)

    fout = open("arbitrage_orderbook.txt", "a")
    fout.write(str(datetime.now()) + "\t")

    for key, orders in arbitrage_orders.iteritems():
        total_ppc_volume = 0.0
        total_btc_volume = 0.0
        for order in orders:
            fout.write(str(order) + "\t")
            total_ppc_volume += order['ppc_volume']
            total_btc_volume += order['btc_volume']
            order['cumulative_ppc_volume'] = total_ppc_volume
            order['cumulative_btc_volume'] = total_btc_volume
        fout.write("\n")

    fout.close()
<<<<<<< HEAD

  
=======
    
    #todo: generalize for > 2 exchanges
>>>>>>> 927d60ceb0c41692668813df33ab92c6e38c9d27
    buy_exchange, sell_exchange = None, None
#*********** SEE ME!!!! why bother with such a long if statement when you can just compare max/min? (Spriha)
    if len(arbitrage_orders['to_sell']) > 0 and \
            arbitrage_orders['to_sell'][-1]['cumulative_ppc_volume'] >= \
            arbitrage_orders['to_buy'][-1]['cumulative_ppc_volume']:
        ppc_volume = arbitrage_orders['to_buy'][-1]['cumulative_ppc_volume']
        for order in arbitrage_orders['to_sell']: #explain, didn't quite get this part here (Spriha)
            if order['cumulative_ppc_volume'] >= ppc_volume: #if the ask order (in terms of ppc) is more than the bid order
                sell_price = order['price']
                break
        #highest bid price
        buy_price = arbitrage_orders['to_buy'][0]['price']
        buy_exchange = arbitrage_orders['to_buy'][0]['exchange']    
        sell_exchange = arbitrage_orders['to_sell'][0]['exchange']
    elif len(arbitrage_orders['to_sell']) > 0:
        ppc_volume = arbitrage_orders['to_sell'][-1]['cumulative_ppc_volume']
        for order in arbitrage_orders['to_buy']:
            if order['cumulative_ppc_volume'] >= ppc_volume:
                buy_price = order['price']
        #lowest ask price
        sell_price = arbitrage_orders['to_sell'][-1]['price']        
        buy_exchange = arbitrage_orders['to_buy'][0]['exchange']    
        sell_exchange = arbitrage_orders['to_sell'][0]['exchange']

    #todo: add transaction fees into consideration
    #trading
    #execution variables:
    #ppc_volume
    #buy_price
    #buy_exchange
    #sell_price
    #sell_exchange

    #todo: multiprocessing here (initiate both trades at the same time)
    #mcxnow
    if buy_exchange != None and sell_exchange != None:
        #get account balances
        #mcxnow
        mcxnow_user = os.environ['mcxnow_user']
        mcxnow_pass = os.environ['mcxnow_pass']
        S = mcxnowapi.McxNowSession(mcxnow_user, mcxnow_pass)
        mcxnow_user_details = S.GetUserDetails()
        mcxnow_ppc_balance = [i[1] for i in mcxnow_user_details if i[0] == 'PPC'][0]
        mcxnow_btc_balance = [i[1] for i in mcxnow_user_details if i[0] == 'BTC'][0]
        #vircurex
        vircurex_key = os.environ['vircurex_key']
        vircurex_user = os.environ['vircurex_user']
        account = Account(vircurex_user, vircurex_key)
        vircurex_ppc_balance = account.balance('ppc')
        vircurex_btc_balance = account.balance('btc')
        #btce
        btce_access_key = os.environ['btce_access_key']
        btce_secret_access_key = os.environ['btce_secret_key']
        try:
            nonce_file = open('nonce.txt', 'r')
            nonce = int(nonce_file.readline().strip())
            nonce_file.close()
        except:
            nonce = 1
        btce = btc_e_api.API(btce_access_key,\
            btce_secret_access_key, nonce=nonce)
        new_nonce_file = open('nonce.txt', 'w')
        new_nonce_file.write(str(nonce + 1))
        new_nonce_file.close()
        response = btce.get_info()
        print response
        btce_ppc_balance = response["return"]["funds"]["ppc"]
        btce_btc_balance = response["return"]["funds"]["btc"] 

        #todo: generalize for > 2 exchanges
        #calculate new ppc volume
        #vircurex and btce
        '''
        if buy_exchange == 'vircurex':
            ppc_volume_buy_limit = float(vircurex_btc_balance) / float(buy_price)
            ppc_volume = min(btce_ppc_balance, ppc_volume, ppc_volume_buy_limit)
        elif sell_exchange == 'vircurex':
            ppc_volume_buy_limit = float(btce_btc_balance) / float(buy_price)
            ppc_volume = min(vircurex_ppc_balance, ppc_volume, ppc_volume_buy_limit)
        '''
        #mcxnow and btce
        if buy_exchange == 'mcxnow':
            ppc_volume_buy_limit = float(mcxnow_btc_balance) / float(buy_price)
            ppc_volume = min(btce_ppc_balance, ppc_volume, ppc_volume_buy_limit)
        elif sell_exchange == 'mcxnow':
            ppc_volume_buy_limit = float(btce_btc_balance) / float(buy_price)
            ppc_volume = min(mcxnow_ppc_balance, ppc_volume, ppc_volume_buy_limit)
        #truncate ppc_volume to second decimal place
        ppc_volume = '%.2f' % ppc_volume
        print ppc_volume

        #mcxnow
        if buy_exchange == 'mcxnow' or sell_exchange == 'mcxnow':
            S = mcxnowapi.McxNowSession(mcxnow_user, mcxnow_pass)
            if buy_exchange == 'mcxnow':
                order = S.SendBuyOrder('PPC', ppc_volume, buy_price, 0)
            if sell_exchange == 'mcxnow':
                order = S.SendSellOrder('PPC', ppc_volume, sell_price, 0)
            print order, S.ErrorCode
            if order == 1:                
                result = S.ExecuteOrder('PPC', S.Return[0])
                print result, S.ErrorCode

        #vircurex
        if buy_exchange == 'vircurex' or sell_exchange == 'vircurex':
            if buy_exchange == 'vircurex':
                order = account.buy("PPC", ppc_volume, "BTC", buy_price)
            if sell_exchange == 'vircurex':
                order = account.sell("PPC", ppc_volume, "BTC", sell_price)
            print order
            result = account.release_order(order["orderid"])
            print result
            
        #btce
        if buy_exchange == 'btce' or sell_exchange == 'btce':
            if buy_exchange == 'btce':
                result = btce.trade('buy', ppc_volume, 'ppc_btc', buy_price)
            elif sell_exchange == 'btce':
                result = btce.trade('sell', ppc_volume, 'ppc_btc', sell_price)
            print result

if __name__ == '__main__':
    #starting balances
    #btce
    #btc=1.01417533
    #ppc=1355.91890139
    #mcxnow
    #btc=1.16494221
    #ppc=926.749068
    #exchange rate (according to coinmarketcap.com):
    #btc-usd=147.17
    #ppc-usd=0.32
    while True:
        print "new poll"
        try:
            run()
            time.sleep(15.0)
        except:
            print "Exception"
            nonce_file = open('nonce.txt', 'r')
            nonce = int(nonce_file.readline().strip())
            nonce_file.close()
            new_nonce_file = open('nonce.txt', 'w')
            new_nonce_file.write(str(nonce + 1))
            new_nonce_file.close()
            time.sleep(60.0)






