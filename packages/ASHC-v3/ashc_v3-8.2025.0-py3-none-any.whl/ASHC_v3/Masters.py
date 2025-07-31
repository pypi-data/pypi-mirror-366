import polars as pl
import ASHC_v3 as ashc
from ASHC_v3.CommonFunction import Polars_toDict

# Functions - JCMerchHier, OKMerchHier, PAMerchHier, VIMerchHier, UZMerchHier, YRMerchHier
def ProcessMasterData(df:pl.DataFrame, brand:str)->pl.DataFrame:
    master_file:str = ""
    sheet:str = ""
    if brand == "JC":
        master_file = ashc.JacadiMaster
        sheet = "JC_Master"
    elif brand == "OK":
        master_file = ashc.OkaidiMaster
        sheet = "OK_Master"
    elif brand == "PA":
        master_file = ashc.PerfoisMaster
        sheet = "PA_Master"
    elif brand == "UZ":
        master_file = ashc.UndizMaster
        sheet = "UZ_Master"
    elif brand == "VI":
        master_file = ashc.VincciMaster
        sheet = "VI_Master"
    elif brand == "YR":
        master_file = ashc.YRMaster
        sheet = "YR_Master"
    elif brand == "LS":
        master_file = ashc.LSMaster
        sheet = "LS_Master"
    else:
        master_file = ""
        sheet = ""

    df_master = pl.read_excel(source=master_file,sheet_name="Sheet1",infer_schema_length=10000,).fill_null(0).fill_nan(0)
    df_master = df_master.with_columns(pl.col('Bar Code').map_elements(lambda x: str(int(float(x))).replace(".0",""), return_dtype=pl.String).alias('Bar Code'),)
    RefCode = Polars_toDict(df_master, 'Bar Code', 'RefCode')
    Style_Code = Polars_toDict(df_master, 'Bar Code', 'Style Code')
    Colour = Polars_toDict(df_master, 'Bar Code', 'Colour')
    Size = Polars_toDict(df_master, 'Bar Code', 'Size')
    Division = Polars_toDict(df_master, 'Bar Code', 'Division')
    ProductGroup = Polars_toDict(df_master, 'Bar Code', 'Product Group')
    ItemCategory = Polars_toDict(df_master, 'Bar Code', 'Item Category')
    ItemClass = Polars_toDict(df_master, 'Bar Code', 'Sub Class')
    SubClass = Polars_toDict(df_master, 'Bar Code', 'Sub Class')
    Theme = Polars_toDict(df_master, 'Bar Code', 'Theme')
    Remarks = Polars_toDict(df_master, 'Bar Code', 'Remarks')
    Season = Polars_toDict(df_master, 'Bar Code', 'Season')
    Extra1 = Polars_toDict(df_master, 'Bar Code', 'Extra-1')
    Extra2 = Polars_toDict(df_master, 'Bar Code', 'Extra-2')
    Extra3 = Polars_toDict(df_master, 'Bar Code', 'Extra-3')
    COO = Polars_toDict(df_master, 'Bar Code', 'COO')

    df = df.with_columns(pl.col("Item No_").replace_strict(RefCode, return_dtype=pl.String, default=None).alias('RefCode'))
    #df = df.with_columns(pl.col("Item No_").replace_strict(Style_Code, return_dtype=pl.String, default=None).alias('Style_Code'))
    #df = df.with_columns(pl.col("Item No_").replace_strict(Colour, return_dtype=pl.String, default=None).alias('Colour'))
    #df = df.with_columns(pl.col("Item No_").replace_strict(Size, return_dtype=pl.String, default=None).alias('Size'))
    df = df.with_columns(pl.col("Item No_").replace_strict(Division, return_dtype=pl.String, default=None).alias('Division'))
    df = df.with_columns(pl.col("Item No_").replace_strict(ProductGroup, return_dtype=pl.String, default=None).alias('Product Group'))
    df = df.with_columns(pl.col("Item No_").replace_strict(ItemCategory, return_dtype=pl.String, default=None).alias('Item Category'))
    df = df.with_columns(pl.col("Item No_").replace_strict(ItemClass, return_dtype=pl.String, default=None).alias('Item Class'))
    df = df.with_columns(pl.col("Item No_").replace_strict(SubClass, return_dtype=pl.String, default=None).alias('Item Sub Class'))
    df = df.with_columns(pl.col("Item No_").replace_strict(Theme, return_dtype=pl.String, default=None).alias('Theme'))
    df = df.with_columns(pl.col("Item No_").replace_strict(Season, return_dtype=pl.String, default=None).alias('Season'))
    df = df.with_columns(pl.col("Item No_").replace_strict(Remarks, return_dtype=pl.String, default=None).alias('Remarks'))
    df = df.with_columns(pl.col("Item No_").replace_strict(Extra1, return_dtype=pl.String, default=None).alias('Extra1'))
    df = df.with_columns(pl.col("Item No_").replace_strict(Extra2, return_dtype=pl.String, default=None).alias('Extra2'))
    df = df.with_columns(pl.col("Item No_").replace_strict(Extra3, return_dtype=pl.String, default=None).alias('Extra3'))
    df = df.with_columns(pl.col("Item No_").replace_strict(COO, return_dtype=pl.String, default=None).alias('COO'))
    df = df.fill_null(0).fill_nan(0)
    return df

def JCMerchHier(df):
    # JC Master
    dfTemp = ProcessMasterData(df,"JC")
    return dfTemp

def OKMerchHier(df):
    # OK Master
    dfTemp = ProcessMasterData(df,"OK")
    return dfTemp

def PAMerchHier(df):
    # Perfois Master
    dfTemp = ProcessMasterData(df,"PA")
    return dfTemp

def UZMerchHier(df):
    # UZ Master
    dfTemp = ProcessMasterData(df,"UZ")
    return dfTemp

def VIMerchHier(df):
    # VI Master
    dfTemp = ProcessMasterData(df,"VI")
    return dfTemp

def YRMerchHier(df):
    # YR Master
    dfTemp = ProcessMasterData(df,"YR")
    return dfTemp

def LSMerchHier(df):
    # LS Master
    dfTemp = ProcessMasterData(df,"LS")
    return dfTemp