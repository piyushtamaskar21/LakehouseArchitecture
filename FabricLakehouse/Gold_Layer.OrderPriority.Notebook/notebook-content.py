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
from delta.tables import *

# CELL ********************

DeltaTable.createIfNotExists(spark)\
          .tableName("Gold_Layer.OrderPriority")\
          .addColumn("OrderPriority_ID", LongType())\
          .addColumn("Order_Priority", StringType())\
          .addColumn("Created_TS", TimestampType())\
          .addColumn("Modified_TS", TimestampType())\
          .execute()

# CELL ********************

df = spark.read.table("Gold_Layer.orderpriority")

# CELL ********************

vMax_Date = df.selectExpr("coalesce(max(Modified_TS),'1900-01-01')").first()[0]

# CELL ********************

df_sales_bronze = spark.read.table("Bronze_Layer.sales")

# CELL ********************

df_sales_bronze_mod = df_sales_bronze.select("Order_Priority").where(col("Modified_TS")>vMax_Date).drop_duplicates()

# CELL ********************

Max_ID = df.selectExpr("coalesce(max(OrderPriority_ID),0)").first()[0]

# CELL ********************

print(Max_ID)

# CELL ********************

df_final = df_sales_bronze_mod.withColumn(
    "OrderPriority_ID", 
    lit(Max_ID) + monotonically_increasing_id() + 1  
)

# CELL ********************

df_gold_delta = DeltaTable.forPath(spark, "abfss://LakehouseArchitecture@onelake.dfs.fabric.microsoft.com/Gold_Layer.Lakehouse/Tables/orderpriority")
df_bronze_table = df_final

# CELL ********************

df_bronze_table.show()

# CELL ********************

df_gold_delta.alias("gold")\
             .merge(\
             df_bronze_table.alias("bronze"),\
             "gold.Order_Priority==bronze.Order_Priority"\
             )\
             .whenMatchedUpdate(\
                    set={
                        "gold.Modified_TS":current_timestamp()
                    }
            )\
             .whenNotMatchedInsert(\
                    values={
                       "gold.OrderPriority_ID":"Bronze.OrderPriority_ID",
                       "gold.Order_Priority":"Bronze.Order_Priority",
                       "gold.Created_TS":current_timestamp(),
                       "gold.Modified_TS":current_timestamp()     
                    }
             )\
             .execute()

# CELL ********************

# MAGIC %%sql
# MAGIC Select * from gold_layer.orderpriority

# CELL ********************

