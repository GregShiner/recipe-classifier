import pickle
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
import pandas as pd
# If the file is not already un-gzipped, unzip it
import gzip
import os
if not os.path.exists('recipes-vectorized.parquet'):
    with open('recipes-vectorized.parquet', 'wb') as f:
        with gzip.open('recipes-vectorized.parquet.gz', 'rb') as f_gz:
            f.write(f_gz.read())
# Read the vectorized DataFrame from the parquet file
df_vectorized = pd.read_parquet('recipes-vectorized.parquet')

grid_search_svm = GridSearchCV(SVC(), {'C': [0.1, 1, 10, 100], 'kernel': [
                               'linear', 'poly', 'rbf', 'sigmoid']}, verbose=3, n_jobs=-1, cv=3)
# Sample 10%
df_sample = df_vectorized.sample(frac=0.1)
X = df_sample['KeywordsVector'].to_list()
y = df_sample['Healthy']
grid_search_svm.fit(X, y)
with open('classifier_svm.pkl', 'wb') as f:
    pickle.dump(grid_search_svm, f)

X_pca_90 = pd.read_parquet('parquets/recipes-pca-90.parquet')
X_pca_95 = pd.read_parquet('parquets/recipes-pca-95.parquet')
X_pca_99 = pd.read_parquet('parquets/recipes-pca-99.parquet')

y = df_vectorized['Healthy']

# Combine the X's and y's into dfs and sample them at 20%
X_pca_90['Healthy'] = y
X_pca_95['Healthy'] = y
X_pca_99['Healthy'] = y

X_pca_90_sample = X_pca_90.sample(frac=0.2)
X_pca_95_sample = X_pca_95.sample(frac=0.2)
X_pca_99_sample = X_pca_99.sample(frac=0.2)

y = X_pca_90_sample['Healthy']
X_pca_90_sample = X_pca_90_sample.drop(columns='Healthy')
X_pca_95_sample = X_pca_95_sample.drop(columns='Healthy')
X_pca_99_sample = X_pca_99_sample.drop(columns='Healthy')

grid_search_svm = GridSearchCV(SVC(), {'C': [0.1, 1, 10, 100], 'kernel': [
                               'linear', 'poly', 'rbf', 'sigmoid']}, verbose=3, n_jobs=-1, cv=3)

print('Fitting svm with pca 90')
grid_search_svm.fit(X_pca_90_sample, y)
with open('classifier_svm_pca_90.pkl', 'wb') as f:
    pickle.dump(grid_search_svm, f)

print('Fitting svm with pca 95')
grid_search_svm.fit(X_pca_95_sample, y)
with open('classifier_svm_pca_95.pkl', 'wb') as f:
    pickle.dump(grid_search_svm, f)

print('Fitting svm with pca 99')
grid_search_svm.fit(X_pca_99_sample, y)
with open('classifier_svm_pca_99.pkl', 'wb') as f:
    pickle.dump(grid_search_svm, f)
