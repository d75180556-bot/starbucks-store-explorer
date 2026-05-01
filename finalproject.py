"""
Name:       Daniyal Hashwani
CS230:      Section XXX
Data:       Starbucks Directory
URL:        Not posted yet

Description:
This Streamlit app explores Starbucks store locations around the world.
Users can filter by country and ownership type, view store counts, compare
top cities, and see store locations on an interactive map.

References:
CS230 class examples and Streamlit documentation.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk


DATA_FILE = "directory.csv"

# [FUNCCALL2]
def load_data(file_name):
    df = pd.read_csv(file_name)
    return df


# [FUNC2P]
def filter_data(df, country="US", ownership_types=None):
    filtered = df[df["Country"] == country]

    if ownership_types is not None:
        filtered = filtered[filtered["Ownership Type"].isin(ownership_types)]

    return filtered


# [FUNCRETURN2]
def get_max_min_city(df):
    city_counts = df["City"].value_counts()
    max_city = city_counts.idxmax()
    min_city = city_counts.idxmin()
    return max_city, min_city


def main():
    st.title("Starbucks Store Explorer")
    st.write("Explore Starbucks locations by country, ownership type, city, and map location.")

    df = load_data(DATA_FILE)

    # [COLUMNS]
    df["Location"] = df["City"] + ", " + df["Country"]

    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

    st.sidebar.header("Filters")  # [ST3]

    # [ST1]
    country = st.sidebar.selectbox("Choose a country:", sorted(df["Country"].dropna().unique()))

    ownership_options = sorted(df["Ownership Type"].dropna().unique())

    # [ST1]
    selected_ownership = st.sidebar.multiselect(
        "Choose ownership type:",
        ownership_options,
        default=ownership_options
    )

    # [ST2]
    top_n = st.sidebar.slider("Number of top cities to show:", 5, 20, 10)

    # [FILTER1]
    country_df = df[df["Country"] == country]

    # [FILTER2]
    filtered_df = filter_data(df, country, selected_ownership)

    st.subheader("Filtered Data")
    st.write(filtered_df)

    st.write("Total stores after filtering:", len(filtered_df))

    if len(filtered_df) > 0:
        # [MAXMIN]
        max_city, min_city = get_max_min_city(filtered_df)
        st.write("City with most Starbucks stores:", max_city)
        st.write("City with fewest Starbucks stores:", min_city)

        # [SORT]
        city_counts = filtered_df["City"].value_counts().reset_index()
        city_counts.columns = ["City", "Store Count"]
        city_counts = city_counts.sort_values("Store Count", ascending=False)

        st.subheader("Top Cities by Starbucks Store Count")

        # [CHART1]
        top_cities = city_counts.head(top_n)

        fig, ax = plt.subplots()
        ax.bar(top_cities["City"], top_cities["Store Count"])
        ax.set_title("Top Cities by Starbucks Stores")
        ax.set_xlabel("City")
        ax.set_ylabel("Number of Stores")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        st.subheader("Ownership Type Breakdown")

        # [CHART2]
        ownership_counts = filtered_df["Ownership Type"].value_counts()

        fig2, ax2 = plt.subplots()
        ax2.pie(ownership_counts, labels=ownership_counts.index, autopct="%1.1f%%")
        ax2.set_title("Ownership Type Share")
        st.pyplot(fig2)

        # [ITERLOOP]
        total_rows_checked = 0
        for city in filtered_df["City"]:
            total_rows_checked = total_rows_checked + 1

        st.write("Rows checked:", total_rows_checked)

        # [DICTMETHOD]
        summary = {
            "country": country,
            "stores": len(filtered_df),
            "top_city": max_city
        }

        st.write("Summary dictionary keys:", summary.keys())
        st.write("Summary dictionary values:", summary.values())

        st.subheader("Map of Starbucks Locations")

        map_df = filtered_df.dropna(subset=["Latitude", "Longitude"])

        if len(map_df) > 0:
            # [MAP]
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=map_df,
                get_position=["Longitude", "Latitude"],
                get_radius=300,
                get_fill_color=[0, 150, 0, 160],
                pickable=True
            )

            view_state = pdk.ViewState(
                latitude=map_df["Latitude"].mean(),
                longitude=map_df["Longitude"].mean(),
                zoom=4,
                pitch=0
            )

            tooltip = {
                "html": "<b>Store:</b> {Store Name}<br><b>City:</b> {City}<br><b>Country:</b> {Country}",
                "style": {"backgroundColor": "green", "color": "white"}
            }

            st.pydeck_chart(
                pdk.Deck(
                    initial_view_state=view_state,
                    layers=[layer],
                    tooltip=tooltip
                )
            )
        else:
            st.write("No map data available for this filter.")

    else:
        st.write("No stores match your filters.")


main()