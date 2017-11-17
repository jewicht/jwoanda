# jwoanda

jwoanda is a work in progress trading/backtesting framework using [OANDA v20 rest API](http://developer.oanda.com/rest-live-v20/introduction/).

Three kinds of strategies can be deployed:
- tick by tick
- time candle
- volume candle

In backtesting mode, strategy can be run against Oanda historical data. A portfolio is created and can be analyzed later on.

In trading mode, any number of strategies on any number of currency pairs can run concurrently.

## Examples

Some examples are available in:
- [strategies](jwoanda/strategies/)
- [backtesting (bt) and trading scripts](examples/scripts)

## Requirements
- an Oanda trading (live or testing) account
- Python 2.7 / 3.5+
- numpy
- pandas
- cython
- TA-lib
- matplotlib

## Installation

```
python setup.py install
```
