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
# MAGIC CREATE TABLE IF NOT EXISTS Gold_Layer.Product(
# MAGIC     Product_ID long,
# MAGIC     Product_Category string,
# MAGIC     Product string,
# MAGIC     Created_TS timestamp,
# MAGIC     Modified_TS timestamp
# MAGIC )
# MAGIC USING DELTA

# CELL ********************

vMax_Date = spark.sql("select COALESCE(max(Modified_TS),'1900-01-01') from Gold_Layer.Product").first()[0]

# CELL ********************

print(vMax_Date)

# CELL ********************

df = spark.sql("""Select distinct
        Product_Category,
        Product
    from Bronze_Layer.sales where Modified_TS > '{}'""".format(vMax_Date))

# CELL ********************

vMax_Product_ID = spark.sql("select COALESCE(max(Product_ID),0) from Gold_Layer.Product").first()[0]
print(vMax_Product_ID)

# CELL ********************

df_final  = df.withColumn("Product_ID",monotonically_increasing_id() + lit(vMax_Product_ID) + 1)

# CELL ********************

df_final.createOrReplaceTempView("ViewProduct")

# CELL ********************

# MAGIC %%sql
# MAGIC MERGE INTO Gold_Layer.Product AS pd
# MAGIC USING ViewProduct AS vp
# MAGIC ON (pd.Product_Category = vp.Product_Category) AND  (pd.Product = vp.Product)
# MAGIC WHEN MATCHED THEN
# MAGIC     UPDATE SET  
# MAGIC     pd.Modified_TS = CURRENT_TIMESTAMP()
# MAGIC WHEN NOT MATCHED THEN
# MAGIC     INSERT (
# MAGIC         pd.Product_ID,
# MAGIC         pd.Product_Category,
# MAGIC         pd.Product,
# MAGIC         pd.Created_TS,
# MAGIC         pd.Modified_TS
# MAGIC     )
# MAGIC VALUES (
# MAGIC         vp.Product_ID,
# MAGIC         vp.Product_Category,
# MAGIC         vp.Product,
# MAGIC         CURRENT_TIMESTAMP(),
# MAGIC         CURRENT_TIMESTAMP()
# MAGIC     );
