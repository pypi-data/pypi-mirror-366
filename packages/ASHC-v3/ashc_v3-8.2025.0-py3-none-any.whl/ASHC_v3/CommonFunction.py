import os
import polars as pl
import ASHC_v3 as ashc

# Functions - dictMerge, MapOffer, discountSlab, fnAgeMap, fnCurrencyConverter, makeCSV, Polars_toDict, changeFWSeason
def dictMerge(dict1, dict2):
    retDict = {}
    retDict.update(dict1)
    retDict.update(dict2)
    return retDict

def MapOffer(df):
    #Offer Master
    offerFileDF  = pl.scan_csv(ashc.offerFile, schema_overrides=ashc.dataTypeForAll,).collect()
    #----------------------------------------------------------
    commKey = offerFileDF.to_dict(as_series=True)['Combo']
    offer_1 = offerFileDF.to_dict(as_series=True)['Offer']
    offer_2 = offerFileDF.to_dict(as_series=True)['Sale Price']
    offerDisc = dict(zip(commKey, offer_1))
    offerPrice = dict(zip(commKey, offer_2))
    #----------------------------------------------------------
    df = df.with_columns((df['Brand Code'] + df['Country'] + df['Item No_']).alias('Offer_Lookup'))
    df = df.with_columns(pl.col("Offer_Lookup").replace_strict(offerDisc, return_dtype=pl.String, default=None).alias('OfferDetail'))
    df = df.with_columns(pl.col('Disc.P').cast(pl.Float32).alias('Disc.P'))
    df = df.with_columns(pl.col('Disc.P').map_elements(discountSlab, return_dtype=pl.String).alias('Discount Slab'))
    df = df.with_columns(pl.col("Offer_Lookup").replace_strict(offerPrice, return_dtype=pl.Float32, default=None).alias('Offer_Price'))
    df = df.fill_nan(0)
    #df = df.drop(["Offer_Lookup","OfferDetail"])
    return df

def discountSlab(x):
    try:
        if x <= 0.10:
            return "Full Price"
        elif (x > 0.10 and x <= 0.30):
            return "Under 30%"
        elif (x > 0.30 and x <= 0.40):
            return "Under 30% - 40%"
        elif (x > 0.40 and x <= 0.50):
            return "Under 40% - 50%"
        elif (x > 0.50 and x <= 0.60):
            return "Under 50% - 60%"
        else:
            return "More than 60%"
    except:
        print(f"Error in converting : {x}")
        return 0
    
def fnAgeMap(ageDays):
    if ageDays > 0 and ageDays <= 45:
        return "000-045 Days"
    elif ageDays > 45 and ageDays <= 90:
        return "046-090 Days"
    elif ageDays > 90 and ageDays <= 180:
        return "091-180 Days"
    elif ageDays > 180 and ageDays <= 365:
        return "181-365 Days"
    else:
        return "Above 365 Days"
    
def fnCurrencyConverter(country):
    if country == "AE":
        return 1.00000
    elif country == "BH":
        return 9.74143
    elif country == "OM":
        return 9.53929
    elif country == "QA":
        return 1.00878
    elif country == "KWT":
        return 12.00000
    else:
        return 0
    
def makeCSV(df,fileName):
    df.write_csv(os.path.join(ashc.outFolder, fileName), separator=",")

def Polars_toDict(df, dKey, dVal):
    df = df.fill_nan(0)
    commKey = df.to_dict(as_series=True)[dKey]
    DictVal = df.to_dict(as_series=True)[dVal]
    return dict(zip(commKey, DictVal))

def changeFWSeason(seasonCode):
    if (str(seasonCode) == "26E"):
        return "25E"
    elif (str(seasonCode) == "26H"):
        return "25E"
    elif (str(seasonCode) == "2026-1"):
        return "2025-1"
    elif (str(seasonCode) == "2026-2"):
        return "2025-1"
    else:
        return seasonCode