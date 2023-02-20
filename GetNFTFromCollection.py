from moralis import evm_api
import pika
import json
import os

api_key = "KE9G7lVZwm7soA1SuaQc61DnUAyrFxNI56Q5e2SsiXaX2UKvYVGXcaNHrJrqNful"

# '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB' - crypto punks - eth
# '0xea1635a0e9344d933df42c0fd494d39bce865dc4' - loaded lions - cronos
# '0x314a2F0311D184d4C5529da578390F5bED45f865'- pyscho kitties - eth
# '0x50332bdca94673F33401776365b66CC4e81aC81d'- cryptocards - bsc
# '0x306b1ea3ecdf94aB739F1910bbda052Ed4A9f949'- beanz - eth

contractAddresses = ['0x306b1ea3ecdf94aB739F1910bbda052Ed4A9f949', '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB',
                     '0xea1635a0e9344d933df42c0fd494d39bce865dc4', '0x314a2F0311D184d4C5529da578390F5bED45f865', '0x50332bdca94673F33401776365b66CC4e81aC81d']

params = {
    "address": "",
    "chain": "eth",
    "format": "decimal",
    "limit": 100,
    "token_addresses": [],
    "cursor": "",
    "normalizeMetadata": True,
}

# params = {
#     "address": "",
#     "chain": "eth",
#     "limit": 100,
#     "cursor": "",
# }

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

# 'eth' , 'goerli' , 'sepolia' , 'polygon' , 'mumbai' , 'bsc' , 'bsc testnet' , 'avalanche' , 'avalanche testnet' , 'fantom' , 'palm' , 'cronos' , 'cronos testnet' , 'arbitrum'

chains = ['eth', 'cronos', 'bsc']

for address in contractAddresses:
    for chain in chains:
        params['address'] = address
        params['chain'] = chain
        print("Params: ", json.dumps(params, sort_keys=True, indent=4))
        results += [evm_api.nft.get_wallet_nfts(
            api_key=api_key,
            params=params,
        )]
        print("Partial: ", json.dumps(results, sort_keys=True, indent=4))

for nftMetada in results:
    for res in nftMetada["result"]:
        nfmInfo = {
            "nftInfo": res
        }
        print('sending to message queue')
        channel.basic_publish(exchange='nfts-exchange',
                              routing_key='nfts-route',
                              body=json.dumps(nfmInfo))

print('NFTs metadata processed')

connection.close()
