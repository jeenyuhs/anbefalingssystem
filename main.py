import ast
import asyncio
from typing import Any

from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer

def recommend_movies(
    movie_title: str, 
    movies_df: pd.DataFrame, 
    combined_features: Any  # csr_array
) -> pd.DataFrame:
    # get the cluster id from the selected movie
    cluster_id = movies_df[movies_df["title"] == movie_title]["cluster"].values[0]
    input_movie_index = movies_df[movies_df["title"] == movie_title].index[0]
    input_movie_vector = combined_features[input_movie_index].toarray()

    # filter movies that belong to the same cluster as the selected movie    
    recommended_movies = movies_df[movies_df["cluster"] == cluster_id]
    # remove the selected movie from the recommended movies (obviously)
    recommended_movies = recommended_movies[recommended_movies["title"] != movie_title]
    recommended_vectors = combined_features[recommended_movies.index].toarray()

    # get the similarity score between movies, so we can sort them
    # by their similarity to the selected movie to get the best
    # recommendations
    similarities = cosine_similarity(input_movie_vector, recommended_vectors).flatten()
    recommended_movies["similarity"] = similarities
    sorted_recommendations = recommended_movies.sort_values(by="similarity", ascending=False)
    
    return sorted_recommendations[["title", "overview", "similarity"]]

def main() -> None:
    # read the movies gotten from the excel file.
    movies_df = pd.read_csv("data/top_rated_movies_10000.csv")

    # vectorize the description of the movies
    tfidf = TfidfVectorizer()
    overview_matrix = tfidf.fit_transform(movies_df["overview"])

    # pandas list are weird where they are list[str] instead 
    # of the list[list[int]], they are supposed to be - this is the fix
    fixed_genre_ids = [ast.literal_eval(genre_list) for genre_list in movies_df["genre"]]
    
    # transform the genre ids to binary values
    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(fixed_genre_ids)

    # combine all features and convert to csr_array
    combined_features = hstack((overview_matrix, genre_matrix)).tocsr()
    
    # initalize the kmeans cluster
    kmeans = KMeans(n_clusters=10, random_state=42)
    movies_df["cluster"] = kmeans.fit_predict(combined_features)

    # examples ...
    recommedation = recommend_movies("28 Days Later", movies_df, combined_features)
    print("Recommended movies based on - 28 Days Later")
    print(recommedation[:20])

    recommedation = recommend_movies("Creep", movies_df, combined_features)
    print("Recommended movies based on - Creep")
    print(recommedation[:20])

    # TODO: implement streamlit to visualize stuff

if __name__ == "__main__":
    main()