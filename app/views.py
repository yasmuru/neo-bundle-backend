import asyncio
from neo3.api.wrappers import ChainFacade, NeoToken, GasToken
from django.http import JsonResponse


async def get_balance(request):
    facade = ChainFacade.node_provider_testnet()
    neo = NeoToken()
    gas = GasToken()
    neo_balance = await facade.test_invoke(neo.balance_of("NVsNAtHvpwpcFbd7bJs83Qai7csaPWk1ye"))
    gas_balance = await facade.test_invoke(gas.balance_of('NVsNAtHvpwpcFbd7bJs83Qai7csaPWk1ye'))
    response = {'neo balance': neo_balance, 'gas balance': gas_balance}
    return JsonResponse(response)
    