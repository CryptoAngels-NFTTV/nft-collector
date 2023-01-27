from moralis import evm_api
import pika,json,os

api_key = "KE9G7lVZwm7soA1SuaQc61DnUAyrFxNI56Q5e2SsiXaX2UKvYVGXcaNHrJrqNful"
params = {
    "address": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",
    "chain": "eth",
    "format": "decimal",
    "limit": 1,
    "token_addresses": [],
    "cursor": "",
    "normalizeMetadata": True,
}

amqpHost = "amqp://localhost?connection_attempts=5&retry_delay=5"

print("AMQP_HOST: ", os.environ.get('AMQP_HOST'))

if os.environ.get('AMQP_HOST') is not None:
    amqpHost = os.environ.get('AMQP_HOST');    
    
print("Reaching AMQP: ", amqpHost)

connection = pika.BlockingConnection(pika.URLParameters(amqpHost))

channel = connection.channel()

channel.queue_declare(queue='nfts-queue')
channel.exchange_declare(exchange='nfts-exchange',
                         exchange_type='fanout')

channel.queue_bind(exchange='nfts-exchange',
                   queue='nfts-queue')


results = []

for chain in ('eth', 'bsc', 'polygon'):
    params['chain'] = chain
    results += [evm_api.nft.get_wallet_nfts(
        api_key=api_key,
        params=params,
    )]
    
    print('sending to message queue')

    for nftMetada in results :        
        nfmInfo = {
            "chain" : chain,
            "metadata" : nftMetada['result']
        };
        channel.basic_publish(exchange='nfts-exchange',
                        routing_key='nfts-route',
                        body=json.dumps(nfmInfo))

print('NFTs metadata processed')

connection.close()
