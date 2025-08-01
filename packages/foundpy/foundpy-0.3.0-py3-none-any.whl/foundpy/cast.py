from .util import *
from .config import *
from .contract import *

class Cast():
    def __init__(self):
        pass

    def age(self, block_number):
        return get_age(block_number)

    def balance(self, address):
        return get_balance(address)
    
    def block(self, block_number):
        return get_block(block_number)
    
    def block_number(self):
        return config.w3.eth.block_number

    def call(self, contract_address, function_signature, *args):
        contract = Contract(contract_address)
        return contract.call(function_signature, *args)
    
    def code(self, contract_address):
        contract = Contract(contract_address)
        return contract.code()
    
    def codesize(self, contract_address):
        contract = Contract(contract_address)
        return contract.codesize()

    def send(self, contract_address, function_signature, *args, value=0, gas_limit=None):
        contract = Contract(contract_address)
        return contract.send(function_signature, *args, value=value, gas_limit=gas_limit)

    def storage(self, contract_address, slot):
        contract = Contract(contract_address)
        return contract.storage(slot)
    
    def tx(self, tx_hash):
        return get_tx(tx_hash)

    
    # todo
    # logs