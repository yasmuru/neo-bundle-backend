import asyncio
import json
import requests
from neo3.api.wrappers import ChainFacade, NeoToken, GasToken
from django.http import JsonResponse


async def get_balance(request):
    facade = ChainFacade.node_provider_mainnet()
    # neo = NeoToken()
    # gas = GasToken()
    address = request.GET.get('address', None)
    token_list = []
    # try:
    #     neo_balance = await facade.test_invoke(neo.balance_of(address))
    #     gas_balance = await facade.test_invoke(gas.balance_of(address))
    # except Exception as e:
    #     print(e)
        
    #     response = []
    #     return JsonResponse(response, safe=False)
    # print(facade.rpc_host)
    # response['data'] = {'address': address, 'quote_currency': 'USD'}
    # neo_token = {'amount': neo_balance, 'contract_address': '0xef4073a0f2b305a38ec4050e4d3d28bc40ea63f5', 'symbol': 'NEO', 'decimals': neo.decimals()}
    # gas_token = {'amount': gas_balance, 'contract_address': '0xd2a4cff31913016155e38e474a2c06d08be276cf', 'symbol': 'GAS', 'decimals': gas.decimals()}
    # gas_token['price'] = 0
    # gas_token['value'] = 0
    # url = "http://seed4t5.neo.org:20332/"
    url="http://seed1.neo.org:10332"

    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "getnep17balances",
        "params": [
            address
        ],
        "id": 1
    })
    headers = {
    'Content-Type': 'application/json'
    }

    gas_response = requests.request("POST", url, headers=headers, data=payload)
    if gas_response.status_code in {200, 201}:
        gas_json = gas_response.json()
        for asset in gas_json['result']['balance']:
            print(asset)
            contract_address = asset['assethash']
            symbol = asset['symbol']
            decimals = asset['decimals']
            amount = asset['amount']
            token = {'amount': amount, 'contract_address': contract_address, 'symbol': symbol, 'decimals': decimals}
            if symbol.lower() == 'neo':
                price_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=neo&vs_currencies=usd')
                if price_response.status_code in {200, 201}:
                    usd_json = price_response.json()
                    if neo_json:=usd_json.get('neo', None):
                        usd_value = neo_json.get('usd', 0)
                        token['price'] = usd_value
                        # price = neo_balance * usd_value
                        # token['value'] = price
            token_list.append(token)
    
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "getnep11balances",
        "params": [
            address
        ],
        "id": 1
    })
    token_response = requests.request("POST", url, headers=headers, data=payload)
    if token_response.status_code in {200, 201}:
        token_json = token_response.json()
        for asset in token_json['result']['balance']:
            print(asset)
            contract_address = asset['assethash']
            symbol = asset['symbol']
            decimals = asset['decimals']
            amount = asset.get('amount', 0)
            if asset.get('tokens', []):
                for to in asset.get('tokens'):
                    amount += float(to.get('amount', 0))
            token = {'amount': amount, 'contract_address': contract_address, 'symbol': symbol, 'decimals': decimals}
            if symbol.lower() == 'neo':
                price_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=neo&vs_currencies=usd')
                if price_response.status_code in {200, 201}:
                    usd_json = price_response.json()
                    if neo_json:=usd_json.get('neo', None):
                        usd_value = neo_json.get('usd', 0)
                        token['price'] = usd_value
                        # price = neo_balance * usd_value
                        # token['value'] = price
            token_list.append(token)     
    response = token_list
    # response['status_code'] = 200
    # response['message'] = "Balance fetched successfully!"
    return JsonResponse(response, safe=False)


def get_transactions(request):
    url = 'http://seed1.neo.org:10332'
    address = request.GET.get('address', None)
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "getnep17transfers",
        "params": [
            address
        ],
        "id": 1
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = {'address': address}
    sent_list = []
    receive_list = []
    transactions_response = requests.request("POST", url, headers=headers, data=payload)
    if transactions_response.status_code in {200, 201}:
        transactions_data = transactions_response.json()
        if transactions_data.get('result', None):
            for sent_data in transactions_data['result'].get('sent', []):
                sent_data['type'] = 'sent'
                sent_list.append(sent_data)
            for receive_data in transactions_data['result'].get('received', []):
                receive_data['type'] = 'received'
                receive_list.append(receive_data)
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "getnep11transfers",
        "params": [
            address
        ],
        "id": 1
    })
    transactions_response = requests.request("POST", url, headers=headers, data=payload)

    if transactions_response.status_code in {200, 201}:
        transactions_data = transactions_response.json()
        if transactions_data.get('result', None):
            for sent_data in transactions_data['result'].get('sent', []):
                sent_data['type'] = 'sent'
                sent_list.append(sent_data)
            for receive_data in transactions_data['result'].get('received', []):
                receive_data['type'] = 'received'
                receive_list.append(receive_data)
    activity_list = sent_list + receive_list
    activity_list = sorted(activity_list, key=lambda instance: instance['timestamp'], reverse=True)
    response['history'] = activity_list
    return JsonResponse(response)
