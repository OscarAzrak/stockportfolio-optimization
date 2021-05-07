import pandas as pd
from pandas_datareader import data as web
import requests
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
pd.options.display.max_columns = None


stocks = ['EVO.ST', 'CAST.ST', 'ICA.ST', 'NIBE-B.ST', 'INVE-B.ST', 'EMBRAC-B.ST']

##Get stock price data

# get data from YFinance
#Get the portfolio starting date

stockStartDate = "2000-01-01"
#Get the portfolios ending date

stockEndDate = "2021-03-09"


# Create a dataframe to store the adjusted close price of the stocks
# Store the adjusted close price of the stock into df
df = pd.DataFrame()
for stock in stocks:
    try:
        df[stock] = web.DataReader(stock, data_source='yahoo', start=stockStartDate, end=stockEndDate)['Adj Close']
    except KeyError:
        pass

print(df)



#Annualized returns and annualized sample cov
mu = expected_returns.mean_historical_return(df)
S = risk_models.sample_cov(df)


#optimize for the maximal sharpe ratio
ef = EfficientFrontier(mu, S)
weights = ef.max_sharpe()

cleaned_weights = ef.clean_weights()

print(ef.portfolio_performance(verbose=True))

portfolio_val = 100000

latest_price = get_latest_prices(df)
weights = cleaned_weights

da = DiscreteAllocation(weights, latest_price, total_portfolio_value=portfolio_val)
allocation, leftover = da.lp_portfolio()

print('Discrete Allocation:', allocation)
print('Funds Remaining:', leftover)

#Get the company names
def get_company_name(symbol):
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)

    result = requests.get(url).json()

    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            return x['name']

#store company name in list and get discrete allocation values
company_name = []
discrete_allocation_list = []
ticker_list = []

for symbol in allocation:
    company_name.append(get_company_name(symbol))
    discrete_allocation_list.append(allocation.get(symbol))
    ticker_list.append(symbol)

#create a dataframe for portfolio

portfolio_df = pd.DataFrame(columns=['Company Name', 'Company Ticker', 'Discrete Values_'+str(portfolio_val)])
portfolio_df['Company Name'] = company_name
portfolio_df['Company Ticker'] = allocation
portfolio_df['Discrete Values_'+str(portfolio_val)] = discrete_allocation_list



print(portfolio_df)
