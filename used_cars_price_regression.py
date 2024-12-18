import pandas as pd
import numpy as np
# import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import xgboost as xgb
import warnings
import pickle as pkl
warnings.filterwarnings('ignore')

df_train = pd.read_csv('/content/train.csv')
df_test = pd.read_csv('/content/test.csv')
df_submission = pd.read_csv('/content/sample_submission.csv')

df_train.head()

df_train.isnull().sum()

duplicate_rows = df_train[df_train.duplicated()]

print(f"Duplicate Rows: {duplicate_rows}")

df_train = df_train.drop_duplicates()

nulls_fuel_type = df_train[df_train['fuel_type'].isnull()]
print(nulls_fuel_type[['engine', 'fuel_type']])

df_train['fuel_type'].fillna('Electricity', inplace=True)
df_test['fuel_type'].fillna('Electricity', inplace=True)

df_train['accident'].fillna('None reported', inplace=True)
df_test['accident'].fillna('None reported', inplace=True)

df_train['clean_title'].fillna('No', inplace=True)
df_test['clean_title'].fillna('No', inplace=True)

df_train.head()

cat_cols = [x for x in df_train.columns if df_train[x].dtype == 'object']
num_cols = [x for x in df_train.columns if df_train[x].dtype != 'object']
print('Categorical : ',cat_cols)
print('Numerical : ',num_cols)

unique_counts = {}
for col in cat_cols:
    unique_counts[col] = df_train[col].nunique()
    print(f" {col}  ------>   {unique_counts[col]}")

## model column will be dropped as it has many varities of models :
df_train  = df_train.drop('model', axis=1)
df_test  = df_test.drop('model', axis=1)

brand_price = df_train.groupby('brand')['price'].mean().sort_values(ascending=False)

plt.figure(figsize=(15, 6))
sns.barplot(x=brand_price.index, y=brand_price.values)
plt.xlabel('Brand')
plt.ylabel('Average Price')
plt.title('Average Price by Brand')
plt.xticks(rotation=90)
plt.show()

def brand_encoder(brand):
    brand_mapping = {
        3: ['Bugatti', 'Lamborghini', 'Rolls-Royce', 'Bentley', 'McLaren', 'Ferrari', 'Aston'],
        2: ['Rivian', 'Porsche', 'Lucid', 'Maserati', 'Tesla', 'Maybach', 'Genesis', 'Land', 'Alfa', 'RAM', 'Mercedes-Benz', 'Jaguar', 'Cadillac', 'BMW'],
    }

    # Iterate through the mapping and return the  value
    for rating, brands in brand_mapping.items():
        if brand in brands:
            return rating

    # Return 1 if the brand isn't found in the mapping
    return 1

df_train['brand_encoded'] = df_train['brand'].apply(brand_encoder)
df_test['brand_encoded'] = df_test['brand'].apply(brand_encoder)

print('encoded_train' ,df_train['brand_encoded'].unique())
print('encoded_test ' ,df_test ['brand_encoded'].unique())

## brand will be dropped after encoding it
df_train  = df_train.drop('brand', axis=1)
df_test  = df_test.drop('brand', axis=1)

df_train['fuel_type'].unique()

fuel_price = df_train.groupby('fuel_type')['price'].mean().sort_values(ascending=False)

plt.figure(figsize=(6, 3))
sns.barplot(x=fuel_price.index, y=fuel_price.values)
plt.xlabel('fuel_type')
plt.ylabel('Average Price')
plt.title('Average Price by fuel_type')
plt.xticks(rotation=45)
plt.show()

## we will encode feul_types as we encoded brands before :
def fuel_encoder(fuel_type):
    fuel_mapping = {
        3: ['Electricity', 'Hybrid','Diesel' ],
        2:  ['Plug-In Hybrid','Gasoline','–'],
    }

    # Iterate through the mapping and return the  value
    for rating, types in fuel_mapping.items():
        if fuel_type in types:
            return rating

    # Return 1 if the brand isn't found in the mapping
    return 1

df_train['fuel_type'] = df_train['fuel_type'].apply(fuel_encoder)
df_test['fuel_type'] = df_test['fuel_type'].apply(fuel_encoder)

print('encoded_train' ,df_train['fuel_type'].unique())
print('encoded_test ' ,df_test ['fuel_type'].unique())

df_train['engine']

# we will use regular expressions (regex) to extract some features from it as :-
# [Horsepower,Displacement,Engine Type,Cylinder Count,Fuel Type] :
import re

def extract_hp(engine):
    match = re.search(r'(\d+(\.\d+)?)HP', engine)
    return float(match.group(1)) if match else None

def extract_displacement(engine):
    match = re.search(r'(\d+\.\d+)L|(\d+\.\d+) Liter', engine)
    return float(match.group(1)) if match else None

def extract_engine_type(engine):
    match = re.search(r'(V\d+|I\d+|Flat \d+|Straight \d+)', engine)
    return match.group(1) if match else None

def extract_cylinder_count(engine):
    match = re.search(r'(\d+) Cylinder', engine)
    return int(match.group(1)) if match else None

def extract_fuel_type(engine):
    fuel_types = ['Gasoline', 'Diesel', 'Electric', 'Hybrid', 'Flex Fuel']
    for fuel in fuel_types:
        if fuel in engine:
            return fuel
    return None

def extract_displacement(engine):
    match = re.search(r'(\d+\.\d+)L|(\d+\.\d+) Liter', engine)
    if match:
        return float(match.group(1)) if match.group(1) else float(match.group(2))
    return None

# Apply extraction functions on train & test :
df_train['Horsepower'] = df_train['engine'].apply(extract_hp)
df_train['Displacement'] = df_train['engine'].apply(extract_displacement)
df_train['Engine Type'] = df_train['engine'].apply(extract_engine_type)
df_train['Cylinder Count'] = df_train['engine'].apply(extract_cylinder_count)
df_train['Fuel Type'] = df_train['engine'].apply(extract_fuel_type)


df_test['Horsepower'] = df_test['engine'].apply(extract_hp)
df_test['Displacement'] = df_test['engine'].apply(extract_displacement)
df_test['Engine Type'] = df_test['engine'].apply(extract_engine_type)
df_test['Cylinder Count'] = df_test['engine'].apply(extract_cylinder_count)
df_test['Fuel Type'] = df_test['engine'].apply(extract_fuel_type)

# handel null values in Horse Power and Cylinder count with mean :

df_train['Horsepower'].fillna(df_train['Horsepower'].mean(), inplace=True)
df_train['Cylinder Count'].fillna(df_train['Cylinder Count'].mean(), inplace=True)

df_test['Horsepower'].fillna(df_test['Horsepower'].mean(), inplace=True)
df_test['Cylinder Count'].fillna(df_test['Cylinder Count'].mean(), inplace=True)

df_train.head()

df_train.drop(['engine','Fuel Type'], axis=1, inplace=True)
df_test.drop(['engine','Fuel Type'], axis=1, inplace=True)

df_train['Engine Type'].isnull().sum()

df_train.drop(['Engine Type'], axis=1, inplace=True)
df_test.drop(['Engine Type'], axis=1, inplace=True)

## transmission feature :
df_train['transmission'].unique()

'''
transmission_map = {
    'manual': 'Manual',
    'm/t': 'Manual',
    'automatic': 'Automatic',
    'a/t': 'Automatic',
    'cvt': 'CVT'
}
'''
def clean_transmission(value):
    value = value.strip().lower()  # Convert to lowercase and strip whitespace
    if 'manual' in value or 'm/t' in value:
        return 'Manual'
    elif 'automatic' in value or 'a/t' in value or 'cvt' in value:
        return 'Automatic'
    elif 'cvt' in value:
        return 'CVT'
    else:
        return 'Other'

# Apply the cleaning function
df_train['transmission'] = df_train['transmission'].apply(clean_transmission)
df_test['transmission'] = df_test['transmission'].apply(clean_transmission)

df_train['transmission'].unique()

df_train.head(3)

# transmission will be encoded based on price :-
transmission_price = df_train.groupby('transmission')['price'].mean().sort_values(ascending=False)

plt.figure(figsize=(15, 6))
sns.barplot(x=transmission_price.index, y=transmission_price.values)
plt.xlabel('transmission')
plt.ylabel('Average Price')
plt.title('Average Price by transmission')
plt.xticks(rotation=90)
plt.show()

def transmission_encoder(transmission):
  if transmission in ['Other' ]:
    return 3
  elif transmission in ['Automatic']:
    return 2
  else:
    return 1

df_train['transmission'] = df_train['transmission'].apply(transmission_encoder)
df_test ['transmission'] = df_test ['transmission'].apply(transmission_encoder)

df_train.head(3)

df_train['ext_col'].nunique()

# ext_col_price = df_train.groupby('ext_col')['price'].mean().sort_values(ascending=False)

# plt.figure(figsize=(100,50))
# sns.barplot(x=ext_col_price.index, y=ext_col_price.values)
# plt.xlabel('ext_col')
# plt.ylabel('Average Price')
# plt.title('Average Price by ext_col')
# plt.xticks(rotation=90)
# plt.show()

# Calculate mean price per color and sort
ext_col_price = df_train.groupby('ext_col')['price'].mean().sort_values(ascending=False)

# color ranked based on its mean of price :
color_rank = {color: rank for rank, color in enumerate(ext_col_price.index, start=1)}

# Encode the colors
df_train['ext_col_encoded'] = df_train['ext_col'].map(color_rank)
df_test['ext_col_encoded'] = df_test['ext_col'].map(color_rank)

df_train.drop('ext_col', axis=1, inplace=True)
df_test.drop('ext_col', axis=1, inplace=True)

print(df_train['ext_col_encoded'].isna().sum())
print(df_test['ext_col_encoded'].isna().sum())

## we will make the same steps on int_col as we did on ext_col :
# int_col_price = df_train.groupby('int_col')['price'].mean().sort_values(ascending=False)

# plt.figure(figsize=(100,50))
# sns.barplot(x=int_col_price.index, y=int_col_price.values)
# plt.xlabel('int_col')
# plt.ylabel('Average Price')
# plt.title('Average Price by int_col')
# plt.xticks(rotation=90)
# plt.show()

# Arrange the colors from highest to lowest based on price , then encode it
int_col_price = df_train.groupby('int_col')['price'].mean().sort_values(ascending=False)

color_rank = {color: rank for rank, color in enumerate(int_col_price.index, 1)}

df_train['int_col_encoded'] = df_train['int_col'].map(color_rank)
df_test['int_col_encoded'] = df_test['int_col'].map(color_rank)

df_train.drop('int_col', axis=1, inplace=True)
df_test.drop('int_col', axis=1, inplace=True)

print(df_train['int_col_encoded'].isna().sum())
print(df_test['int_col_encoded'].isna().sum())

df_train.head(3)

## accident feature :
df_train['accident'].unique()

# Define a mapping for the accident types
accident_mapping = {
    'None reported': 0,
    'At least 1 accident or damage reported': 1
}

# Apply the encoding
df_train['accident_encoded'] = df_train['accident'].map(accident_mapping)
df_test['accident_encoded'] = df_test['accident'].map(accident_mapping)

print(df_train['accident'].isna().sum())
print(df_test ['accident'].isna().sum())

df_train.drop('accident', axis=1, inplace=True)
df_test.drop('accident', axis=1, inplace=True)

# clean_title feature :
df_train['clean_title'].unique()

def clean_title_encoder(clean_title):
  if clean_title in ['Yes']:
    return 1
  elif clean_title in ['No']:
    return 0

df_train['clean_title'] = df_train['clean_title'].apply(clean_title_encoder)
df_test['clean_title'] = df_test['clean_title'].apply(clean_title_encoder)

df_train.head(3)

#  replace model_year column with the age of the car as (model_age) :-

current_year = 2024

df_train['model_age'] = current_year - df_train['model_year']
df_test['model_age'] = current_year - df_test['model_year']

df_train.drop('model_year', axis=1, inplace=True)
df_test.drop('model_year', axis=1, inplace=True)

cat_cols = [x for x in df_train.columns if df_train[x].dtype == 'object']
num_cols = [x for x in df_train.columns if df_train[x].dtype != 'object']
print('Categorical : ',cat_cols)
print('Numerical : ',num_cols)

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import matplotlib.pyplot as plt
df_train[num_cols].hist(bins = 100, figsize = (20, 15))

corr_matrix = df_train[num_cols].corr()
import seaborn as sns
import matplotlib.pyplot as plt

# plt.subplots(figsize=(20, 15))
# sns.heatmap(corr_matrix,
#             xticklabels=corr_matrix.columns.values,
#             yticklabels=corr_matrix.columns.values,
#             linewidth=0.1,
#             annot=True,  # This will show the correlation values on the graph
#             fmt=".3f")
# plt.show()

# we droped (Displacement) as it was high_corr with (Cylinder Count)
df_train.drop('Displacement', axis=1, inplace=True)
df_test.drop('Displacement', axis=1, inplace=True)

# create csv files for new df_train and df_test
df_train.to_csv('df_train_processed2.csv', index=False)
df_test.to_csv('df_test_processed2.csv', index=False)

df_train.drop(['id'], axis=1, inplace=True)
df_test.drop(['id'], axis=1, inplace=True)

## Downloading the (df_train) file after preprocessing
# from google.colab import files
# files.download('df_train_processed2.csv')

x = df_train.drop(['price'], axis=1)
y = df_train['price']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

"""**LinearRegression**"""

model1 = LinearRegression()

model1.fit(X_train, y_train)
y_pred = model1.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
rmse = mse ** 0.5
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"R-squared: {r2:.6f}")
print(f"Mean Squared Error (MSE): {mse:.6f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.6f}")
print(f"Mean Absolute Error (MAE): {mae:.6f}")

y_pred = model1.predict(df_test)

df_submission['price'] = y_pred

df_submission.to_csv('submission2.csv', index=False)

"""**XGBRegressor**"""

# model2 = xgb.XGBRegressor()

# model2.fit(X_train, y_train)
# y_pred = model2.predict(X_test)

# mse = mean_squared_error(y_test, y_pred)
# rmse = mse ** 0.5
# mae = mean_absolute_error(y_test, y_pred)
# r2 = r2_score(y_test, y_pred)

# print(f"R-squared: {r2:.6f}")
# print(f"Mean Squared Error (MSE): {mse:.6f}")
# print(f"Root Mean Squared Error (RMSE): {rmse:.6f}")
# print(f"Mean Absolute Error (MAE): {mae:.6f}")
# filename= "Used Cars Price.sav "
# pkl.dump(model1,open(filename,'wb'))
