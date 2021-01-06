import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns


def plot_equity(equity, color):
    plt.figure(figsize=(8, 3), dpi=300)
    plt.plot(equity,color=color)
    plt.xlabel("Time")
    plt.ylabel("Profit/Loss")
    plt.title("Equity Line")
    plt.xticks(rotation='vertical')
    plt.grid(True)
    plt.show()
    return


def draw_down(equity):
    maxvalue = equity.expanding(0).max()
    num_drawdown = equity - maxvalue
    drawdown_series = pd.Series(num_drawdown, index = equity.index)
    return drawdown_series


def plot_draw_down(equity, color):
    dd = draw_down(equity)
    plt.figure(figsize=(12, 6), dpi=300)
    plt.plot(dd, color=color)
    plt.fill_between(dd.index, 0, dd, color=color)
    plt.xlabel("Time")
    plt.ylabel("Profit/Loss")
    plt.title("Draw down")
    plt.xticks(rotation='vertical')
    plt.grid(True)
    plt.show()
    return


def max_draw_down(equity):
    dd = draw_down(equity)
    return round(dd.min(), 2)


def avg_draw_down_nozero(equity):
    dd = draw_down(equity)
    return round(dd[dd < 0].mean(), 2)


def avg_loss(operations):
    return round(operations[operations < 0].mean(), 2)


def max_loss(operations):
    return round(operations[operations < 0].min(), 2)


def max_loss_date(operations):
    return operations.idxmin()


def avg_gain(operations):
    return round(operations[operations > 0].mean(), 2)


def max_gain(operations):
    return round(operations[operations > 0].max(), 2)


def max_gain_date(operations):
    return operations.idxmax()


def gross_profit(operations):
    return round(operations[operations > 0].sum(), 2)


def gross_loss(operations):
    return round(operations[operations < 0].sum(), 2)


def profit_factor(operations):
    gp = gross_profit(operations)
    gl = gross_loss(operations)

    if gl != 0:
        return round(abs(gp / gl), 2)
    else:
        return round(abs(gp / 0.0000001), 2)


def percent_win(operations):
    return round(operations[operations > 0].count() / operations.count() * 100, 2)


def percent_loss(operations):
    return round(operations[operations < 0].count() / operations.count() * 100, 2)


def reward_risk_ratio(operations):
    if operations[operations <= 0].mean() != 0:
        return round((operations[operations > 0].mean() / -operations[operations <= 0].mean()), 2)
    else:
        return np.inf


def delay_between_peaks(equity):
    work_df = pd.DataFrame(equity, equity.index)
    work_df["drawdown"] = draw_down(equity)
    work_df["delay_elements"] = work_df["drawdown"].apply(lambda x: 1 if x < 0 else 0)
    work_df["resets"] = np.where(work_df["drawdown"] == 0, 1, 0)
    work_df["cumsum"] = work_df["resets"].cumsum()
    a = pd.Series(work_df["delay_elements"].groupby(work_df["cumsum"]).cumsum())
    return a


def max_delay_between_peaks(equity):
    a = delay_between_peaks(equity)
    return a.max()


def avg_delay_between_peaks(equity):
    work_df = pd.DataFrame(equity, equity.index)
    work_df["drawdown"] = draw_down(equity)
    work_df["delay_elements"] = work_df["drawdown"].apply(lambda x: 1 if x < 0 else np.nan)
    work_df["resets"] = np.where(work_df["drawdown"] == 0, 1, 0)
    work_df["cumsum"] = work_df["resets"].cumsum()
    work_df.dropna(inplace=True)
    a = work_df["delay_elements"].groupby(work_df["cumsum"]).sum()
    return round(a.mean(), 2)


def plot_annual_histogram(operations):
    yearly = operations.resample('A').sum()
    colors = pd.Series()
    colors = yearly.apply(lambda x: "green" if x > 0 else "red")
    n_groups = len(yearly)
    plt.subplots(figsize=(10, 7), dpi=200)
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 1
    rects1 = plt.bar(index,
                     yearly,
                     bar_width,
                     alpha=opacity,
                     color=colors,
                     label="Yearly Stats")

    plt.xlabel("Years")
    plt.ylabel("Profit / Loss")
    plt.title("Yearly Profit / Loss")
    plt.xticks(index, yearly.index.year, rotation=90)
    plt.grid(True)
    plt.show()
    return


def plot_monthly_bias_histogram(operations):
    monthly = pd.DataFrame(operations.fillna(0)).resample('M').sum()
    monthly["month"] = monthly.index.month

    biasMonthly = []
    months = []

    for month in range(1,13):
        months.append(month)
    for month in months:
        biasMonthly.append(monthly[(monthly["month"]==month)].mean())

    biasMonthly = pd.DataFrame(biasMonthly)
    column = biasMonthly.columns[0]

    colors = pd.Series()
    colors = biasMonthly[column].apply(lambda x: "green" if x > 0 else "red")
    n_groups = len(biasMonthly)
    plt.subplots(figsize=(10, 7), dpi=200)
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 1
    rects1 = plt.bar(index,
                     biasMonthly[column],
                     bar_width,
                     alpha=opacity,
                     color=colors,
                     label="Yearly Stats")

    plt.xlabel("Months")
    plt.ylabel("Average Profit / Loss")
    plt.title("Average Monthly Profit / Loss")

    months_names = ["January", "February", "March", "April",
                    "May", "June", "July", "August",
                    "September", "October", "November", "December"]

    plt.xticks(index, months_names, rotation=45)
    plt.grid(True)
    plt.show()
    return


def plot_equity_heatmap(operations,annotations):
    monthly = operations.resample('M').sum()
    to_heat_map = pd.DataFrame(monthly)
    to_heat_map["Year"] = to_heat_map.index.year
    to_heat_map["Month"] = to_heat_map.index.month

    show = to_heat_map.groupby(by=['Year','Month']).sum().unstack()
    show.columns = ["January", "February", "March", "April",
                    "May", "June", "July", "August",
                    "September", "October", "November", "December"]

    plt.figure(figsize=(8,6), dpi=120)
    sns.heatmap(show, cmap="RdYlGn", linecolor="white", linewidths=0.1, annot=annotations,
                vmin=-max(monthly.min(), monthly.max()), vmax=monthly.max())
    return



