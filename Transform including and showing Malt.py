# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 14:13:43 2022

@author: HUAYX179
"""

"""
Created on Thu Jul  7 20:38:12 2022

@author: HUAYX179
"""

# -*- coding: utf-8 -*-
"""
Created on Sun May 15 08:52:27 2022

@author: HUAYX179
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import pandas as pd
import numpy as np
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error

#Import the original data dump to Python and transform the data set to a pivotable data frame
df=pd.read_excel('RTD Data Dump - KDP 2017 to April 2022.xlsx',header=[2,3])
df = df.iloc[: , 2:]
df=df.set_index([('Unnamed: 2_level_0',   'Entity'), ('Unnamed: 3_level_0',   'Category'),
                 ('Unnamed: 4_level_0',   'Province'), ('Unnamed: 5_level_0',   'Agent'),
                 ('Unnamed: 6_level_0',   'Supplier'), ('Unnamed: 7_level_0',   'Brand Family'),
                 ('Unnamed: 8_level_0',   'Brand'), ('Unnamed: 9_level_0',   'SKU Detail'),
                 ('Unnamed: 10_level_0',   'Description'), ('Unnamed: 11_level_0',   'Vol/Unit'),
                 ('Unnamed: 12_level_0',   'Sub Category'), ('Reporting Date',   'MDM Segment')])

df=df.stack([0,1]).reset_index(name='value')
df.columns = ['Entity', 'Category', 'Province', 'Agent','Supplier',
              'Brand Family', 'Brand', 'SKU Detail', 'Description','Vol/Unit',
              'Sub Category', 'MDM Segment', 'Date Range','Measurement','Value']
df=df.dropna(subset=['Entity'])

#Seperate Quebec Malt products from the rest of RTD volume
df["Concat"] = df["Province"] + df["Description"]

df1=df[['Province', 'Description']]
df1=df1.drop_duplicates()
df1=df1.loc[df['Province'] == 'PQ']
df1=df1[df["Description"].str.contains("MALT")]
df1["Concat"] = df1["Province"] + df1["Description"]
df1=df1[['Concat']]
df = pd.merge(df, df1, on=["Concat", "Concat"], how="outer", indicator=True)

df['merge3'] = (df['_merge']).astype(object)


df = df.groupby([df['merge3'].fillna('(blank)'),df['Brand Family'].fillna('(blank)'),df['MDM Segment'].fillna('(blank)'),df['SKU Detail'].fillna('(blank)'),df['Date Range'].fillna('(blank)'),df['Measurement'].fillna('(blank)')])['Value'].sum().reset_index()


#Tranform the time to our calendar
df_Range=pd.read_excel('Date.xlsx')
df4=df_Range.groupby(['Date Range'])["Date Range"].count().reset_index(name="Days count")
df5=pd.merge(df4,df_Range, on='Date Range', how='inner')
df3=pd.merge(df5,df, on='Date Range', how='outer')
df3["Value(Daily)"] = df3["Value"]/df3["Days count"]
df6 = df3.groupby(['merge3','Year','Month','Brand Family','MDM Segment','SKU Detail','Measurement'])['Value(Daily)'].sum().reset_index()

df6=df6[(df6['Year']>2018)]
df6=df6[(df6['Measurement']!='R1 (9L Cases)')]
print(df6)

#Generate CSV file
df6.to_csv('RTD for CX 2024-2-19.csv')

