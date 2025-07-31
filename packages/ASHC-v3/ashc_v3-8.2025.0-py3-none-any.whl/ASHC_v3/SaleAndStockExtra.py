import polars as pl
import ASHC_v3 as ashc
from ASHC_v3.CommonFunction import Polars_toDict, dictMerge
# Functions - calculateFCCost, extractStyleSale, returnFirstAndLastPurchDate, returnUnitCost

def calculateFCCost(tmp_sls01, ytdDays):
    """This function returns average daily sale and cost based on ytd average,
    takes sale dataframe and ytd days as input,
    eg: retDF = calculateFCCost(saleDF, ytdDays)"""
    rearrangeCols = ["Country","City","Location Code","StoreName","ShortName","Location Type","LFL Status","Comp","Year","Quarter","Month","MerchWeek","Posting Date","Brand Code","Season Code","Division","Product Group","Item Category","Item Class","Item Sub Class","Sub Class","Remarks","FC Qty","FC Cost (AED)"]
    pIdx = ["Country","Posting Date","City","Location Code","StoreName","ShortName","Location Type","LFL Status","Comp","Brand Code","Season Code","Division","Product Group","Item Category","Item Class","Item Sub Class","Sub Class","Remarks",]
    pVal = ["SaleQty","Total Sale Cost(AED)"]
    tmp_sls03 = tmp_sls01.group_by(pIdx).agg(pl.sum(pVal),)
    tmp_sls03 = tmp_sls03.fill_null(0)
    tmp_sls03 = tmp_sls03.fill_nan(0)
    tmp_sls03 = tmp_sls03.with_columns(abs((tmp_sls03['SaleQty'] / ytdDays)).alias('FC Qty'),)
    tmp_sls03 = tmp_sls03.with_columns(abs((tmp_sls03['Total Sale Cost(AED)'] / ytdDays)).alias('FC Cost (AED)'),)
    tmp_sls03 = tmp_sls03.with_columns(pl.col("Posting Date").replace_strict(ashc.Week_, return_dtype=pl.String, default=None).alias('MerchWeek'))
    tmp_sls03 = tmp_sls03.with_columns(pl.col("Posting Date").replace_strict(ashc.Year_, return_dtype=pl.String, default=None).alias('Year'))
    tmp_sls03 = tmp_sls03.with_columns(pl.col("Posting Date").replace_strict(ashc.Month_, return_dtype=pl.String, default=None).alias('Month'))
    tmp_sls03 = tmp_sls03.with_columns(pl.col("Posting Date").replace_strict(ashc.Qtr_, return_dtype=pl.String, default=None).alias('Quarter'))
    tmp_sls03 = tmp_sls03.with_columns(pl.col("Posting Date").replace_strict(ashc.Lyty_, return_dtype=pl.String, default=None).alias('Comp'))
    tmp_sls03 = tmp_sls03.drop(['SaleQty','Total Sale Cost(AED)'])
    df_FCCost = tmp_sls03[rearrangeCols]
    df_FCCost = df_FCCost.with_columns(pl.lit("111").alias('Style Code'),)
    df_FCCost = df_FCCost.with_columns(pl.lit("111").alias('Colour Code'),)
    df_FCCost = df_FCCost.with_columns(pl.lit("All").alias('Sale_Period'),)
    df_FCCost = df_FCCost.with_columns(pl.lit("All").alias('Season_Group'),)
    df_FCCost = df_FCCost.with_columns(pl.lit("All").alias('Theme'),)
    df_FCCost = df_FCCost.with_columns(pl.lit("All").alias('Type'),)
    df_FCCost = df_FCCost.with_columns(pl.lit("All").alias('Disc_Status'),)
    df_FCCost = df_FCCost.with_columns(pl.lit("All").alias('OfferDetail'),)
    df_FCCost = df_FCCost.with_columns(pl.lit("1900-01-01T00:00:00.000000",dtype=pl.Datetime).alias('First Purchase Date'),)
    df_FCCost = df_FCCost.with_columns(pl.lit("1900-01-01T00:00:00.000000",dtype=pl.Datetime).alias('Last Receive Date'),)
    df_FCCost = df_FCCost.with_columns(pl.lit(0.0, dtype=pl.Float32).alias('StoreSize'),)
    df_FCCost = df_FCCost.with_columns(pl.lit(0).alias('Age(Days)'),)
    df_FCCost = df_FCCost.with_columns(pl.lit("All").alias('Age_Group'),)
    df_FCCost = df_FCCost.with_columns(pl.lit("All").alias('YTD'),)
    df_FCCost = df_FCCost.with_columns(pl.lit("All").alias('WTD'),)
    df_FCCost = df_FCCost.with_columns(pl.lit(0.0, dtype=pl.Float32).alias('Unit_Cost'),)
    df_FCCost = df_FCCost.with_columns(pl.lit(0.0, dtype=pl.Float32).alias('Unit_Price'),)
    df_FCCost = df_FCCost.with_columns(pl.lit(0.0, dtype=pl.Float32).alias('Current_Price'),)
    fcCostVal = df_FCCost.group_by(['Comp']).agg(pl.sum(["FC Cost (AED)","FC Qty"]),)
    return df_FCCost

def extractStyleSale(df, file):
    """This function extracts sale for particular styles given as input list from a sale dump file,
    input file is just a simple txt file containing style codes arranged vertically.
    eg: retDF = extractStyleSale(Sale_Dump_df, input_style_file)"""
    fp = open(file,'r')
    data = fp.readlines()
    style_dict = {x.replace('\n',''):1 for x in data}
    df = df.with_columns(pl.col("Style Code").replace(style_dict, return_dtype=pl.Int32, default=None).alias('sFilter'))
    df01 = df.filter(pl.col('sFilter') == 1)
    df01 = df01.drop(['sFilter'])
    return df01

def returnFirstAndLastPurchDate():
    """This function returns first and last received dates in a dict, where key is combination of location code and item no,
    and value is first and last receive date,
    eg: frd, lrd = returnFirstAndLastPurchDate()"""
    lazy_df = pl.scan_csv(ashc.purchDateFiles, schema_overrides=ashc.dataTypeForAll,).collect()
    lazy_df = lazy_df.with_columns((lazy_df['Location Code'] + lazy_df['Item No_']).alias('LocItem'))
    df_tmp = lazy_df.group_by(['LocItem']).agg(
        pl.col('Posting Date').min().alias('First_purchase_date'),
        pl.col('Posting Date').max().alias('Last_purchase_date')
    )
    lazy_df = lazy_df.join(df_tmp, on="LocItem")
    lazy_df = lazy_df.with_columns(pl.when(lazy_df['First_purchase_date'].is_null()).then(lazy_df['Last_purchase_date']).otherwise(lazy_df['First_purchase_date']).alias('First_purchase_date'))

    lazy_df = lazy_df.with_columns(pl.lit(1).alias('Count'),)
    lazy_df = lazy_df.group_by(['LocItem','First_purchase_date','Last_purchase_date']).agg(pl.sum('Count'),)
    dictFRD = Polars_toDict(lazy_df, 'LocItem', 'First_purchase_date')
    dictLRD = Polars_toDict(lazy_df, 'LocItem', 'Last_purchase_date')
    return dictFRD, dictLRD

def returnUnitCost():
    """This Function returns unit cost from stock dump files, 
    return value is three dictionary, first dict is for cost, second is for Org. price and 3rd is for current price,
    return dict contains combination of location code and item no as key and cost/org. curr. prices as value.
    eg: ucs, uop, ucp = returnUnitCost()"""
    stk_df = pl.scan_csv(ashc.stockDumpFiles, schema_overrides=ashc.dataTypeForAll,).collect()
    stkPvt = stk_df.group_by(['Country','Location Code','Item No_']).agg(pl.mean(['Unit Price','Current Retail Price','Unit Cost']),)
    stkPvt = stkPvt.fill_nan(0)
    stkPvt = stkPvt.with_columns((stkPvt['Location Code'] + stkPvt['Item No_']).alias('Combo'))
    ucsx = Polars_toDict(stkPvt, 'Combo', 'Unit Cost')
    upsx = Polars_toDict(stkPvt, 'Combo', 'Unit Price')
    ucpx = Polars_toDict(stkPvt, 'Combo', 'Current Retail Price')

    for key, val in upsx.items():
        upsx[key] = round(val,2)
    
    return ucsx, upsx, ucpx

