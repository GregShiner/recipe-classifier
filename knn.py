import pandas as pd
# If the file is not already un-gzipped, unzip it
import gzip
import os
if not os.path.exists('recipes-vectorized.parquet'):
    with open('recipes-vectorized.parquet', 'wb') as f:
        with gzip.open('recipes-vectorized.parquet.gz', 'rb') as f_gz:
            f.write(f_gz.read())
df_vectorized = pd.read_parquet('recipes-vectorized.parquet') # Read the vectorized DataFrame from the parquet file

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV
grid_search_knn = GridSearchCV(KNeighborsClassifier(), {'hidden_layer_sizes': [(100,), (100, 100), (100, 100, 100)], 'alpha': [0.0001, 0.001, 0.01]}, verbose=3, n_jobs=-1, cv=3)
# Sample 10%
df_sample = df_vectorized.sample(frac=0.1)
X = df_sample['KeywordsVector'].to_list()
y = df_sample['Healthy']
grid_search_knn.fit(X, y)
import pickle
with open('classifier_knn.pkl', 'wb') as f:
    pickle.dump(grid_search_knn, f)
# import pandas as pd
# from sklearn.neighbors import KNeighborsClassifier
# from sklearn.model_selection import GridSearchCV
# import pickle

# X_pca_90 = pd.read_parquet('parquets/recipes-pca-90')
# X_pca_95 = pd.read_parquet('parquets/recipes-pca-95')
# X_pca_99 = pd.read_parquet('parquets/recipes-pca-99')

# df_vectorized = pd.read_parquet('recipes-vectorized.parquet') # Read the vectorized DataFrame from the parquet file
# y = df_vectorized['Healthy']

# grid_search_knn = GridSearchCV(KNeighborsClassifier(), {'n_estimators': [100, 200, 300], 'max_depth': [3, 5, 7]}, verbose=3, n_jobs=-1, cv=3)

# print('Fitting knn with pca 90')
# grid_search_knn.fit(X_pca_90, y)
# with open('classifier_knn_pca_90.pkl', 'wb') as f:
#     pickle.dump(grid_search_knn, f)

# print('Fitting knn with pca 95')
# grid_search_knn.fit(X_pca_95, y)
# with open('classifier_knn_pca_95.pkl', 'wb') as f:
#     pickle.dump(grid_search_knn, f)
    
# print('Fitting knn with pca 99')
# grid_search_knn.fit(X_pca_99, y)
# with open('classifier_knn_pca_99.pkl', 'wb') as f:
#     pickle.dump(grid_search_knn, f)