from moralis import evm_api
import pika
import json
import os

api_key = "KE9G7lVZwm7soA1SuaQc61DnUAyrFxNI56Q5e2SsiXaX2UKvYVGXcaNHrJrqNful"

# 'eth' , 'goerli' , 'sepolia' , 'polygon' , 'mumbai' , 'bsc' , 'bsc testnet' , 'avalanche' , 'avalanche testnet' , 'fantom' , 'palm' , 'cronos' , 'cronos testnet' , 'arbitrum'

# '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB' - crypto punks - eth
# '0xea1635a0e9344d933df42c0fd494d39bce865dc4' - loaded lions - cronos
# '0x314a2F0311D184d4C5529da578390F5bED45f865'- pyscho kitties - eth
# '0x50332bdca94673F33401776365b66CC4e81aC81d'- cryptocards - bsc
# '0x306b1ea3ecdf94aB739F1910bbda052Ed4A9f949'- beanz - eth


# collections
collections = {
    'bsc': ['cryptocards'],
    'cronos': ['loaded lions'],
    'eth': ['crypto punks', 'pyscho kitties', 'beanz']

}


params = {
    "q": "",
    "chain": "",
    "format": "decimal",
    "filter": "name",
    # "from_block": 0,
    # "to_block": 0,
    # "from_date": "",
    # "to_date": "",
    # "addresses": [],
    "cursor": "",
    "limit": 100,
}

amqpHost = "amqp://localhost?connection_attempts=5&retry_delay=5"

print("AMQP_HOST: ", os.environ.get('AMQP_HOST'))

if os.environ.get('AMQP_HOST') is not None:
    amqpHost = os.environ.get('AMQP_HOST')

print("Reaching AMQP: ", amqpHost)

connection = pika.BlockingConnection(pika.URLParameters(amqpHost))

channel = connection.channel()

channel.queue_declare(queue='nfts-queue')
channel.exchange_declare(exchange='nfts-exchange',
                         exchange_type='fanout')

channel.queue_bind(exchange='nfts-exchange',
                   queue='nfts-queue')


results = []

try:
    for chain in collections:
        params['chain'] = chain
        for collectionName in collections[chain]:
            params['q'] = collectionName
            # print("Params: ", json.dumps(params, sort_keys=True, indent=4))
            results += [evm_api.nft.search_nfts(
                api_key=api_key,
                params=params,
            )]

except Exception as e:
    print("Exception collecting data from Moralis API:",
          json.dumps(e, sort_keys=True, indent=4))


for nftMetada in results:
    for res in nftMetada["result"]:
        nfmInfo = {
            "nftInfo": res
        }
        # print('sending to message queue')
        channel.basic_publish(exchange='nfts-exchange',
                              routing_key='nfts-route',
                              body=json.dumps(nfmInfo))

print('NFTs metadata processed')

connection.close()
