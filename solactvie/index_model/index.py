"""
This file is for Solactive's coding challenge assessment
where Minki Park builds a index model according to their instructions
(Most recently updated on September 26, 2022)
"""

import datetime as dt
import numpy as np
import pandas as pd


class IndexModel:
    def __init__(self) -> None:
        # import data
        path = "data_sources/stock_prices.csv"
        stock_prices = pd.read_csv(path, index_col=0) # create a dataframe that contains the data in the csv file
        stock_prices_index = list(stock_prices.index)
        for i in range(len(stock_prices_index)):
            stock_prices_index[i] = dt.datetime.strptime(stock_prices_index[i], "%d/%m/%Y").date()       
        stock_prices.index = pd.to_datetime(stock_prices_index) # convert the data type of dataframe's index from string to date
        
        # calculate stock returns
        stock_returns = stock_prices.copy() # create a temporary dataframe with the same size as stock_prices
        for i in range(len(stock_returns)):
            if i == 0:
                stock_returns.iloc[i] = 0 # On the first day when the stock prices data begin, stock returns are zero (the returns cannot be calculated or defined)
            else:
                stock_returns.iloc[i] = (stock_prices.iloc[i]-stock_prices.iloc[i-1])/stock_prices.iloc[i-1] # From the second day, calculate the stock prices returns
        
        # determine top 3 stocks for each month
        business_month = stock_prices.asfreq("BM") # create a dataframe that contains stock prices data on the last business day of each month
        top_3_columns = ["Top 1", "Top 2", "Top 3"]
        top_3_stocks = pd.DataFrame(business_month.columns.values[np.argsort(-business_month.values, axis = 1)[: ,: 3]],
                                     index = business_month.index,
                                     columns = top_3_columns) # create a dataframe that contains the names of the top 3 stocks based on the market capitalization, based on the last business day of each month (on a monthly basis )
        
        # identify the top 3 stocks' prices and returns for each month
        start_date = dt.date(year=2020, month=1, day=1)
        end_date = dt.date(year=2020, month=12, day=31)
        business_dates = pd.bdate_range(start_date, end_date)
        top_3_prices = pd.DataFrame(np.random.randn(len(business_dates),len(top_3_columns)),
                                    index = business_dates,
                                    columns = top_3_columns) # create a temporary dataframe to contain the prices data of the top 3 stocks (on a daily basis)
        top_3_lists = top_3_prices.copy() # create a temporary dataframe to contain the names of the top 3 stocks (on a daily basis)
        top_3_returns = top_3_prices.copy() # create a temporary dataframe to contain the returns data of the top 3 stocks (on a daily basis)
        business_month_start = stock_prices.asfreq("BMS").index # create a index variable that implies the first business day of each month 
        j = 0
        for i in top_3_prices.index: # On the first business day of each month, select the top 3 stocks
            [top_1, top_2, top_3] = list(top_3_stocks.iloc[j])
            if i in business_month_start:
                if i == top_3_prices.index[0]: # January (2019)'s top 3 stocks are selected based on the prices data (thus market capitalization data as the number of shares are the same across all the companies) in December 2020
                    pass
                else:
                    j += 1 # update on the first business day of each month
                    [top_1, top_2, top_3] = list(top_3_stocks.iloc[j])
            else:
                pass
            top_3_lists.loc[i] = [top_1, top_2, top_3]
            top_3_prices.loc[i, top_3_columns[0]] = stock_prices.loc[i,top_1]
            top_3_prices.loc[i, top_3_columns[1]] = stock_prices.loc[i,top_2]
            top_3_prices.loc[i, top_3_columns[2]] = stock_prices.loc[i,top_3]
            top_3_returns.loc[i,[top_3_columns[0]]] = stock_returns.loc[i,top_1]
            top_3_returns.loc[i,[top_3_columns[1]]] = stock_returns.loc[i,top_2]
            top_3_returns.loc[i,[top_3_columns[2]]] = stock_returns.loc[i,top_3]
            
        self.business_dates = business_dates
        self.top_3_returns = top_3_returns

    def calc_index_level(self, start_date: dt.date, end_date: dt.date) -> None:
        # create a dataframe to contain index_level data
        business_dates = pd.bdate_range(start_date, end_date)
        index_level = pd.DataFrame(np.empty(len(business_dates)),
                                   index = business_dates,
                                   columns = ["index_level"]) # create a temporary dataframe to contain index level information
        
        # calculate the index level for each date and update the index_level dataframe
        weights = [0.5, 0.25, 0.25] # the weights assigned to each of the top 3 stocks
        change = pd.DataFrame(np.average(self.top_3_returns.to_numpy(), weights = weights, axis=1), index=self.top_3_returns.index, columns=["percentage change"]) # determine the percentage change to be applied to the index for each date
        change.iloc[0] = 0 # On January 1, 2020, there is no percentage change to the index level as the index only starts on the date
        for i in range(len(business_dates)):
            if i == 0:
                index_level.iloc[i] = 100 # On January 1, 2020, the index level starts at 100
            else:
                index_level.iloc[i,0] = index_level.iloc[i-1,0] * (1 + change.iloc[i,0]) # update the index level every business day
            
        self.index_level = index_level

    def export_values(self, file_name: str) -> None:
        self.index_level.to_csv(file_name) # export the index_level dataframe to a csv file
