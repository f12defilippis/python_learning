import library as util
import strategy_library as sl

SMA_SLOW = 50
SMA_FAST = 20

COSTS = 0
INSTRUMENT = 1
OPERATION_MONEY = 10000
DIRECTION = "long"
ORDER_TYPE = "market"

str_sma_slow = 'sma'+str(SMA_SLOW)
str_sma_fast = 'sma'+str(SMA_FAST)

data = util.load_data('ACN', '2000-01-01', '2021-01-01')

data[str_sma_slow] = util.sma(data['close'], SMA_SLOW)
data[str_sma_fast] = util.sma(data['close'], SMA_FAST)
data = data.apply(lambda x: round(x, 2))


enter_rules = util.crossover(data[str_sma_fast], data[str_sma_slow])
exit_rules = util.crossunder(data[str_sma_fast], data[str_sma_slow])
enter_rules_short = util.crossunder(data[str_sma_fast], data[str_sma_slow])
exit_rules_short = util.crossover(data[str_sma_fast], data[str_sma_slow])
enter_level = data.open


trading_system = sl.apply_trading_system(data, DIRECTION,ORDER_TYPE, enter_level, enter_rules, exit_rules, enter_rules_short, exit_rules_short)
sl.print_performance_report(trading_system, True)

trading_system.to_csv('tradingsystem.csv')