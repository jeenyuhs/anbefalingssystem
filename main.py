import pandas as pd

import streamlit as st
import model

def main() -> None:
    st.set_page_config(
        page_title="Film anbefalingssystem",
        layout="wide",
    )
    # load the dataset from .csv file
    movies_df = pd.read_csv("data/top_rated_movies_10000.csv")
    
    # load the model
    kmeans, features = model.fit(movies_df)    # mutates movies_df in function
    

    search_input = st.text_input("Vælg en film, du kan lide.")

    if not search_input:
        return
    
    recommendations, cluster_plot = st.tabs(["Anbefalinger", "Cluster plot"])

    if not movies_df.isin([search_input]).any().any():
        st.write(f"There is no movie named `{search_input}`")
        return
    
    recommended_movies = model.get_movies_based_on_title(movies_df, search_input, features)
    recommendations.dataframe(recommended_movies.head(20), use_container_width=True)

    cluster_plot.write(
        "Man kunne eventuelt lave et cluster plot, "
        "hvor man kan se hvor den udvalgte film er "
        "i den cluster den tilhører og dermed få "
        "et bedre indblik på hvilke film er "
        "tættest på, den man valgte."
    )

if __name__ == "__main__":
    main()