# This Python file uses the following encoding: utf-8
import polars as pl
import os,sys
import datetime as dt

__all__ = ["initiateConfig","calculateFCCost","changeFWSeason","cummelativeSale","dictMerge","discountSlab",
           "extractStyleSale","fnAgeMap","fnCurrencyConverter","jacadiWeeklySellthruReport","JCMerchHier",
           "makeCSV","makeDateIndex","makeDateRangeDict","makeMTD_YTDIndex","makeSaleSeasonDict","makeSaleSeasonIndex",
           "MapOffer","okaidiWeeklyBestSellerReport","okaidiWeeklySellthruReport",
           "Polars_toDict","prepareBudgetFiles","prepareKPIFiles","prepareSaleDF","prepareStockDF","removeWarehouseSale",
           "removeWarehouseSaleFromCombined","returnFirstAndLastPurchDate","returnUnitCost"]

dataTypeForAll = {"ATV":pl.String, "Bar Code":pl.String, 'Brand':pl.String, 'Location':pl.String, 'Barcode':pl.String, 'Combo':pl.String, 
                  'Offer':pl.String, "Brand Code":pl.String, "Buyers":pl.String, "Buyers with Traffic":pl.Int32, "Category":pl.String, 
                  "CF Store Status":pl.String, "City":pl.String, "Closing Ratio":pl.Float32, "Closing Stock":pl.Float32, "Colour":pl.String, 
                  "Colour Code":pl.String, "Comparable":pl.String, "Cord Sets":pl.String, "CostValue":pl.Float32, "Country":pl.String, 
                  "Country Region Code":pl.String, "Current Retail Price":pl.Float32, "Date":pl.String, "Date Day":pl.String, 
                  "Date Day Description":pl.String, "Date Day Number":pl.String, "Date Month":pl.String, "Date Month Description":pl.String, 
                  "Date Month Number":pl.String, "Date Year":pl.String, "Date Year Number":pl.String, "Description":pl.String, "Division":pl.String, 
                  "Family":pl.String, "Fashion Type":pl.String, "First Purchase Date":pl.Datetime, "Image Reference":pl.String, "IPC":pl.String, 
                  "Item Category":pl.String, "Item Class":pl.String, "Item No_":pl.String, "Item Sub Class":pl.String, 
                  "Last Purchase Date":pl.Datetime, "LFL":pl.String, "LOC_Item":pl.String, "LOC_Item1":pl.String, "LOC_Item2":pl.String, 
                  "LOC_Item3":pl.String, "Location Code":pl.String, "Location Name":pl.String, "Mall Owner":pl.String, "MTD CostValue":pl.Float32, 
                  "MTD SaleQty":pl.Float32, "MTD SaleValue":pl.Float32, "Post Code":pl.String, "Posting Date":pl.Datetime, "Product Group":pl.String, 
                  "Profit Centre Code":pl.String, "Profit Centre Name":pl.String, "Remarks":pl.String, "SaleQty":pl.Float32, "Sales Amount":pl.String, 
                  "Sales Amount LCY":pl.String, "SaleValue":pl.Float32, "Saved":pl.String, "Season":pl.String, "Season Code":pl.String, 
                  "Short Name":pl.String, "Size":pl.String, "Sold Qty":pl.String, "Store Closing Date Day":pl.String, 
                  "Store Closing Date Day Description":pl.String, "Store Closing Date Day Number":pl.String, "Store Closing Date Month":pl.String, 
                  "Store Closing Date Month Description":pl.String, "Store Closing Date Month Number":pl.String, "Store Closing Date Year":pl.String, 
                  "Store Closing Date Year Number":pl.String, "Store Opening Date":pl.String, "Store Opening Date Month":pl.String, 
                  "Store Opening Date Month Description":pl.String, "Store Opening Date Month Number":pl.String, "Store Opening Date Year":pl.String, 
                  "Store Opening Date Year Number":pl.String, "Store Size Square Meters":pl.Float32, "StoreName":pl.String, "Style Code":pl.String, 
                  "Sub Class":pl.String, "SubFamily":pl.String, "Target":pl.String, "Target Amout":pl.String, "Target Amout LCY":pl.Float32, 
                  "Theme":pl.String, "Type":pl.String, "Unit Cost":pl.Float32, "Unit Price":pl.Float32, "Unit Price Including VAT":pl.Float32, 
                  "Var %":pl.String, "Visitors":pl.String, "WTD CostValue":pl.Float32, "WTD SaleQty":pl.Float32, "WTD SaleValue":pl.Float32, 
                  "YTD CostValue":pl.Float32, "YTD SaleQty":pl.Float32, "YTD SaleValue":pl.Float32, 'First_purchase_date':pl.Datetime,
                  'Last_purchase_date':pl.Datetime, 'Original Retail':pl.Float32, 'Sale Price':pl.Float32}

selectSeason = ["All","FLW","NOS","25H","25E","24H","24E","23H","23E","2023-2","2023-01","2024-1","2024-2","2025-1","2025-2","2026-1","2512","2511",
                "2510","2509","2508","2507","2506","2505","2504","2503","2502","2501","2412","2411","2410","2409","2408","2407","2406","2405","2404",
                "2403","2402","2401","2312","2311","2310","2309","2308","2307","2306","2305","2304","2303","2302","2301","2212","2211","2210","2209",
                "2208"]

delLocation = ["DE98","A01JC99","JC99","A01JC-TR","A05JC99","A05JC-TR","A01OK3PL","A01OK99","OK92","OK98","OK99","OK99R","OK99S","A01OK-TR","A02OK99",
               "OK00","OK99T","A06OK99","INTRANSIT","A05OK-TR","OK90","A03OK-TR","A02OK-TR","PA98","PA99","A01PA-TR","PA01D","PA06D","PA09D","PA11D",
               "PA12D","PA15D","PA16D","PA23D","PA24D","PA25D","PA26D","PA27D","PA29D","PA31D","PA99D","PA99S","A06PA-TR","A05PA-TR","PA92","A03PA-TR",
               "UZ98","UZ99","A01UZ-TR","UZ99D","UZ99R","UZ90","A03UZ-TR","VI98","VI99","A01VI-TR","VI00","VI99D","VI99R","A06VI-TR","VI90","A03VI-TR",
               "VI92","VI93","A02VI-TR","YR89","YR99","A01YR-TR","YR99D","YR99M","YR99R","A01PA3PL","LS99M","LS100BE","LS98"]

fcSaleSeason = {"JC":"25H","OK":"25H","PA":"2025-2","UZ":"2025-2","VI":"2504","YR":"FLW","LS":"FLW"}
FC_Week = 8
fcCostDays = 56
mark = False
debugGen = False
configData = pl.DataFrame()
lflData = pl.DataFrame()
dateData = pl.DataFrame()
ShortStoreName = {}
StoreName = {}
BrandName = {}
Country = {}
City = {}
LocationType = {}
Status = {}
Area = {}
OpeningDate = {}
LocCode = {}
Year_ = {}
Qtr_ = {}
Month_ = {}
Week_ = {}
Lyty_ = {}
Lfl = {}
budFile = ''
kpiFile = ''
sysPriceFiles = ''
purchDateFiles = ''
stockDumpFiles = ''
offerFile = ''
xlConfigFile = ''
UndizMaster = ''
VincciMaster = ''
YRMaster = ''
JacadiMaster = ''
OkaidiMaster = ''
PerfoisMaster = ''
LSMaster = ''

last = dt.date(2025, 12, 31)
tod = dt.date.today()
currDir = os.getcwd()
if (tod > last):
    sys.exit(0)
