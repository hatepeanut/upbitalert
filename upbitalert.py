import pyupbit
import requests
import discord
import asyncio
import pytz
import threading
import numpy as np
from bs4 import BeautifulSoup
import time
import datetime
from discord.ext import commands

access = "NULL"          # 본인 값으로 변경
secret = "NULL"          # 본인 값으로 변경
client = discord.Client()
token = ""

upbit = pyupbit.Upbit(access, secret)

def get_start_price(ticker):
    #각 티거들의 시초가 설정
    df = pyupbit.get_ohlcv(ticker, interval="day",count =2)
    start_price = df.iloc[0]['close']
    return start_price

def get_past_price(ticker):
    #각 티거들의 현재가 3분전 가격 설정
    df2 = pyupbit.get_ohlcv(ticker, interval="minute3",count =2)
    past_price = df2.iloc[0]['close']
    return past_price

def get_cur_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]    

def get_ma25(ticker):
    """25일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=25)
    ma25 = df['close'].rolling(25).mean().iloc[-1]
    return ma25

def get_ma60(ticker):
    """60일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=60)
    ma60 = df['close'].rolling(60).mean().iloc[-1]
    return ma60

def get_ma120(ticker):
    """120일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=120)
    ma120 = df['close'].rolling(120).mean().iloc[-1]
    return ma120

def get_ma224(ticker):
    """224일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=224)
    ma224 = df['close'].rolling(224).mean().iloc[-1]
    return ma224

time_ticker = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
ticker_state = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
bit_alert1 = 0
bit_alert2 = 0
bit_time1 = 0
bit_time2 = 0
# 2021-08-03 12:11:32

@client.event
async def on_ready() : #봇이 실행되면 한번 실행
    print("실행")
    await client.change_presence(status=discord.Status.online, activity=discord.Game("ONLINE"))
    ch = client.get_channel(874265330258698260)
    while True:
        try :
            url = "https://www.coingecko.com/ko/거래소/upbit"
            bs = BeautifulSoup(requests.get(url).text,'html.parser')
            high_ticker = []
            
            ticker_temp = bs.find_all("a", attrs={"rel":"nofollow noopener", "class":"mr-1"})
            ma25 = get_ma25("KRW-BTC")
            ma60 = get_ma60("KRW-BTC")
            ma120 = get_ma120("KRW-BTC")
            ma224 = get_ma224("KRW-BTC")
            
            for i in range(16):
                now = datetime.datetime.now()
                nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
                high_ticker.append('KRW-' + list(ticker_temp[i])[0][1:-5])
                cur_price = get_cur_price(high_ticker[i]) #pyupbit.get_current로 여러종목 조회시 dic로 반환됨
                start_price = get_start_price(high_ticker[i])
                past_price = get_past_price(high_ticker[i])

                # print(time.time())
                # print(high_ticker[i])
                # print(start_price)
                # print(cur_price)
                # print(past_price)
                # print(ticker_state[i])
                # print(nowDatetime)


                if past_price < start_price :
                    if cur_price > start_price :
                        if ticker_state[i] == 0 :
                            ticker_state[i] = 1
                            time_ticker[i] = time.time()
                            await ch.send("{} 시초가 돌파 {}".format(high_ticker[i],nowDatetime)) 
                        
                            print(" Find ")
                            
                            
                        else :
                            if time_ticker[i]+ 300 < time.time() :
                                ticker_state[i] = 0
                            else :
                                ticker_state[i] = 1
                    
                if ma25 < ma60 < ma120 :
                    if bit_alert1 == 0 :
                        print("비트코인 하락추세")
                        await ch.send("비트코인 하락추세 {}".format(nowDatetime))
                        bit_alert1 = 1
                        bit_time1=time.time()
                    else :
                        if bit_time1 + 1200 < time.time() :
                            bit_alert1 = 0
                        else :
                            bit_alert1 = 1

                if ma25 < ma60 < ma224 :
                    if bit_alert2 == 0 :
                        print("비트코인 폭락 조심")
                        await ch.send("비트코인 폭락 조심 {}".format(nowDatetime))
                        bit_alert2 = 1
                        bit_time2=time.time()
                    else :
                        if bit_time2 + 3600 < time.time() :
                            bit_alert2 = 0
                        else :
                            bit_alert2 = 1

                time.sleep(0.4)
        except Exception as e:
                        
            print(e)
            time.sleep(1)
client.run(token)    

        