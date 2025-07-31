import polars as pl
from datetime import datetime
from ASHC_v3.CommonFunction import dictMerge

# Functions - makeDateIndex, makeDateRangeDict, makeMTD_YTDIndex, makeSaleSeasonDict, makeSaleSeasonIndex
def makeDateIndex(startDate, endDate):
    """Make a date index, input is start date and end date, return result contains a dictionary, where date is key and value as 1
    eg: dateIdx = makeDateIndex(startDate, endDate)"""
    dateSeries = pl.datetime_range(datetime(int(startDate.split('-')[0]),int(startDate.split('-')[1]),int(startDate.split('-')[2])), datetime(int(endDate.split('-')[0]),int(endDate.split('-')[1]),int(endDate.split('-')[2])),'1d',eager=True)
    dateRangeDict = {x:1 for x in dateSeries}
    return dateRangeDict

def makeDateRangeDict(startDate, endDate):
    """Make a date index with last years dates as well, input is start date and end date, return result contains a dictionary, 
    with both input date range and last years date range, where date is key and value as 1
    eg: dateIdx = makeDateRangeDict(startDate, endDate)"""
    DateDict = {}
    dateSeriesTY = pl.datetime_range(datetime(int(startDate.split('-')[0]),int(startDate.split('-')[1]),int(startDate.split('-')[2])), datetime(int(endDate.split('-')[0]),int(endDate.split('-')[1]),int(endDate.split('-')[2])),'1d',eager=True)
    dateSeriesLY = pl.datetime_range(datetime(int(startDate.split('-')[0])-1,int(startDate.split('-')[1]),int(startDate.split('-')[2])), datetime(int(endDate.split('-')[0])-1,int(endDate.split('-')[1]),int(endDate.split('-')[2])),'1d',eager=True)
    dateRangeDictTY = {x:1 for x in dateSeriesTY}
    dateRangeDictLY = {x:1 for x in dateSeriesLY}
    DateDict = dictMerge(DateDict, dateRangeDictTY)
    DateDict = dictMerge(DateDict, dateRangeDictLY)
    return DateDict

def makeMTD_YTDIndex(startDate, endDate, ses):
    """Make a date index with last years dates as well, input is start date and end date, return result contains a dictionary, 
    with both input date range and last years date range, where date is key and value as 3rd parameter
    eg: dateIdx = makeMTD_YTDIndex(startDate, endDate, ses)"""
    DateDict = {}
    dateSeriesTY = pl.datetime_range(datetime(int(startDate.split('-')[0]),int(startDate.split('-')[1]),int(startDate.split('-')[2])), datetime(int(endDate.split('-')[0]),int(endDate.split('-')[1]),int(endDate.split('-')[2])),'1d',eager=True)
    dateSeriesLY = pl.datetime_range(datetime(int(startDate.split('-')[0])-1,int(startDate.split('-')[1]),int(startDate.split('-')[2])), datetime(int(endDate.split('-')[0])-1,int(endDate.split('-')[1]),int(endDate.split('-')[2])),'1d',eager=True)
    dateRangeDictTY = {x:ses for x in dateSeriesTY}
    dateRangeDictLY = {x:ses for x in dateSeriesLY}
    DateDict = dictMerge(DateDict, dateRangeDictTY)
    DateDict = dictMerge(DateDict, dateRangeDictLY)
    return DateDict

def makeSaleSeasonDict():
    allSesDict = {}
    #----------------------------------------------------------------------------------
    # Feb - Jul - Spring Summer
    # Aug - Jan - Fall Winter
    # YYYY-MM-DD
    SS20_Idx = makeSaleSeasonIndex('2020-01-01', '2020-06-30', 'SS20')
    FW20_Idx = makeSaleSeasonIndex('2020-07-01', '2020-12-31', 'FW20')
    SS21_Idx = makeSaleSeasonIndex('2021-01-01', '2021-06-30', 'SS21')
    FW21_Idx = makeSaleSeasonIndex('2021-07-01', '2021-12-31', 'FW21')
    SS22_Idx = makeSaleSeasonIndex('2022-01-01', '2022-06-30', 'SS22')
    FW22_Idx = makeSaleSeasonIndex('2022-07-01', '2022-12-31', 'FW22')
    SS23_Idx = makeSaleSeasonIndex('2023-01-01', '2023-06-30', 'SS23')
    FW23_Idx = makeSaleSeasonIndex('2023-07-01', '2023-12-31', 'FW23')
    SS24_Idx = makeSaleSeasonIndex('2024-01-01', '2024-06-30', 'SS24')
    FW24_Idx = makeSaleSeasonIndex('2024-07-01', '2024-12-31', 'FW24')
    SS25_Idx = makeSaleSeasonIndex('2025-01-01', '2025-06-30', 'SS25')
    FW25_Idx = makeSaleSeasonIndex('2025-07-01', '2025-12-31', 'FW25')
    allSesDict = dictMerge(allSesDict, SS20_Idx)
    allSesDict = dictMerge(allSesDict, FW20_Idx)
    allSesDict = dictMerge(allSesDict, SS21_Idx)
    allSesDict = dictMerge(allSesDict, FW21_Idx)
    allSesDict = dictMerge(allSesDict, SS22_Idx)
    allSesDict = dictMerge(allSesDict, FW22_Idx)
    allSesDict = dictMerge(allSesDict, SS23_Idx)
    allSesDict = dictMerge(allSesDict, FW23_Idx)
    allSesDict = dictMerge(allSesDict, SS24_Idx)
    allSesDict = dictMerge(allSesDict, FW24_Idx)
    allSesDict = dictMerge(allSesDict, SS25_Idx)
    allSesDict = dictMerge(allSesDict, FW25_Idx)
    return allSesDict

def makeSaleSeasonIndex(startDate, endDate, ses):
    """Make a date index, input is start date and end date, return result contains a dictionary, 
    where date is key and value as per input in 3rd parameter
    eg: dateIdx = makeSaleSeasonIndex(startDate, endDate, ses)"""
    dateSeries = pl.datetime_range(datetime(int(startDate.split('-')[0]),int(startDate.split('-')[1]),int(startDate.split('-')[2])), datetime(int(endDate.split('-')[0]),int(endDate.split('-')[1]),int(endDate.split('-')[2])),'1d',eager=True)
    dateRangeDict = {x:ses for x in dateSeries}
    return dateRangeDict