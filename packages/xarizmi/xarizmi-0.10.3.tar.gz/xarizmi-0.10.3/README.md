# Xarizmi
Xarizmi (read Khwarizmi) project is an educational project that contains tools for technical analysis in Python.


## Installation
```bash
pip install xarizmi
```

## Example

### Build Candlestick
```python
from xarizmi.candlestick import Candlestick
c = Candlestick(
    **{
        "open": 2,
        "low": 1,
        "high": 4,
        "close": 3,
    }
)
```


### Indicators
### OBV Indicator
```python
from xarizmi.candlestick import CandlestickChart
from xarizmi.ta.obv import OBVIndicator

# assuming btc_usdt_monthly_data is defined (similar to tests/conftest.py)
c = CandlestickChart.model_validate({"candles": btc_usdt_monthly_data})

obv_indicator = OBVIndicator(candlestick_chart=c, volume='amount')
obv_indicator.compute()
print(obv_indicator.indicator_data)
obv_indicator.plot()
```


