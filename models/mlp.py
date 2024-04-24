import pickle
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPClassifier
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

grid_search_mlp = GridSearchCV(MLPClassifier(), {
    'hidden_layer_sizes': [(100,), (100, 100), (100, 100, 100)],
    'alpha': [0.0001, 0.001, 0.01]},
    verbose=3, n_jobs=-1, cv=3)
# Sample 10%
df_sample = df_vectorized.sample(frac=0.5)
X = df_sample['KeywordsVector'].to_list()
y = df_sample['Healthy']
grid_search_mlp.fit(X, y)
with open('classifier_mlp.pkl', 'wb') as f:
    pickle.dump(grid_search_mlp, f)
