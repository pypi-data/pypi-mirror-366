import os
import polars as pl
import ASHC_v3 as ashc
from ASHC_v3.CommonFunction import Polars_toDict

def initiateConfig(saleDir, stockDir, masterDir, dataDir, outDir):
    """This Function initializes this library with various default parameters,
    It is very important to call this function before using any other functions from ASHC_v3"""
    #print("Config initiated")
    ashc.outFolder = outDir
    ashc.budFile = os.path.join(dataDir, 'Budget', '1.1a._DAILY_SALES___TY_vs_PY*.csv')
    ashc.kpiFile = os.path.join(dataDir, 'KPI', '*.csv')
    ashc.purchDateFiles = os.path.join(dataDir, 'PurchaseData', '*.csv.gz')
    ashc.stockDumpFiles = os.path.join(stockDir, '*.csv.gz')
    ashc.offerFile = os.path.join(dataDir, 'Configs', 'Offer_Detail.csv')
    ashc.xlConfigFile = os.path.join(dataDir, 'Configs', 'ConfigFile.xlsx')
    ashc.UndizMaster = os.path.join(masterDir, 'UZ-Master.xlsx')
    ashc.VincciMaster = os.path.join(masterDir, 'VI-Master.xlsx')
    ashc.YRMaster = os.path.join(masterDir, 'YR-Master.xlsx')
    ashc.JacadiMaster = os.path.join(masterDir, 'JC-Master.xlsx')
    ashc.OkaidiMaster = os.path.join(masterDir, 'OK-Master.xlsx')
    ashc.PerfoisMaster = os.path.join(masterDir, 'PA-Master.xlsx')
    ashc.LSMaster = os.path.join(masterDir, 'LS-Master.xlsx')
    
    configData = pl.read_excel(source=ashc.xlConfigFile,sheet_name="StoreMaster",infer_schema_length=0,)    #engine_options={"skip_empty_lines": True},
    lflData = pl.read_excel(source=ashc.xlConfigFile,sheet_name="LFLMaster",infer_schema_length=0,)         #engine_options={"skip_empty_lines": True},
    dateData = pl.read_excel(source=ashc.xlConfigFile,sheet_name="DateMaster",infer_schema_length=0,)       #schema_overrides={"Date(Month2nd)":pl.Datetime},engine_options={"skip_empty_lines": True},
    try:
        dateData = dateData.with_columns(pl.col('Date(Month2nd)').str.to_datetime())
    except:
        print(" ")
    #----------------------Store Master---------------------------------------------
    ashc.ShortStoreName = Polars_toDict(configData, 'Location Code', 'ShortName')
    ashc.StoreName = Polars_toDict(configData, 'Location Code', 'StoreName')
    ashc.BrandName = Polars_toDict(configData, 'Location Code', 'Brand Code')
    ashc.Country = Polars_toDict(configData, 'Location Code', 'Country')
    ashc.City = Polars_toDict(configData, 'Location Code', 'City')
    ashc.LocationType = Polars_toDict(configData, 'Location Code', 'Location Type')
    ashc.Status = Polars_toDict(configData, 'Location Code', 'Status')
    ashc.Area = Polars_toDict(configData, 'Location Code', 'Store Size')
    ashc.OpeningDate = Polars_toDict(configData, 'Location Code', 'OpeningDate')
    ashc.LocCode = Polars_toDict(configData, 'StoreName', 'Location Code')
    #--------------------------------------------------------------------------------
    ashc.Year_ = Polars_toDict(dateData, 'Date(Month2nd)', 'Year')
    ashc.Qtr_ = Polars_toDict(dateData, 'Date(Month2nd)', 'Quarter')
    ashc.Month_ = Polars_toDict(dateData, 'Date(Month2nd)', 'Month')
    ashc.Week_ = Polars_toDict(dateData, 'Date(Month2nd)', 'WeekNo')
    ashc.Lyty_ = Polars_toDict(dateData, 'Date(Month2nd)', 'Comp')
    #--------------------------------------------------------------------------------
    ashc.Lfl = Polars_toDict(lflData, 'Combo', 'Status(LFL)')