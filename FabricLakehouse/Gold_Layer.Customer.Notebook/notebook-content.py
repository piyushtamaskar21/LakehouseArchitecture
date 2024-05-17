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
# MAGIC CREATE TABLE IF NOT EXISTS Gold_Layer.Customer(
# MAGIC     Customer_ID string,
# MAGIC     Customer_Name string,
# MAGIC     Segment string,
# MAGIC     City string,
# MAGIC     State string,
# MAGIC     Country string,
# MAGIC     Region string,
# MAGIC     Created_TS timestamp,
# MAGIC     Modified_TS timestamp
# MAGIC )
# MAGIC USING DELTA

# CELL ********************

vMax_Date = spark.sql("select COALESCE(max(Modified_TS),'1900-01-01') from Gold_Layer.Customer").first()[0]

# CELL ********************

print(vMax_Date)

# CELL ********************

df = spark.sql("""Select distinct
        Customer_ID
        , Customer_Name
        , Segment
        , City
        , State
        , Country
        , Region
        , Create_TS
        , Modified_TS
    from Bronze_Layer.sales where Modified_TS > '{}'""".format(vMax_Date))

# CELL ********************

df.show()

# CELL ********************

df.createOrReplaceTempView('ViewCustomer')

# CELL ********************

# MAGIC %%sql
# MAGIC MERGE INTO Gold_Layer.Customer AS cs
# MAGIC USING ViewCustomer AS vc
# MAGIC ON cs.Customer_ID = vc.Customer_ID
# MAGIC WHEN MATCHED THEN
# MAGIC     UPDATE SET
# MAGIC         cs.Customer_Name = vc.Customer_Name,
# MAGIC         cs.Segment = vc.Segment,
# MAGIC         cs.City = vc.City,
# MAGIC         cs.State = vc.State,
# MAGIC         cs.Country = vc.Country,
# MAGIC         cs.Region = vc.Region,
# MAGIC         cs.Modified_TS = CURRENT_TIMESTAMP()
# MAGIC WHEN NOT MATCHED THEN
# MAGIC     INSERT (
# MAGIC         cs.Customer_ID,
# MAGIC         cs.Customer_Name,
# MAGIC         cs.Segment,
# MAGIC         cs.City,
# MAGIC         cs.State,
# MAGIC         cs.Country,
# MAGIC         cs.Region,
# MAGIC         cs.Modified_TS,
# MAGIC         cs.Created_TS
# MAGIC     )
# MAGIC VALUES (
# MAGIC         vc.Customer_ID,
# MAGIC         vc.Customer_Name,
# MAGIC         vc.Segment,
# MAGIC         vc.City,
# MAGIC         vc.State,
# MAGIC         vc.Country,
# MAGIC         vc.Region,
# MAGIC         CURRENT_TIMESTAMP(),
# MAGIC         CURRENT_TIMESTAMP()
# MAGIC     );

