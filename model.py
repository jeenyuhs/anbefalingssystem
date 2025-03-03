import ast
from typing import Any
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack
from sklearn.preprocessing import MultiLabelBinarizer

def fit(df: pd.DataFrame) -> tuple[KMeans, Any]:
    # vectorize the description of the movies
    tfidf = TfidfVectorizer()
    overview_matrix = tfidf.fit_transform(df["overview"])

    # pandas list are weird where they are list[str] instead 
    # of the list[list[int]], they are supposed to be - this is the fix
    fixed_genre_ids = [ast.literal_eval(genre_list) for genre_list in df["genre"]]
    
    # transform the genre ids to binary values
    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(fixed_genre_ids)

    # combine all features and convert to csr_array
    combined_features = hstack((overview_matrix, genre_matrix)).tocsr()
    
    # initalize the kmeans cluster
    kmeans = KMeans(n_clusters=20, random_state=42)
    df["cluster"] = kmeans.fit_predict(combined_features)
    
    return (kmeans, combined_features)

def get_movies_based_on_title(df: pd.DataFrame, title: str, features: Any) -> pd.DataFrame:
    # get the cluster id from the selected movie
    cluster_id = df[df["title"] == title]["cluster"].values[0]
    input_movie_index = df[df["title"] == title].index[0]
    input_movie_vector = features[input_movie_index].toarray()

    # filter movies that belong to the same cluster as the selected movie    
    recommended_movies = df[df["cluster"] == cluster_id]
    # remove the selected movie from the recommended movies (obviously)
    recommended_movies = recommended_movies[recommended_movies["title"] != title]
    recommended_vectors = features[recommended_movies.index].toarray()

    # get the similarity score between movies, so we can sort them
    # by their similarity to the selected movie to get the best
    # recommendations
    similarities = cosine_similarity(input_movie_vector, recommended_vectors).flatten()
    recommended_movies["similarity"] = similarities

    # slightly change the sorting method to include rating in the final sorting
    recommended_movies["sort_method"] = similarities * 1.4 + (recommended_movies["rating"] * 0.02)
    
    recommended_movies.sort_values(by="sort_method", ascending=False, inplace=True)
    
    return recommended_movies[["title", "overview", "rating", "similarity"]]