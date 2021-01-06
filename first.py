import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ffn
import cufflinks as cf
import plotly.graph_objs as go
import plotly.express as px






def crossover(a1, a2):
    return (a1 > a2.shift(1)) & (a1.shift(1) < a2.shift(2))


def crossunder(a1, a2):
    return (a1 < a2.shift(1)) & (a1.shift(1) > a2.shift(2))


def sma(array, period):
    return array.rolling(period).mean()


def ExpandingMax(array):
    return array.expanding().max()


def DonchainChannelUp(array, period):
    return array.rolling(period).max()


def DonchainChannelDown(array, period):
    return array.rolling(period).min()


# data = ffn.get('aapl:Open,aapl:High,aapl:Low,aapl:Close,aapl:Volume', start = '2000-01-01' , end = '2021-01-01')
data = ffn.get('bac:Open,bac:High,bac:Low,bac:Close,bac:Volume', start='2000-01-01', end='2021-01-01')
data.columns = ["open", "high", "low", "close", "volume"]
data = data.apply(lambda x: round(x, 2))
data.volume = data.volume.apply(lambda x: round(x, 0))
data["sma20"] = sma(data.close, 20)
data["sma200"] = sma(data.close, 200)
data["deltaperc"] = data.close.pct_change()
data["buyhold"] = (data.deltaperc + 1).cumprod() * 100
data.dropna(inplace=True)

data["position"] = np.where((data.sma20 > data.sma200), 1, 0)
data.position = data.position.shift(1)
data.iloc[-22:-10, :]
data["strategyperc"] = data.deltaperc * data.position
data["strategy"] = (data.strategyperc + 1).cumprod() * 100
data.iloc[-22:-10, :]

statistics = pd.DataFrame(data.buyhold.diff().resample("A").sum())
statistics["strategy"] = data.strategy.diff().resample("A").sum()
statistics

print(data.head(10))

monthly = data.buyhold.diff().resample("M").sum()
toHeatMap = pd.DataFrame(monthly)
toHeatMap["Year"] = toHeatMap.index.year
toHeatMap["Month"] = toHeatMap.index.month
Show = toHeatMap.groupby(by=["Year","Month"]).sum().unstack()
Show.columns = ["January","February","March","April",
                "May","June","July","August",
                "September","October","November","December",]
plt.figure(figsize=[8,6],dpi=120)
sns.heatmap(Show,cmap="RdYlGn",linecolor="white",linewidth=1,annot=True,vmin=-max(monthly.min(),monthly.max()), vmax = monthly.max())


print("Fine")