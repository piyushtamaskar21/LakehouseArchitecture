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
# MAGIC CREATE TABLE IF NOT EXISTS Gold_Layer.ShipMode(
# MAGIC     ShipMode_ID int,
# MAGIC     Ship_Mode string,
# MAGIC     Created_TS timestamp,
# MAGIC     Modified_TS timestamp
# MAGIC )
# MAGIC USING DELTA

# CELL ********************

vMax_Date = spark.sql("select COALESCE(max(Modified_TS),'1900-01-01') from Gold_Layer.ShipMode").first()[0]

# CELL ********************

print(vMax_Date)

# CELL ********************

df = spark.sql("""Select distinct
        Ship_Mode
    from Bronze_Layer.sales where Modified_TS > '{}'""".format(vMax_Date))

# CELL ********************

vMax_ShipMode_ID = spark.sql("select COALESCE(max(ShipMode_ID),0) from Gold_Layer.ShipMode").first()[0]
print(vMax_ShipMode_ID)

# CELL ********************

df_final  = df.withColumn("ShipMode_ID",monotonically_increasing_id() + lit(vMax_ShipMode_ID) + 1)

# CELL ********************

df_final.createOrReplaceTempView("ViewShipMode")

# CELL ********************

# MAGIC %%sql
# MAGIC Select * from ViewShipMode

# CELL ********************

# MAGIC %%sql
# MAGIC MERGE INTO Gold_Layer.shipmode AS gs
# MAGIC USING ViewShipMode AS vs
# MAGIC ON gs.Ship_Mode = vs.Ship_Mode  
# MAGIC WHEN MATCHED THEN
# MAGIC     UPDATE SET gs.Modified_TS = CURRENT_TIMESTAMP()
# MAGIC WHEN NOT MATCHED THEN
# MAGIC     INSERT (
# MAGIC         gs.ShipMode_ID,
# MAGIC         gs.Ship_Mode,
# MAGIC         gs.Created_TS,
# MAGIC         gs.Modified_TS
# MAGIC     )
# MAGIC VALUES (
# MAGIC         vs.ShipMode_ID,
# MAGIC         vs.Ship_Mode,
# MAGIC         CURRENT_TIMESTAMP(),
# MAGIC         CURRENT_TIMESTAMP()
# MAGIC     );
