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
# META         },
# META         {
# META           "id": "c30b6e57-1cc1-4f4e-92b3-20fab14b5de5"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

# Welcome to your new notebook
# Type here in the cell editor to add code!
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import*

# CELL ********************

# MAGIC %%sql
# MAGIC CREATE table if not EXISTS Gold_Layer.fact_sales
# MAGIC (
# MAGIC     Order_ID String,
# MAGIC     Price float,
# MAGIC     Quaantity float,
# MAGIC     Sales float,
# MAGIC     Discount float,
# MAGIC     Profit float,
# MAGIC     Shipping_Cost float,
# MAGIC     Order_Date date,
# MAGIC     Shipping_Date date,
# MAGIC     Product_ID long,
# MAGIC     OrderPriority_ID long,
# MAGIC     ShipMode_ID long,
# MAGIC     Customer_ID string,
# MAGIC     Order_Year int,
# MAGIC     Order_Month int,
# MAGIC     Created_TS timestamp,
# MAGIC     Modified_TS timestamp
# MAGIC )
# MAGIC using DELTA
# MAGIC PARTITIONED BY(Order_Year, Order_Month)

# CELL ********************

vMax_Date = spark.sql("select COALESCE(max(Modified_TS),'1900-01-01') from Gold_Layer.fact_sales").first()[0]
vMax_Date

# CELL ********************

df_fact_sales = spark.sql(
"""SELECT 
     bs.Order_ID,
     cast(bs.Sales as float) as Price,
     cast(bs.Quantity as float) as Quantity,
     cast(bs.Sales * bs.Quantity as float) as Sales,
     cast(bs.Discount as float) as Discount,
     cast(bs.Profit as float) as Profit,
     cast(bs.Shipping_Cost as float) as Shipping_Cost,
     bs.Order_Date,
     bs.Shipping_Date,
     gp.Product_ID,
     op.OrderPriority_ID,
     sm.ShipMode_ID,
     bs.Customer_ID,
     Year(Order_Date) as Order_Year,
     Month(Order_Date) as Order_Month
FROM
bronze_layer.sales bs
inner join Gold_Layer.product gp on bs.Product = gp.Product and bs.Product_Category = gp.Product_Category
inner join Gold_Layer.shipmode sm on bs.Ship_Mode = sm.Ship_Mode
inner join Gold_Layer.orderpriority op on bs.Order_Priority = op.Order_Priority
where bs.Modified_TS > '{}'""".format(vMax_Date)
)

# CELL ********************

display(df_fact_sales)

# CELL ********************

df_fact_sales.createOrReplaceTempView("ViewFactSale")

# CELL ********************

# MAGIC %%sql
# MAGIC merge into Gold_Layer.fact_sales as gfs
# MAGIC using ViewFactSale as vfs 
# MAGIC on gfs.Order_Year=vfs.Order_Year and gfs.Order_Month=vfs.Order_Month and gfs.Order_ID=vfs.Order_ID
# MAGIC when matched then 
# MAGIC update SET
# MAGIC gfs.Sales= vfs.Sales,
# MAGIC gfs.Price = vfs.Price,
# MAGIC gfs.Quaantity = vfs.Quantity,
# MAGIC gfs.Discount = vfs.Discount,
# MAGIC gfs.Profit = vfs.Profit,
# MAGIC gfs.Shipping_Cost = vfs.Shipping_Cost,
# MAGIC gfs.Order_Date = vfs.Order_Date,
# MAGIC gfs.Shipping_Date =vfs.Shipping_Date,
# MAGIC gfs.Product_ID = vfs.Product_ID,
# MAGIC gfs.OrderPriority_ID= vfs.OrderPriority_ID,
# MAGIC gfs.ShipMode_ID= vfs.ShipMode_ID,
# MAGIC gfs.Customer_ID= vfs.Customer_ID,
# MAGIC gfs.Modified_TS= current_timestamp()
# MAGIC when not matched then
# MAGIC INSERT
# MAGIC (
# MAGIC     gfs.Order_ID,
# MAGIC     gfs.Sales,
# MAGIC     gfs.Price,
# MAGIC     gfs.Quaantity,
# MAGIC     gfs.Discount,
# MAGIC     gfs.Profit,
# MAGIC     gfs.Shipping_Cost,
# MAGIC     gfs.Order_Date,
# MAGIC     gfs.Shipping_Date,
# MAGIC     gfs.Product_ID,
# MAGIC     gfs.OrderPriority_ID,
# MAGIC     gfs.ShipMode_ID,
# MAGIC     gfs.Customer_ID,
# MAGIC     gfs.Order_Year,
# MAGIC     gfs.Order_Month,
# MAGIC     gfs.Created_TS,
# MAGIC     gfs.Modified_TS
# MAGIC )
# MAGIC VALUES
# MAGIC (
# MAGIC         vfs.Order_ID,
# MAGIC         vfs.Sales,
# MAGIC         vfs.Price,
# MAGIC         vfs.Quantity,
# MAGIC         vfs.Discount,
# MAGIC         vfs.Profit,
# MAGIC         vfs.Shipping_Cost,
# MAGIC         vfs.Order_Date,
# MAGIC         vfs.Shipping_Date,
# MAGIC         vfs.Product_ID,
# MAGIC         vfs.OrderPriority_ID,
# MAGIC         vfs.ShipMode_ID,
# MAGIC         vfs.Customer_ID,
# MAGIC         vfs.Order_Year,
# MAGIC         vfs.Order_Month,
# MAGIC         current_timestamp(),
# MAGIC         current_timestamp()
# MAGIC     )

# CELL ********************

# MAGIC %%sql
# MAGIC SELECT * FROM Gold_Layer.fact_sales LIMIT 1000

# CELL ********************

