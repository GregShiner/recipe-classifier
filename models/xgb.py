import pandas as pd
# If the file is not already un-gzipped, unzip it
import gzip
import os
if not os.path.exists('recipes-vectorized.parquet'):
    with open('recipes-vectorized.parquet', 'wb') as f:
        with gzip.open('recipes-vectorized.parquet.gz', 'rb') as f_gz:
            f.write(f_gz.read())
df_vectorized = pd.read_parquet('recipes-vectorized.parquet') # Read the vectorized DataFrame from the parquet file

from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV
# grid_search_xgb = GridSearchCV(XGBClassifier(), {'n_estimators': [100, 200, 300], 'max_depth': [3, 5, 7]}, verbose=3, n_jobs=-1, cv=3)
# Sample 10%
# df_sample = df_vectorized.sample(frac=0.1)
# X = df_sample['KeywordsVector'].to_list()
# y = df_sample['Healthy']
# grid_search_xgb.fit(X, y)
import pickle
# with open('classifier_xgb.pkl', 'wb') as f:
#     pickle.dump(grid_search_xgb, f)

X_pca_90 = pd.read_parquet('parquets/recipes-pca-90.parquet')
X_pca_95 = pd.read_parquet('parquets/recipes-pca-95.parquet')
X_pca_99 = pd.read_parquet('parquets/recipes-pca-99.parquet')

y = df_vectorized['Healthy']

grid_search_xgb = GridSearchCV(XGBClassifier(), {'n_estimators': [100, 200, 300], 'max_depth': [3, 5, 7]}, verbose=3, n_jobs=-1, cv=3)

print('Fitting xgb with pca 90')
grid_search_xgb.fit(X_pca_90, y)
with open('classifier_xgb_pca_90.pkl', 'wb') as f:
    pickle.dump(grid_search_xgb, f)

print('Fitting xgb with pca 95')
grid_search_xgb.fit(X_pca_95, y)
with open('classifier_xgb_pca_95.pkl', 'wb') as f:
    pickle.dump(grid_search_xgb, f)
    
print('Fitting xgb with pca 99')
grid_search_xgb.fit(X_pca_99, y)
with open('classifier_xgb_pca_99.pkl', 'wb') as f:
    pickle.dump(grid_search_xgb, f)