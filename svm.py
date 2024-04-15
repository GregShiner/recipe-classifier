import pandas as pd
# If the file is not already un-gzipped, unzip it
import gzip
import os
if not os.path.exists('recipes-vectorized.parquet'):
    with open('recipes-vectorized.parquet', 'wb') as f:
        with gzip.open('recipes-vectorized.parquet.gz', 'rb') as f_gz:
            f.write(f_gz.read())
df_vectorized = pd.read_parquet('recipes-vectorized.parquet') # Read the vectorized DataFrame from the parquet file

from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
grid_search_svm = GridSearchCV(SVC(), {'C': [0.1, 1, 10, 100], 'kernel': ['linear', 'poly', 'rbf', 'sigmoid']}, verbose=3, n_jobs=-1, cv=3)
# Sample 10%
df_sample = df_vectorized.sample(frac=0.1)
X = df_sample['KeywordsVector'].to_list()
y = df_sample['Healthy']
grid_search_svm.fit(X, y)
import pickle
with open('classifier_svm.pkl', 'wb') as f:
    pickle.dump(grid_search_svm, f)