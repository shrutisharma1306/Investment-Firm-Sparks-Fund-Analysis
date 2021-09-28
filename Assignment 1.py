import numpy as np
import pandas as pd
#import matplotlib as plt
import seaborn as sns
import matplotlib.pyplot as plt
desired_width=320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns',20)

#Reading companies and rounds2 dataset
r1=pd.read_csv("rounds2.csv")
c1=pd.read_csv("companies.csv")


#renaming column in rounds2 dataframe before merging
r1=r1.rename(columns={'company_permalink':'permalink'})
r1['permalink']= r1['permalink'].str.upper()
r1['permalink'] = r1['permalink'].str.strip()
c1['permalink']= c1['permalink'].str.upper()
c1['permalink'] = c1['permalink'].str.strip()
c1['category_list'] = c1['category_list'].str.strip()
c1['category_list'] = c1['category_list'].str.upper()

#Counting unique values in companies and rounds2 dataframe
print(len(pd.unique(r1['permalink'])))
print(len(pd.unique(c1['permalink'])))

#print(c1.head(2))

#Are there any companies in the rounds2 file which are not present in companies ? Answer Y/N.
a=len(r1[~r1.isin(c1)])
print(a)

#Merge two dataframes
master_frame=pd.merge(r1,c1,how='outer',on='permalink')
print(master_frame.shape)

#print(round(100*(master_frame.isnull().sum()/len(master_frame.index)),2))

#Dropping unnecessary columns
master_frame=master_frame.drop("funding_round_code",axis=1)
print(master_frame.isnull().sum())
master_frame=master_frame.drop("homepage_url",axis=1)
master_frame=master_frame.drop("funding_round_permalink",axis=1)
master_frame=master_frame.drop("funded_at",axis=1)
master_frame=master_frame.drop("state_code",axis=1)
master_frame=master_frame.drop("region",axis=1)
master_frame=master_frame.drop("city",axis=1)
master_frame=master_frame.drop("founded_at",axis=1)

#Data cleaning for columns
master_frame = master_frame[master_frame['country_code'].notna()]
master_frame = master_frame[master_frame['category_list'].notna()]
master_frame = master_frame[master_frame['funding_round_type'].notna()]
master_frame = master_frame[master_frame['raised_amount_usd'].notna()]

#print(master_frame.describe())
print(round(100*(master_frame.isnull().sum()/len(master_frame.index)),2))
#print(master_frame)

#fraction of rows lost
#d=len(master_frame.index)/114983
#print(d)
master_frame['country_code'] = master_frame['country_code'].str.strip()

#Country Analysis
## Grouping by country code for only 'venture' funding type
df2=master_frame[master_frame['funding_round_type'] == 'venture'].groupby('country_code')['raised_amount_usd'].sum()
print(df2)
#df2.to_csv('QC.csv', index=True)

#SECTOR ANALYSIS 1: Adding 'primary sector column' to master_frame
master_frame['primary_sector'] = master_frame['category_list'].str.split('|').str[0]
print(master_frame)

#FUNDING TYPE selection (Table 2.1)
#b=master_frame.pivot_table(values='raised_amount_usd',index='funding_round_type',aggfunc='sum')
#print(b)
top9 = master_frame[master_frame['country_code'].isin(['USA', 'CHN', 'GBR', 'IND', 'CAN', 'FRA', 'ISR', 'DEU', 'JPN' ])]
top9.groupby('country_code')['raised_amount_usd'].sum().sort_values(ascending=False)
print(top9)

#Sector Analysis 2: Adding main sectors from mapping file
m1=pd.read_csv("mapping_1.csv")
m1['category_list'] = m1['category_list'].str.strip()
m1['category_list'] = m1['category_list'].str.upper()
m1 = m1.rename(columns = {'category_list': 'primary_sector'}, inplace = False)
left = pd.merge(master_frame,
                     m1,
                     on ='primary_sector',
                     how ='left')
master_frame=left
print(master_frame)

# Let's now create a new data frame with only these 3 countries data for furthur sector wise analysis\n
top3_english = top9[top9['country_code'].isin(['USA', 'GBR', 'IND'])]
top3_english.groupby('country_code')['raised_amount_usd'].sum().sort_values(ascending=False)
left = pd.merge(top3_english,
                     m1,
                     on ='primary_sector',
                     how ='left')
top3_english=left
print(top3_english)
#print(top3_english)

top3_english = top3_english.drop(top3_english[(top3_english.raised_amount_usd < 5000000)].index)
top3_english = top3_english.drop(top3_english[(top3_english.raised_amount_usd > 15000000)].index)
print(top3_english)

#Create dataframe D1,D2,D3
D1 = top3_english[top3_english['country_code'] == 'USA']
D2 = top3_english[top3_english['country_code'] == 'GBR']
D3 = top3_english[top3_english['country_code'] == 'IND']

#print(D1)
#print(D2)
#print(D3)

USA_data1=D1.pivot_table(values = 'raised_amount_usd',index = ['main_sector'], aggfunc = {'sum','count'})
USA_data2=D1.groupby('main_sector')['raised_amount_usd'].count().sort_values(ascending=False)
USA_data3=D1[D1['main_sector'] == "Others"].groupby('permalink')['raised_amount_usd'].sum().sort_values(ascending=False).head(5)
print(USA_data1)
print(USA_data2)
print(USA_data3)

GBR_data1=D2.pivot_table(values = 'raised_amount_usd',index = ['main_sector'], aggfunc = {'sum','count'})
GBR_data2=D2.groupby('main_sector')['raised_amount_usd'].count().sort_values(ascending=False)
GBR_data3=D2[D2['main_sector'] == "Others"].groupby('permalink')['raised_amount_usd'].sum().sort_values(ascending=False).head(5)
print(GBR_data1)
print(GBR_data2)
print(GBR_data3)

IND_data1=D3.pivot_table(values = 'raised_amount_usd',index = ['main_sector'], aggfunc = {'sum','count'})
IND_data2=D3.groupby('main_sector')['raised_amount_usd'].count().sort_values(ascending=False)
IND_data3=D3[D3['main_sector'] == "Others"].groupby('permalink')['raised_amount_usd'].sum().sort_values(ascending=False).head(5)
print(IND_data1)
print(IND_data2)
print(IND_data3)

plt.figure(figsize=(20, 10))
plt.subplot(1, 2, 1)
sns.countplot(y="main_sector", data=D1)
plt.title("Count")
plt.subplot(1, 2, 2)
sns.barplot(y="main_sector", x="raised_amount_usd", data=D1, estimator=sum)
plt.title("Sum")
plt.show()

plt.figure(figsize=(20, 10))
plt.subplot(1, 2, 1)
sns.countplot(y="main_sector", data=D2)
plt.title("Count")
plt.subplot(1, 2, 2)
sns.barplot(y="main_sector", x="raised_amount_usd", data=D2, estimator=sum)
plt.title("Sum")
plt.show()


plt.figure(figsize=(20, 10))
plt.subplot(1, 2, 1)
sns.countplot(y="main_sector", data=D3)
plt.title("Count")
plt.subplot(1, 2, 2)
sns.barplot(y="main_sector", x="raised_amount_usd", data=D3, estimator=sum)
plt.title("Sum")
plt.show()

frames = [D1, D2, D3]
result = pd.concat(frames)
plt.figure(figsize=(20, 10))
sns.barplot(y='country_code', x='raised_amount_usd', hue="main_sector", data=result, estimator=np.sum)
plt.show()

