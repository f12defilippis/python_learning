import ffn


def crossover(a1, a2):
    return (a1 > a2.shift(1)) & (a1.shift(1) < a2.shift(2))


def crossunder(a1, a2):
    return (a1 < a2.shift(1)) & (a1.shift(1) > a2.shift(2))


def sma(array, period):
    return array.rolling(period).mean()


def expanding_max(array):
    return array.expanding().max()


def donchain_channel_up(array, period):
    return array.rolling(period).max()


def donchain_channel_down(array, period):
    return array.rolling(period).min()

def load_data(ticker, start, end):
    data = ffn.get(ticker+':Open,'+ticker+':High,'+ticker+':Low,'+ticker+':Close,'+ticker+':Volume', start=start, end=end)
    data.columns = ["open", "high", "low", "close", "volume"]
    data = data.apply(lambda x: round(x, 2))
    data.volume = data.volume.apply(lambda x: round(x, 0))
    return data