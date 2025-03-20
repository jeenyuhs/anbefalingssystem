import pandas as pd


from sklearn.cluster import KMeans
from sqlmodel import SQLModel

from starlette.responses import JSONResponse

from fastapi import FastAPI
from api import v1 as api

import state
import model

def startup() -> None:
    SQLModel.metadata.create_all(state.engine)

    # TODO: load data from database and train the model

app = FastAPI(
    on_lifespan=[startup()],
)

app.include_router(api.router, prefix="/api")


# def main() -> None:
#     t.set_page_config(
#         page_title="Film anbefalingssystem",
#         layout="wide",
#     )
#     # load the dataset from .csv file
#     movies_df = pd.read_csv("data/top_rated_movies_10000.csv")
#
#     # load the model
#     kmeans, features = model.fit(movies_df)    # mutates movies_df in function
#
#     search_input = st.text_input("Vælg en film, du kan lide.")
#
#     if not search_input:
#         return
#
#     recommendations, cluster_plot, inertia = st.tabs(["Anbefalinger", "Cluster plot", "Inertia analyse"])
#
#     if not movies_df.isin([search_input]).any().any():
#         st.write(f"There is no movie named `{search_input}`")
#         return
#
#     recommended_movies = model.get_movies_based_on_title(movies_df, search_input, features)
#     recommendations.dataframe(recommended_movies.head(20), use_container_width=True)
#
#     cluster_plot.write(
#         "Man kunne eventuelt lave et cluster plot, "
#         "hvor man kan se hvor den udvalgte film er "
#         "i den cluster den tilhører og dermed få "
#         "et bedre indblik på hvilke film er "
#         "tættest på, den man valgte."
#     )
#
#     inertia.write(
#         "For at kunne finde ud af den mængde clusters man skal anvende, "
#         "for at modellen bliver så bedst som overhovedet muligt, kan man "
#         "lave en inertia analyse."
#     )
#
#     _n_clusters = range(1, 40)
#     inertias = []
#     with st.spinner("Analysere inertia værdien...", show_time=True):
#         for k in _n_clusters:
#             model_ = KMeans(n_clusters=k)
#             model_.fit(features)
#
#             inertias.append(model_.inertia_)
#
#     inertia.line_chart(inertias)
#     inertia.write(
#         "Når inertia værdien pludselig falder, betyder det, at vi er på "
#         "vej til at nå en mængde clusters, som passer godt til vores datasæt. "
#         "I vores tilfælde kan vi se når vi gør brug af ca. 15-20 clusters, "
#         "så begynder faldet at ligne ud."
#     )
