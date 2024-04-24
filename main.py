from typing import List
import iterfzf
import pickle
import polars as pl
import threading
from xgboost import XGBClassifier
import gdown
import os

# Asynchronously load the data
df = None


def load_data():
    global df
    df = pl.read_parquet('parquets/recipes-joined.parquet')


def get_keywords():
    """
    Gets the keywords from the keywords.txt file
    """
    with open('keywords/keywords.txt', 'r') as f:
        return f.read().splitlines()


def vectorize(unique_elems: List[str], input_elems: List[str]) -> List[int]:
    """Creates a vector of 1s and 0s, where a 1 indicates that the element at that index
    is in the input_elems list"""
    vector = [0] * len(unique_elems)
    for unique_elem in unique_elems:
        if unique_elem in input_elems:
            vector[unique_elems.index(unique_elem)] = 1
    return vector


def unique_elems(element_lists: List[List[str]]) -> List[str]:
    """Creates a list of all of the unique strings in the input lists
    This potentially be accomplished in a better way using sets, but sets 
    do not guarantee a specific order, which is necessary to keep the feature
    order consistent."""
    unique = []
    # Uses a set to (theoretically) trade some extra memory usage to make `in` run in constant time
    unique_set = set()
    for element_list in element_lists:
        for element in element_list:
            if element not in unique_set:
                unique_set.add(element)
                unique.append(element)
    return unique


def main():
    # If the parquets directory does not exist, create it
    if not os.path.exists('parquets'):
        os.makedirs('parquets')
    # Download the parquet file if it does not exist
    if not os.path.exists('parquets/recipes-joined.parquet'):
        print('Downloading data...')
        gdown.download(
            'https://drive.google.com/uc?id=1Or9udvyR64KZh3Un-wLCSNSnDn9D4lAh', 'parquets/recipes-joined.parquet', quiet=False)
        print('Data downloaded.')
    global df
    thread = threading.Thread(target=load_data)
    thread.start()

    # Load the best model (pkls/best_model.pkl)
    model: XGBClassifier = pickle.load(open('pkls/best_model.pkl', 'rb'))

    # Get the keywords
    keywords = get_keywords()

    chosen_keywords = iterfzf.iterfzf(
        keywords, multi=True, prompt="Choose keywords: ")
    # Ensure the user picks between 2 and 5 keywords
    while len(chosen_keywords) < 2 or len(chosen_keywords) > 5:
        print('Please choose between 2 and 5 keywords. Press enter to continue.')
        input()
        chosen_keywords = iterfzf.iterfzf(
            keywords, multi=True, prompt="Choose keywords: ")

    # Wait for the data to be loaded
    if df is None:
        print('Loading data...')
        thread.join()
    print('Data loaded.')

    old_keywords = unique_elems(df['Keywords'].to_list())

    # Filter the rows for ones whose keyword list contains all the chosen keywords
    def filter_keywords(row_keywords):
        return set(chosen_keywords).issubset(row_keywords)

    print('Filtering data...')
    df = df.filter(df['Keywords'].map_elements(filter_keywords, bool))
    print('There are', len(df), 'recipes that contain all of the chosen keywords.')
    if len(df) == 0:
        print('No recipes found. Please try using different, or fewer, keywords. Exiting.')
        return

    # Vectorize the chosen keywords
    chosen_keywords_vector = vectorize(old_keywords, chosen_keywords)

    # Predict the healthiness of the recipe
    prediction = model.predict([chosen_keywords_vector])
    print(f'The keywords, {chosen_keywords}, are most likely going to result in a',
          'healthy' if prediction[0] == 1 else 'unhealthy', 'recipe.')

    # Find the top 5 lowest NutrientScore recipes
    top_5 = df.sort('NutrientScore').head(5)
    # Drop all List columns
    for column in top_5.columns:
        if isinstance(top_5[column].dtype, pl.List):
            top_5 = top_5.drop(column)
    top_5.write_csv('top_5.csv')

    # Create a new column called "FormattedName"
    def format_name(name):
        # This removes all non-alphanumeric characters, replaces spaces with hyphens, and makes the string lowercase
        return ''.join(e for e in name if e.isalnum() or e == ' ').lower().replace(' ', '-')
    top_5 = top_5.with_columns(pl.col('Name').map_elements(
        format_name, str).alias('FormattedName'))
    print('Here are links to the top 5 healthiest recipes:')
    # links have the following format: https://www.food.com/recipe/<recipe-name>-<recipe-id>
    for row in top_5.iter_rows(named=True):
        print(
            f'https://www.food.com/recipe/{row["FormattedName"]}-{int(row["RecipeId"])}')


main()
