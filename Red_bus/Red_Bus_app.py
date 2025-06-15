import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Function to get SQLAlchemy engine
def get_engine():
    return create_engine("mysql+pymysql://root:root@127.0.0.1/redbus")

# Function to fetch route names starting with a specific letter
def fetch_route_names(engine, starting_letter):
    query = """
        SELECT DISTINCT Route_Name 
        FROM bus_routes 
        WHERE Route_Name LIKE %s 
        ORDER BY Route_Name
    """
    like_pattern = f"{starting_letter}%"
    df = pd.read_sql(query, engine, params=(like_pattern,))
    return df['Route_Name'].tolist()

# Function to fetch route data by Route_Name and price sort
def fetch_data(engine, route_name, price_sort_order):
    price_sort = "ASC" if price_sort_order == "Low to High" else "DESC"
    query = f"""
        SELECT * 
        FROM bus_routes 
        WHERE Route_Name = %s 
        ORDER BY Star_Rating DESC, Price {price_sort}
    """
    df = pd.read_sql(query, engine, params=(route_name,))
    return df

# Function to apply filters
def filter_data(df, star_ratings, bus_types):
    if not star_ratings and not bus_types:
        return df
    if star_ratings and not bus_types:
        return df[df['Star_Rating'].isin(star_ratings)]
    if not star_ratings and bus_types:
        return df[df['Bus_Type'].isin(bus_types)]
    return df[df['Star_Rating'].isin(star_ratings) & df['Bus_Type'].isin(bus_types)]

# Streamlit app
def main():
    st.header("🚌 Easy and Secure Online Bus Tickets Booking")

    engine = get_engine()

    # Sidebar input for starting letter
    starting_letter = st.sidebar.text_input('Enter starting letter of Route Name', 'A')

    if starting_letter:
        route_names = fetch_route_names(engine, starting_letter.upper())

        if route_names:
            selected_route = st.sidebar.radio("Select Route Name", route_names)

            if selected_route:
                price_sort_order = st.sidebar.selectbox("Sort by Price", ["Low to High", "High to Low"])

                # Fetch data
                data = fetch_data(engine, selected_route, price_sort_order)

                if not data.empty:
                    st.subheader(f"🗺️ Route Details for: {selected_route}")
                    st.dataframe(data)

                    # Filters
                    star_ratings = data['Star_Rating'].dropna().unique().tolist()
                    selected_ratings = st.multiselect("Filter by Star Rating", star_ratings)

                    bus_types = data['Bus_Type'].dropna().unique().tolist()
                    selected_bus_types = st.multiselect("Filter by Bus Type", bus_types)

                    # Apply filters
                    filtered_data = filter_data(data, selected_ratings, selected_bus_types)

                    if not filtered_data.empty:
                        st.subheader("🔍 Filtered Results")
                        st.dataframe(filtered_data)
                    else:
                        st.warning("No buses found for selected filters.")
                else:
                    st.warning("No data found for selected route.")
        else:
            st.warning("No route names starting with that letter found.")

if __name__ == '__main__':
    main()