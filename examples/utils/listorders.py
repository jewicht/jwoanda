#!/usr/bin/python
from __future__ import print_function

from jwoanda.oandaaccount import oandaenv

def main():
    api = oandaenv.api()
    response = api.order.list(oandaenv.account_id)
    orders = response.get('orders')
    
    if len(orders) < 1:
        print("No orders")
        return

    for order in orders:
        print(order)
    
if __name__ == "__main__":
    main()
    
