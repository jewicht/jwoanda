#!/usr/bin/python

from __future__ import print_function

from jwoanda.oandaaccount import oandaenv


def main():
    api = oandaenv.api()
    response = api.position.list_open(oandaenv.account_id)

    positions = response.get("positions")

    if len(positions) < 1:
        print("No positions")
        return

    for position in positions:
        print(position)
        print(type(position))
        res = api.position.close(oandaenv.account_id, position.instrument, longUnits='ALL', shortUnits='ALL')
        print("Close operation result = ", res)

if __name__ == "__main__":
    main()

        
# oandapy/oandapy.py:    def get_positions(self, account_id, **params):
# oandapy/oandapy.py:        """ Get a list of all open positions
# oandapy/oandapy.py:        Docs: http://developer.oanda.com/rest-live/positions
# oandapy/oandapy.py:        endpoint = 'v1/accounts/%s/positions' % (account_id)
# oandapy/oandapy.py:    def get_position(self, account_id, instrument, **params):
# oandapy/oandapy.py:        """ Get the position for an instrument
# oandapy/oandapy.py:        Docs: http://developer.oanda.com/rest-live/positions
# oandapy/oandapy.py:        endpoint = 'v1/accounts/%s/positions/%s' % (account_id, instrument)
# oandapy/oandapy.py:    def close_position(self, account_id, instrument, **params):
# oandapy/oandapy.py:        """ Close an existing position
# oandapy/oandapy.py:        Docs: http://developer.oanda.com/rest-live/positions
# oandapy/oandapy.py:        endpoint = 'v1/accounts/%s/positions/%s' % (account_id, instrument)
