#!/usr/bin/python

from __future__ import print_function

from jwoanda.oandaaccount import oandaenv

def main():

    api = oandaenv.api()
    response = api.trade.list(oandaenv.account_id)

    trades = response.get("trades")

    if len(trades) < 1:
        print("No trades")
        return
    
    for trade in trades:
        print(trade)
        res = api.trade.close(oandaenv.account_id, trade.id)#, units=int(-trade.currentUnits))
        print("Close operation result = ", res)

if __name__ == "__main__":
    main()
