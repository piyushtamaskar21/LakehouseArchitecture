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
# MAGIC DROP TABLE IF EXISTS Gold_Layer.DimDate;
# MAGIC CREATE TABLE IF NOT EXISTS Gold_Layer.DimDate(
# MAGIC     BusinessDate date,
# MAGIC     Business_Year int,
# MAGIC     Business_Month int,
# MAGIC     Business_Quarter int,
# MAGIC     Business_Week int
# MAGIC )
# MAGIC USING DELTA
# MAGIC PARTITIONED by (Business_year)

# CELL ********************

vStart_Date = spark.sql("select COALESCE(min(Order_Date),'1900-01-01') from Bronze_Layer.sales").first()[0]
vEnd_Date = spark.sql("select COALESCE(max(Order_Date),'1900-01-01') from Bronze_Layer.sales").first()[0]

# CELL ********************

print(vStart_Date)
print(vEnd_Date)
date_diff = spark.sql("Select date_diff('{}','{}')".format(vEnd_Date, vStart_Date)).first()[0]
print(date_diff)

# CELL ********************

ID_Data = spark.range(0,date_diff)

# CELL ********************

date_data = ID_Data.selectExpr("date_add('{}', cast(id as int)) as BusinessDate".format(vStart_Date))

# CELL ********************

date_data = date_data.withColumn("Business_Year", year(col("BusinessDate")))\
        .withColumn("Business_Month", month(col("BusinessDate")))\
        .withColumn("Business_Quarter", quarter(col("BusinessDate")))\
        .withColumn("Business_Week", weekofyear(col("BusinessDate")))


# CELL ********************

date_data.createOrReplaceTempView("ViewDate")

# CELL ********************

# MAGIC %%sql
# MAGIC INSERT INTO Gold_Layer.DimDate
# MAGIC Select * from ViewDate;
