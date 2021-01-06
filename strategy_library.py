import pandas as pd
import numpy as np
import performance_report_builder as prb

INSTRUMENT = 1
OPERATION_MONEY = 10000
COSTS = 0


def marketposition_generator(enter_rules, exit_rules, enter_rules_short, exit_rules_short):
    service_dataframe = pd.DataFrame(index=enter_rules.index)
    service_dataframe['enter_rules'] = enter_rules
    service_dataframe['exit_rules'] = exit_rules
    service_dataframe['enter_rules_short'] = enter_rules_short
    service_dataframe['exit_rules_short'] = exit_rules_short

    status = 0
    mp = []

    for (a, b, c, d) in zip(enter_rules, exit_rules, enter_rules_short, exit_rules_short):
        if status == 0:
            if a == 1 and b != -1:
                status = 1
            elif c == -1 and d != 1:
                status = -1
        else:
            if b == -1:
                status = 0
            elif d == 1:
                status = 0

        mp.append(status)

    service_dataframe['mp_new'] = mp
    service_dataframe.mp_new = service_dataframe.mp_new.shift(1)
    service_dataframe.to_csv('marketposition_generator.csv')
    return service_dataframe.mp_new


def apply_trading_system(imported_dataframe,
                         direction,
                         order_type,
                         enter_level,
                         enter_rules_long,
                         exit_rules_long,
                         enter_rules_short,
                         exit_rules_short
                         ):
    dataframe = imported_dataframe.copy()
    dataframe['enter_rules_long'] = enter_rules_long.apply(lambda x: 1 if x == True else 0)
    dataframe['exit_rules_long'] = exit_rules_long.apply(lambda x: -1 if x == True else 0)
    dataframe['enter_rules_short'] = enter_rules_short.apply(lambda x: -1 if x == True else 0)
    dataframe['exit_rules_short'] = exit_rules_short.apply(lambda x: 1 if x == True else 0)
    dataframe['mp'] = marketposition_generator(dataframe.enter_rules_long, dataframe.exit_rules_long,
                                               dataframe.enter_rules_short, dataframe.exit_rules_short)

    if order_type == "market":
        dataframe['entry_price'] = np.where((dataframe.mp.shift(1) == 0) & (dataframe.mp == 1), dataframe.open, np.nan)
        dataframe['number_of_stocks'] = np.where((dataframe.mp.shift(1) == 0) & (dataframe.mp == 1),
                                                 OPERATION_MONEY / dataframe.open, np.nan)

    dataframe['entry_price'] = dataframe['entry_price'].fillna(method='ffill')
    dataframe['number_of_stocks'] = dataframe['number_of_stocks'].fillna(method='ffill')
    dataframe['events_in'] = np.where((dataframe.mp == 1) & (dataframe.mp.shift(1) == 0), "entry", "")

    dataframe['open_operations'] = np.where(dataframe.mp == 1,
                                            ((dataframe.close - dataframe.entry_price) * dataframe.number_of_stocks),
                                            np.nan)
    dataframe['open_operations'] = np.where(dataframe.mp == -1,
                                            ((dataframe.entry_price - dataframe.close) * dataframe.number_of_stocks),
                                            dataframe.open_operations)
    dataframe['open_operations'] = np.where((dataframe.mp == 1) & (dataframe.mp.shift(-1) == 0),
                                            (dataframe.open.shift(
                                                -1) - dataframe.entry_price) * dataframe.number_of_stocks - 2 * COSTS,
                                            dataframe.open_operations)
    dataframe['open_operations'] = np.where((dataframe.mp == -1) & (dataframe.mp.shift(-1) == 0),
                                            (dataframe.entry_price - dataframe.open.shift(
                                                -1)) * dataframe.number_of_stocks - 2 * COSTS,
                                            dataframe.open_operations)

    dataframe['open_operations'] = np.where(dataframe.mp != 0, dataframe.open_operations, 0)
    dataframe['events_out'] = np.where((dataframe.mp == 1) & (dataframe.exit_rules_long == -1), "exit long", "")
    dataframe['events_out'] = np.where((dataframe.mp == -1) & (dataframe.exit_rules_short == 1), "exit short", "")
    dataframe['operations'] = np.where((dataframe.exit_rules_long == -1) & (dataframe.mp == 1), dataframe.open_operations,
                                       np.nan)
    dataframe['operations'] = np.where((dataframe.exit_rules_short == 1) & (dataframe.mp == -1), dataframe.open_operations,
                                       np.nan)
    dataframe['closed_equity'] = dataframe.operations.fillna(0).cumsum()
    dataframe['open_equity'] = dataframe.closed_equity + dataframe.open_operations - dataframe.operations.fillna(0)

    dataframe['number_of_stocks'] = dataframe['number_of_stocks'].apply(lambda x: round(x, 2))
    dataframe['open_operations'] = dataframe['open_operations'].apply(lambda x: round(x, 2))
    dataframe['operations'] = dataframe['operations'].apply(lambda x: round(x, 2))
    dataframe['closed_equity'] = dataframe['closed_equity'].apply(lambda x: round(x, 2))
    dataframe['open_equity'] = dataframe['open_equity'].apply(lambda x: round(x, 2))

    return dataframe


def print_performance_report(trading_system, complete):
    ingressi = trading_system.events_in[trading_system.events_in != ""].count()
    uscite = trading_system.events_out[trading_system.events_out != ""].count()
    operations = trading_system.operations.dropna()
    ddor = round(prb.avg_draw_down_nozero(trading_system.open_equity) / prb.max_draw_down(trading_system.open_equity),
                 2)
    ddcr = round(
        prb.avg_draw_down_nozero(trading_system.closed_equity) / prb.max_draw_down(trading_system.closed_equity), 2)

    print("Profitto:                          " + str(trading_system.closed_equity[-1]))
    print("Numero Operazioni chiuse:          " + str(operations.count()))
    print("Media dei profitti:                " + str(round(operations.mean(), 2)))
    print("Max Draw Down Open:                " + str(prb.max_draw_down(trading_system.open_equity)))
    print("Max Draw Down Closed:              " + str(prb.max_draw_down(trading_system.closed_equity)))
    print("Avg Draw Down Open:                " + str(prb.avg_draw_down_nozero(trading_system.open_equity)))
    print("Avg Draw Down Closed:              " + str(prb.avg_draw_down_nozero(trading_system.closed_equity)))
    print("Draw Down Open Ratio:              " + str(ddor))
    print("Draw Down Closed Ratio:            " + str(ddcr))
    print("Perdita media:                     " + str(prb.avg_loss(operations)))
    print("Perdita massima:                   " + str(prb.max_loss(operations)))
    print("Data Perdita massima:              " + str(prb.max_loss_date(operations)))
    print("Guadagno medio:                    " + str(prb.avg_gain(operations)))
    print("Guadagno massimo:                  " + str(prb.max_gain(operations)))
    print("Data Guadagno massimo:             " + str(prb.max_gain_date(operations)))
    print("Profit Factor:                     " + str(prb.profit_factor(operations)))
    print("% Vincite:                         " + str(prb.percent_win(operations)))
    print("Reward Risk Ratio:                 " + str(prb.reward_risk_ratio(operations)))
    print("Max Ritardo Tra Massimi:           " + str(prb.max_delay_between_peaks(trading_system.open_equity)))
    print("Avg Ritardo Tra Massimi:           " + str(prb.avg_delay_between_peaks(trading_system.open_equity)))
    print("Operazioni Aperte:                 " + str(ingressi - uscite))
    print(operations.tail(25))

    prb.plot_equity(trading_system.open_equity, "red")
    prb.plot_draw_down(trading_system.open_equity, "red")
    if complete:
        prb.plot_equity(trading_system.closed_equity, "brown")
        prb.plot_draw_down(trading_system.closed_equity, "brown")

    prb.plot_annual_histogram(operations)
    prb.plot_monthly_bias_histogram(operations)
    prb.plot_equity_heatmap(operations, False)
