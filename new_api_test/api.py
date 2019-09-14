import requests

api_token_key = '0oa4AZ1WYhRqMLeJOBXj8ht1NukxmmVymmOQEdvqnha0rqZQpfKaWdD4JNX9'
root_url = 'https://api.worldtradingdata.com/api/v1/stock?symbol={}&api_token={}'
company_symbols = ['AAPL', 'GOOGL', 'MSFT', 'FB', 'SNAP', 'NFLX', 'AMZN', '005930.KS', 'ADBE', 'ORCL', 'TSLA', 'INTC', 'AMD', 'NVDA', 'IBM', 'QCOM', 'CSCO', 'TXN', 'ACN', 'UBER', 'CRM', 'CTSH', 'SNE', 'NTDOF', 'SB3.F', 'TECHM.NS', 'TCS.NS', 'INFY', 'HCLTECH.NS', '0419.HK', 'BIDU', 'BABA', 'NOW', '1810.HK', 'DIS', 'SPOT', 'NOA3.F', 'HPQ', 'DELL', 'PYPL', 'RCOM.NS', '066570.KS', 'EBAY', 'SAP', 'VLKAF', 'DDAIF', 'TM', 'TWTR', 'T', 'VZ']
no_companies_at_a_time = 5

for i in range(0, 50, no_companies_at_a_time):
	symbols = company_symbols[i:i+no_companies_at_a_time]
	url = root_url.format(','.join(symbols), api_token_key)
	print(url)
	r = requests.get(url)
	data = r.json()['data']
	for each_company in data:
		print(i, each_company['name'], each_company['currency'])
