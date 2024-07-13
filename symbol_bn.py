from collections import OrderedDict
import json
import pandas as pd
import requests

import random
from app_tools import dt_utils
from app_tools.logger_config import logging

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

    
class SYMBOL_FILTER():
    K_COLUMNS = ['ts_start', 'open', 'high','low','close','volume','ts_end','amount','count','buy_vol','buy_amount','ignore']
    
    K_FLOAT_COLUMNS = ['open', 'high', 'low', 'close', 'volume', 'buy_vol']

    UF_KLINE_URL= 'https://fapi.binance.com/fapi/v1/klines'


    def __init__(self):

        self.period = 60
        self.use_proxy = True
        self.symbol_info ={}

        self.executor = ThreadPoolExecutor(max_workers=10)
        self.proxy_data = {}
    def get_proxy_data(self):
        url = 'https://raw.githubusercontent.com/bailiang9966/ccpp/main/out/output.json'
        response = requests.get(url)
        self.proxy_data = json.loads(response.text)

    def execute_request(self,url,proxy_key = None,params=None):
        if not self.use_proxy:
            return requests.get(url,params=params)
        else:
            proxy = random.choice(self.proxy_data[proxy_key])
            while True:
                try:
                    response = requests.get(url, params=params,proxies={'http': proxy, 'https': proxy}, timeout=3)
                    if response.status_code == 200:
                        return response
                except (requests.exceptions.Timeout, requests.exceptions.RequestException):
                    # 处理超时和其他请求异常
                    self.proxy_data[proxy_key].remove(proxy)
                
                proxy = random.choice(self.proxy_data[proxy_key])
    def get_kline_volatility(self,symbol):
        '''
        查询合约和现货k线历史合并为一个df后转换为list
        '''
        start_ts,end_ts = dt_utils.get_period_ts(self.period)
        start_ts = start_ts-self.period*60000*999
        params = {
            'symbol':f"{symbol}USDT",
            'interval':'1h',
            'limit':999,
            'startTime':start_ts,
            'endTime':end_ts,

        }
        uf_klines = self.execute_request(self.UF_KLINE_URL,proxy_key='bn_uf',params=params).json()
        
        df = pd.DataFrame(uf_klines,columns=self.K_COLUMNS)
        df[self.K_FLOAT_COLUMNS] = df[self.K_FLOAT_COLUMNS].astype(float)
        df['volatility'] = round((df['high'] - df['low']) / df['open'], 6)
        volatility = df['volatility'].sort_values().iloc[60]
        # self.symbol_info .append({'symbol':symbol,'volatility':volatility})
        self.symbol_info[symbol]=volatility
    
    def get_bn_exchange(self,market_type ):
        if market_type == 'SPOT':
            url = 'https://api.binance.com/api/v3/exchangeInfo'
            result = self.execute_request(url,proxy_key='bn_spot').json()
        else:
            url ='https://fapi.binance.com/fapi/v1/exchangeInfo'
            result = self.execute_request(url,proxy_key='bn_uf').json()
        # result = self.execute_request(url).json()
        symbols = result['symbols']
    
        data = []    
        for s in symbols:
            if s['quoteAsset'] == 'USDT' and s['status'] == 'TRADING' and "_" not in s['symbol']:# and s['isSpotTradingAllowed'] == True:
                
                data.append(s['baseAsset'])
        return data
    def data_to_file(self,data):
        file_path = 'out/data.json'  # 替换成你想要保存文件的路径
        file = open(file_path, 'w')
        json_data = json.dumps(data)
        file.write(json_data)
        file.close()
    def get_top_data(self,data_dict):
        # sorted_data = sorted(self.symbol_info, key=lambda x: x['volatility'], reverse=True)
        sorted_data = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)

        n = len(sorted_data)
        result = sorted_data[:int(n * 0.3)]
        result= dict(result)

        keep_symbols = ['BTC', 'ETH']
        for ks in keep_symbols:
            result[ks] = self.symbol_info[ks]
        return result

    def get_symbols(self):
        '''
        币安现货和合约都已经上线 
        '''
        bn_spot_symbols = self.get_bn_exchange('SPOT')
        bn_uf_symbols = self.get_bn_exchange('UF')
        black_list = ['USDC','USDC','BUSD','DAI','TUSD','PAX','GUSD','EURS','FUSD','USDY']
        
        bn_symbols = list((set(bn_uf_symbols) & set(bn_spot_symbols))- set(black_list))

        futures = []
        for s in bn_symbols:
            future  = self.executor.submit(self.get_kline_volatility,s)
            futures.append(future)
        concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)

        result = self.get_top_data(self.symbol_info)

        self.data_to_file(self.symbol_info)
        return result
        
    def run(self):
        logging.info('start')
        if self.use_proxy:
            self.get_proxy_data()
            logging.info(f'proxy_data:{self.proxy_data}')
        result = self.get_symbols()
        logging.info(f'币种总数:{len(self.symbol_info)}')
        logging.info(f'过滤后:{len(result)}')

if __name__ == '__main__':
    sf = SYMBOL_FILTER()
    sf.run()

