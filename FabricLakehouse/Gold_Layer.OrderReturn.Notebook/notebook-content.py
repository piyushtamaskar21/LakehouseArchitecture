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
# META           "id": "c30b6e57-1cc1-4f4e-92b3-20fab14b5de5"
# META         },
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

# MAGIC %%sql
# MAGIC CREATE TABLE IF NOT EXISTS Gold_Layer.OrderReturn(
# MAGIC     Order_ID string,
# MAGIC     ReturnFlag string,
# MAGIC     Order_Year int,
# MAGIC     Order_Month int,
# MAGIC     Created_TS timestamp,
# MAGIC     Modified_TS timestamp
# MAGIC )
# MAGIC USING DELTA
# MAGIC PARTITIONED BY(Order_Year, Order_Month)

# CELL ********************

vMax_Date = spark.sql("select COALESCE(max(Modified_TS),'1900-01-01') from Gold_Layer.OrderReturn").first()[0]

# CELL ********************

print(vMax_Date)

# CELL ********************

df = spark.sql("""Select 
        Order_Id
        , Return
        , Order_Year
        , Order_Month
        , Create_TS
        , Modified_TS
    from Bronze_Layer.sales where Return = "Yes" and Modified_TS > '{}'""".format(vMax_Date))

# CELL ********************

df.createOrReplaceTempView('ViewReturn')

# CELL ********************

# MAGIC %%sql
# MAGIC insert into Gold_Layer.OrderReturn
# MAGIC Select * from ViewReturn
