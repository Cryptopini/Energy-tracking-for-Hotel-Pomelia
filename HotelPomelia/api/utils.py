from web3 import Web3
# we set up the credentials to send transactions on the blockchain
def sendTransaction(message):
    w3 = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/f7a042f9a6d54e39abd91c7803077646'))
    address = '0x759fd9D944667b89A1d1b67fD36717aE7163EA0F'
    privateKey = '0x20072575e4823d24ce969c8c1d0363f020d2e64ce43fb86ef152835dd8fe926d'
    nonce = w3.eth.getTransactionCount(address)
    gasPrice = w3.eth.gasPrice
    value = w3.toWei(0, 'ether')
    signedTx = w3.eth.account.signTransaction(dict(
        nonce=nonce,
        gasPrice=gasPrice,
        gas=100000,
        to='0x0000000000000000000000000000000000000000',
        value=value,
        data=message.encode('utf-8')
    ), privateKey)

    tx = w3.eth.sendRawTransaction(signedTx.rawTransaction)
    txID = w3.toHex(tx)
    return txID