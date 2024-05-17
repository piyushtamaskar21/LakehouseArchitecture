# Fabric notebook source

# METADATA ********************

# META {
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "c30b6e57-1cc1-4f4e-92b3-20fab14b5de5",
# META       "default_lakehouse_name": "Gold_Layer",
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
from notebookutils import mssparkutils

# CELL ********************

mssparkutils.fs.mount("abfss://LakehouseArchitecture@onelake.dfs.fabric.microsoft.com/Bronze_Layer.Lakehouse/Files","/Files")

# CELL ********************

mssparkutils.fs.getMountPath("/Files")

# CELL ********************

check_files = mssparkutils.fs.ls(f"file://{mssparkutils.fs.getMountPath('/Files')}/Current/")

# CELL ********************

for file in check_files:
    if file.path:
        mssparkutils.fs.mv(file.path,f"file://{mssparkutils.fs.getMountPath('/Files')}/Archive/")
