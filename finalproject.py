"""
Name:       Daniyal Hashwani
CS230:      Section XXX
Data:       Starbucks Directory
URL:        Add your Streamlit link here

Description:
This program explores Starbucks store locations around the world.
Users can filter by country and ownership type, view charts, and explore
store locations on an interactive map.

References:
CS230 class examples.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

DATA_FILE = "directory.csv"

st.set_page_config(page_title="Starbucks Store Explorer", page_icon="☕", layout="wide")


# [FUNCCALL2]
def load_data(file_name):
    df = pd.read_csv(file_name)
    return df


# [FUNC2P]
def filter_data(df, country="US", ownership="Company Owned"):
    filtered = df[df["Country"] == country]
    filtered = filtered[filtered["Ownership Type"] == ownership]
    return filtered


# [FUNCRETURN2]
def city_info(df):
    city_counts = df["City"].value_counts()
    most_city = city_counts.idxmax()
    most_count = city_counts.max()
    return most_city, most_count


def main():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #F4F1EA;
        }

        .hero {
            background: linear-gradient(135deg, #E8E3D8 0%, #F9F7F2 100%);
            padding: 55px;
            border-radius: 28px;
            text-align: center;
            margin-bottom: 30px;
            border: 1px solid #DDD5C7;
        }

        .hero-title {
            font-size: 30px;
            font-weight: 300;
            letter-spacing: 4px;
            color: #1B1B1B;
            margin-bottom: 10px;
        }

        .hero-subtitle {
            font-size: 18px;
            color: #5D5D5D;
            letter-spacing: 1px;
        }

        .small-label {
            color: #1B5E20;
            font-size: 60px;
            font-weight: bold;
            letter-spacing: 2px;
        }

        .section-card {
            background-color: white;
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 20px;
            border: 1px solid #E0DDD6;
            box-shadow: 0px 3px 12px rgba(0,0,0,0.04);
        }

        .section-title {
            font-size: 26px;
            font-weight: 600;
            color: #1B5E20;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero">
            <div class="small-label">STARBUCKS DIRECTORY</div>
            <div class="hero-title">WELCOME<br>TO THE STORE EXPLORER</div>
            <div class="hero-subtitle">
                Explore Starbucks locations by country, ownership type, city, and map location.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    df = load_data(DATA_FILE)

    # [COLUMNS]
    df["Location"] = df["City"] + ", " + df["Country"]

    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

    st.sidebar.title("Filters")  # [ST3]
    st.sidebar.write("Use these controls to customize the dashboard.")

    countries = sorted(df["Country"].dropna().unique())

    if "US" in countries:
        default_country = countries.index("US")
    else:
        default_country = 0

    # [ST1]
    country = st.sidebar.selectbox("Choose a country:", countries, index=default_country)

    ownership_types = sorted(df["Ownership Type"].dropna().unique())

    # [ST1]
    ownership = st.sidebar.selectbox("Choose ownership type:", ownership_types)

    # [ST2]
    top_n = st.sidebar.slider("Number of top cities to show:", 5, 20, 10)

    search_city = st.sidebar.text_input("Search for a city:")

    # [FILTER1]
    df_country = df[df["Country"] == country]

    # [FILTER2]
    df_filtered = filter_data(df, country, ownership)

    if search_city != "":
        df_filtered = df_filtered[df_filtered["City"].str.contains(search_city, case=False, na=False)]

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Project Overview</div>', unsafe_allow_html=True)
    st.write(
        "This dashboard shows Starbucks store locations, store ownership types, "
        "top cities, and map locations based on the filters selected by the user."
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Selected Country", country)
    col2.metric("Ownership Type", ownership)
    col3.metric("Stores Found", len(df_filtered))
    col4.metric("Cities Found", df_filtered["City"].nunique())
    st.markdown('</div>', unsafe_allow_html=True)

    if len(df_filtered) > 0:
        tab1, tab2, tab3 = st.tabs(["Data Table", "Visualizations", "Map"])

        with tab1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Filtered Store Data</div>', unsafe_allow_html=True)
            st.write("The table below shows the stores that match your selected filters.")

            table = df_filtered[
                ["Store Name", "City", "State/Province", "Country", "Ownership Type", "Location"]
            ]

            st.dataframe(table, use_container_width=True, height=350)

            csv = table.to_csv(index=False)
            st.download_button(
                label="Download Filtered Data",
                data=csv,
                file_name="filtered_starbucks_data.csv",
                mime="text/csv"
            )

            # [MAXMIN]
            most_city, most_count = city_info(df_filtered)

            st.success("City with the most Starbucks stores: " + most_city)
            st.info("Number of stores in that city: " + str(most_count))

            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Visualizations</div>', unsafe_allow_html=True)
            st.write("The bar chart shows top cities. The pie chart shows ownership type distribution.")

            # [SORT]
            city_counts = df_filtered["City"].value_counts().reset_index()
            city_counts.columns = ["City", "Store Count"]
            city_counts = city_counts.sort_values("Store Count", ascending=False)

            top_cities = city_counts.head(top_n)

            chart1, chart2 = st.columns(2)

            with chart1:
                st.write("Top Cities by Store Count")

                # [CHART1]
                fig, ax = plt.subplots(figsize=(5, 3))
                ax.bar(top_cities["City"], top_cities["Store Count"], color="#1B5E20")
                ax.set_title("Top Cities", fontsize=11)
                ax.set_xlabel("City", fontsize=9)
                ax.set_ylabel("Stores", fontsize=9)
                ax.tick_params(axis="x", rotation=45, labelsize=8)
                ax.tick_params(axis="y", labelsize=8)
                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)

            with chart2:
                st.write("Ownership Type Breakdown")

                ownership_counts = df_country["Ownership Type"].value_counts()

                # [CHART2]
                fig2, ax2 = plt.subplots(figsize=(4, 3))
                ax2.pie(
                    ownership_counts,
                    labels=ownership_counts.index,
                    autopct="%1.1f%%",
                    startangle=90,
                    textprops={"fontsize": 8}
                )
                ax2.set_title("Ownership Breakdown", fontsize=11)
                plt.tight_layout()
                st.pyplot(fig2, use_container_width=True)

            # [ITERLOOP]
            count = 0
            for city in df_filtered["City"]:
                count = count + 1

            # [DICTMETHOD]
            summary = {
                "Country": country,
                "Ownership": ownership,
                "Stores": len(df_filtered),
                "Cities": df_filtered["City"].nunique()
            }

            with st.expander("Technical Summary"):
                st.write("Rows checked with loop:", count)
                st.write("Summary keys:", summary.keys())
                st.write("Summary values:", summary.values())

            st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Store Location Map</div>', unsafe_allow_html=True)
            st.write("Each green dot represents a Starbucks store. Hover over a dot to see details.")

            map_df = df_filtered.dropna(subset=["Latitude", "Longitude"])

            if len(map_df) > 0:
                # [MAP]
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=map_df,
                    get_position=["Longitude", "Latitude"],
                    get_radius=300,
                    get_fill_color=[27, 94, 32, 170],
                    pickable=True
                )

                view_state = pdk.ViewState(
                    latitude=map_df["Latitude"].mean(),
                    longitude=map_df["Longitude"].mean(),
                    zoom=4
                )

                tooltip = {
                    "html": "<b>Store:</b> {Store Name}<br>"
                            "<b>City:</b> {City}<br>"
                            "<b>Country:</b> {Country}<br>"
                            "<b>Ownership:</b> {Ownership Type}",
                    "style": {"backgroundColor": "#1B5E20", "color": "white"}
                }

                st.pydeck_chart(
                    pdk.Deck(
                        initial_view_state=view_state,
                        layers=[layer],
                        tooltip=tooltip
                    )
                )
            else:
                st.warning("No map data is available for this selection.")

            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.warning("No stores match your filters. Try changing the country, ownership type, or city search.")


main()
