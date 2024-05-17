# Fabric notebook source

# METADATA ********************

# META {
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "026e37f1-1eff-4871-b3cb-faad22143daa",
# META       "default_lakehouse_name": "Bronze_Layer",
# META       "default_lakehouse_workspace_id": "fb2314eb-64cc-4d6f-90a5-518da07767b0",
# META       "known_lakehouses": [
# META         {
# META           "id": "026e37f1-1eff-4871-b3cb-faad22143daa"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

# Welcome to your new notebook
# Type here in the cell editor to add code!
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql import *

# CELL ********************

sales_schema = StructType(
    [
        StructField("Order_ID",StringType()),
        StructField("Order_Date", DateType()),
        StructField("Shipping_Date", DateType()),
        StructField("Aging", StringType()), 
        StructField("Ship_Mode", StringType()),
        StructField("Product_Category", StringType()),
        StructField("Product", StringType()),
        StructField("Sales", FloatType()),
        StructField("Quantity", IntegerType()),
        StructField("Discount", FloatType()),
        StructField("Profit",  FloatType()),
        StructField("Shipping_Cost", FloatType()),
        StructField("Order_Priority", StringType()),
        StructField("Customer_ID",  StringType()),
        StructField("Customer_Name",  StringType()),
        StructField("Segment", StringType()),
        StructField("City", StringType()),
        StructField("State", StringType()),
        StructField("Country", StringType()),
        StructField("Region", StringType()),
    ]
)

# CELL ********************

sales_df = spark.read.format("csv").schema(sales_schema).option("header","true").load("abfss://LakehouseArchitecture@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Files/Current/Sales_*.csv")
# sales_df now is a Spark DataFrame containing CSV data from All Sales files".
display(sales_df)



# CELL ********************

returns_df = spark.read.format("csv").option("header","true").load("abfss://LakehouseArchitecture@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Files/Current/Returns_*.csv")
# sales_df now is a Spark DataFrame containing CSV data from All Sales files".
display(returns_df)

# CELL ********************

final_df = sales_df.join(returns_df, sales_df.Order_ID==returns_df.Order_ID,how="left").\
                    drop(returns_df.Order_ID, returns_df.Customer_Name, returns_df.Sales_Amount)

# CELL ********************

final_df = final_df.withColumns({"Order_Year":year("Order_Date"),\
                   "Order_Month":month("Order_Date"),\
                   "Create_TS":current_timestamp(),\
                   "Modified_TS":current_timestamp(),\
})

# CELL ********************

final_df.createOrReplaceTempView("BronzeSales")

# CELL ********************

# MAGIC %%sql
# MAGIC CREATE TABLE IF not EXISTS Bronze_Layer.Sales
# MAGIC (
# MAGIC         Order_ID string,
# MAGIC         Order_Date date,
# MAGIC         Shipping_Date date,
# MAGIC         Aging string,
# MAGIC         Ship_Mode string,
# MAGIC         Product_Category string,
# MAGIC         Product string,
# MAGIC         Sales float,
# MAGIC         Quantity int,
# MAGIC         Discount float,
# MAGIC         Profit float,
# MAGIC         Shipping_Cost float,
# MAGIC         Order_Priority string,
# MAGIC         Customer_ID string,
# MAGIC         Customer_Name string,
# MAGIC         Segment string,
# MAGIC         City string,
# MAGIC         State string,
# MAGIC         Country string,
# MAGIC         Region string,
# MAGIC         Return string,
# MAGIC         Order_Year int,
# MAGIC         Order_Month int,
# MAGIC         Create_TS TIMESTAMP,
# MAGIC         Modified_TS TIMESTAMP
# MAGIC )
# MAGIC USING DELTA
# MAGIC PARTITIONED BY(Order_Year, Order_Month)

# CELL ********************

final_df.columns

# CELL ********************

# MAGIC %%sql
# MAGIC MERGE INTO Bronze_Layer.Sales as bs 
# MAGIC using BronzeSales as vs 
# MAGIC on bs.Order_Year = vs.Order_Year and bs.Order_Month = vs.Order_Month and bs.Order_ID = vs.Order_ID
# MAGIC when matched THEN
# MAGIC UPDATE SET
# MAGIC bs.Order_Date = vs.Order_Date,
# MAGIC bs.Shipping_Date = vs.Shipping_Date ,
# MAGIC bs.Aging = vs.Aging, 
# MAGIC bs.Ship_Mode = vs.Ship_Mode,
# MAGIC bs.Product_Category = vs.Product_Category,
# MAGIC bs.Product = vs.Product,
# MAGIC bs.Sales = vs.Sales,
# MAGIC bs.Quantity = vs.Quantity,
# MAGIC bs.Discount = vs.Discount,
# MAGIC bs.Profit = vs.Profit,
# MAGIC bs.Shipping_Cost = vs.Shipping_Cost,
# MAGIC bs.Order_Priority = vs.Order_Priority,
# MAGIC bs.Customer_ID = vs.Customer_ID,
# MAGIC bs.Customer_Name = vs.Customer_Name,
# MAGIC bs.Segment = vs.Segment,
# MAGIC bs.City = vs.City,
# MAGIC bs.State = vs.State,
# MAGIC bs.Country = vs.Country,
# MAGIC bs.Region = vs.Region,
# MAGIC bs.Return = vs.Return,
# MAGIC bs.Create_TS = CURRENT_TIMESTAMP(),
# MAGIC bs.Modified_TS = CURRENT_TIMESTAMP()
# MAGIC WHEN NOT MATCHED THEN
# MAGIC INSERT 
# MAGIC (
# MAGIC     Order_ID,
# MAGIC     Order_Date,
# MAGIC     Shipping_Date,
# MAGIC     Aging,
# MAGIC     Ship_Mode,
# MAGIC     Product_Category,
# MAGIC     Product,
# MAGIC     Sales,
# MAGIC     Quantity,
# MAGIC     Discount,
# MAGIC     Profit,
# MAGIC     Shipping_Cost,
# MAGIC     Order_Priority,
# MAGIC     Customer_ID,
# MAGIC     Customer_Name,
# MAGIC     Segment,
# MAGIC     City,
# MAGIC     State,
# MAGIC     Country,
# MAGIC     Region,
# MAGIC     Return,
# MAGIC     Order_Year,
# MAGIC     Order_Month,
# MAGIC     Create_TS,
# MAGIC     Modified_TS
# MAGIC )
# MAGIC VALUES
# MAGIC (
# MAGIC     vs.Order_ID,
# MAGIC     vs.Order_Date,
# MAGIC     vs.Shipping_Date,
# MAGIC     vs.Aging,
# MAGIC     vs.Ship_Mode,
# MAGIC     vs.Product_Category,
# MAGIC     vs.Product,
# MAGIC     vs.Sales,
# MAGIC     vs.Quantity,
# MAGIC     vs.Discount,
# MAGIC     vs.Profit,
# MAGIC     vs.Shipping_Cost,
# MAGIC     vs.Order_Priority,
# MAGIC     vs.Customer_ID,
# MAGIC     vs.Customer_Name,
# MAGIC     vs.Segment,
# MAGIC     vs.City,
# MAGIC     vs.State,
# MAGIC     vs.Country,
# MAGIC     vs.Region,
# MAGIC     vs.Return,
# MAGIC     vs.Order_Year,
# MAGIC     vs.Order_Month,
# MAGIC     vs.Create_TS,
# MAGIC     vs.Modified_TS
# MAGIC 
# MAGIC )
