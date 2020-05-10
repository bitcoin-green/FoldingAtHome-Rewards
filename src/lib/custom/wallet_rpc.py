from bitcoinrpc.authproxy import AuthServiceProxy

workers = {}

class wallet_rpc(object):
    def connect(self):
        try:
            return AuthServiceProxy("http://%s:%s@127.0.0.1:8331" % ('Folding@Home', 'Fold4BITG'),timeout=120)
        except BrokenPipeError:
            return AuthServiceProxy("http://%s:%s@127.0.0.1:8331" % ('Folding@Home', 'Fold4BITG'), timeout=120)

wallet = wallet_rpc()

def block_height():
    try:
        return wallet.connect().getblockcount()
    except Exception as rpc_error:
        return rpc_error

def unlock_wallet(password, timeout):
    try:
        return wallet.connect().walletpassphrase(password, timeout)
    except Exception as rpc_error:
        return rpc_error

def lock_wallet():
    try:
        return wallet.connect().walletlock()
    except Exception as rpc_error:
        return rpc_error

def process_worker(address, amount):
    workers[address] = amount

def get_balance():
    try:
        return wallet.connect().getbalance()
    except Exception as rpc_error:
        return rpc_error

def pay_workers():
    try:
        return wallet.connect().sendmany('', workers, 16)
    except Exception as rpc_error:
        return rpc_error

def validate_address(addr):
    try:
        return wallet.connect().validateaddress(str(addr))
    except Exception as rpc_error:
        return rpc_error

def lastTx_confirmations():
    try:
        last_transaction = len(wallet.connect().listtransactions()) - 1
        return wallet.connect().listtransactions()[last_transaction]['confirmations']
    except Exception as rpc_error:
        return rpc_error

def lastTx():
    try:
        last_transaction = len(wallet.connect().listtransactions()) - 1
        return wallet.connect().listtransactions()[last_transaction]['txid']
    except Exception as rpc_error:
        return rpc_error

def clear_payroll():
    workers.clear()