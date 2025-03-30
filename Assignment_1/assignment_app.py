import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import date
import matplotlib.pyplot as plt
from io import BytesIO


st.set_page_config(page_title="Airbnb Price Estimator", layout="wide", initial_sidebar_state="expanded")


model = joblib.load(
    "./Prototyping_Emre_Ozener/Assignment_1/airbnb_price_model.pkl")
preprocess_pipe = joblib.load(
    "./Prototyping_Emre_Ozener/Assignment_1/preprocessing_pipeline.pkl")
data_path = "https://github.com/jnin/information-systems/raw/refs/heads/main/data/Airbnb_Hackathon_IA1_2024.zip"
df = pd.read_csv(data_path)


if "log_price" in df.columns:
    df["price"] = np.exp(df["log_price"])
else:
    st.error("Dataset does not contain 'log_price' column.")
    st.stop()


cities = sorted(df["city"].dropna().unique())
property_types = sorted(df["property_type"].dropna().unique())
room_types = sorted(df["room_type"].dropna().unique())
bed_types = sorted(df["bed_type"].dropna().unique())
cancellation_policies = sorted(df["cancellation_policy"].dropna().unique())


with st.sidebar:
    st.title("Sections")
    nav = st.radio("Go to", ["Landlord Dashboard", "About"])
    if nav == "About":
        st.markdown(
            """
            **Landlord Dashboard for Airbnb**

            This app helps landlords decide on a price, calculate their revenue, see the market trends, and download a full report.
            """
        )
        st.stop()


st.title("Airbnb Landlord Dashboard")
st.markdown("Estimate your nightly price, calculate revenue, view market trends, and download your full report.")


tabs = st.tabs(["Price Estimator", "Revenue Calculator", "Market Trends Dashboard", "Full Report"])

# ------------------ Price Estimator Tab ------------------
with tabs[0]:
    st.subheader("Enter Your Property Details")

    with st.expander("Property Details", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            property_type = st.selectbox("Property Type", property_types, key="property_type")
            room_type = st.selectbox("Room Type", room_types, key="room_type")
            bed_type = st.selectbox("Bed Type", bed_types, key="bed_type")
        with col2:
            accommodates = st.number_input("Accommodates", 1, 20, 2, key="accommodates")
            bedrooms = st.number_input("Bedrooms", 0, 10, 1, key="bedrooms")
            beds = st.number_input("Beds", 0, 10, 1, key="beds")
        with col3:
            bathrooms = st.number_input("Bathrooms", 0, 10, 1, key="bathrooms")
            cancellation_policy = st.selectbox("Cancellation Policy", cancellation_policies, key="cancellation_policy")
            cleaning_fee = st.checkbox("Includes Cleaning Fee?", key="cleaning_fee")

    with st.expander("Location Details", expanded=True):
        city = st.selectbox("City", cities, key="city")
        df_city = df[df["city"] == city]
        zipcodes = sorted(df_city["zipcode"].dropna().astype(str).unique())
        zipcode = st.selectbox("Zipcode", zipcodes, key="zipcode")
        location = f"{city}, {zipcode}"
        st.markdown(f"**Location:** {location}")
        if "latitude" in df_city.columns and "longitude" in df_city.columns:
            map_data = df_city[df_city["zipcode"].astype(str) == zipcode][["latitude", "longitude"]]
            if not map_data.empty:
                st.map(map_data, use_container_width=True)

    with st.expander("Host & Reviews", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            host_pic = st.checkbox("Host Has Profile Picture?", key="host_has_profile_pic")
            host_verified = st.checkbox("Host Identity Verified?", key="host_identity_verified")
            host_response = st.slider("Host Response Rate (%)", 0, 100, 90, key="host_response_rate")
        with col2:
            instant_bookable = st.checkbox("Instant Bookable?", key="instant_bookable")
            num_reviews = st.number_input("Number of Reviews", 0, 1000, 10, key="number_of_reviews")
            review_rating = st.slider("Review Score Rating", 0.0, 5.0, 4.5, 0.1, key="review_scores_rating")

    sub_tabs = st.tabs(["Additional Details", "Amenities"])
    with sub_tabs[0]:
        st.subheader("Additional Details")
        days_first = st.number_input("Days Since First Review", 0, 5000, 365, key="days_since_first_review")
        days_last = st.number_input("Days Since Last Review", 0, 5000, 100, key="days_since_last_review")
        days_host = st.number_input("Days Since Host Started", 0, 5000, 365, key="days_since_host_since")
    with sub_tabs[1]:
        st.subheader("Amenities")
        amenities_list = [
            'Wireless Internet', 'Kitchen', 'Heating', 'Essentials', 'Smoke detector',
            'Air conditioning', 'TV', 'Shampoo', 'Hangers', 'Carbon monoxide detector',
            'Internet', 'Laptop friendly workspace', 'Washer', 'Hair dryer', 'Dryer',
            'Iron', 'Family/kid friendly', 'Fire extinguisher', 'First aid kit'
        ]
        selected_amenities = st.multiselect("Select Amenities", amenities_list)


    input_data = {
        "property_type": property_type,
        "room_type": room_type,
        "accommodates": accommodates,
        "bathrooms": bathrooms,
        "bed_type": bed_type,
        "cancellation_policy": cancellation_policy,
        "cleaning_fee": cleaning_fee,
        "bedrooms": bedrooms,
        "beds": beds,
        "host_has_profile_pic": host_pic,
        "host_identity_verified": host_verified,
        "host_response_rate": host_response / 100,
        "instant_bookable": instant_bookable,
        "number_of_reviews": num_reviews,
        "review_scores_rating": review_rating,
        "zipcode": zipcode,
        "city": city,
        "location": location,
        "days_since_first_review": days_first,
        "days_since_last_review": days_last,
        "days_since_host_since": days_host,
    }
    for amenity in amenities_list:
        input_data[f"amenity_{amenity}"] = 1 if amenity in selected_amenities else 0
    input_data["amenity_translation missing: en.hosting_amenity_50"] = 0

    st.divider()
    if st.button("Estimate Price"):
        df_input = pd.DataFrame([input_data])
        transformed = preprocess_pipe.transform(df_input)
        log_price = model.predict(transformed)[0]
        predicted_price = np.exp(log_price)
        st.success(f"Estimated Nightly Price: €{predicted_price:.2f}")
        st.session_state["predicted_price"] = predicted_price

# ------------------ Revenue Calculator Tab ------------------
with tabs[1]:
    st.subheader("Revenue Calculator")
    if "predicted_price" in st.session_state:
        nights = st.slider("Nights booked per month", 0, 30, 15)
        revenue = st.session_state["predicted_price"] * nights
        st.info(f"Estimated Monthly Revenue: €{revenue:.2f}")
    else:
        st.info("Please estimate the nightly price first.")

# ------------------ Market Trends Dashboard Tab ------------------
with tabs[2]:
    st.subheader("Market Trends Dashboard")

    # Overall metrics
    overall_avg = df["price"].mean()
    overall_median = df["price"].median()
    total_listings = len(df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Nightly Price", f"€{overall_avg:.2f}")
    col2.metric("Median Nightly Price", f"€{overall_median:.2f}")
    col3.metric("Total Listings", total_listings)


    chart_option = st.selectbox("Select Chart",
                                ["Average Price by City","Average Price by Property Type"])

    if chart_option == "Average Price by City":
        st.markdown("#### Average Nightly Price by City")
        avg_price_city = df.groupby("city")["price"].mean().reset_index()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(avg_price_city["city"], avg_price_city["price"])
        ax.set_xlabel("City")
        ax.set_ylabel("Average Nightly Price")
        ax.set_title("Average Nightly Price by City")
        st.pyplot(fig)
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        st.download_button("Download Graph", data=buf, file_name="avg_price_by_city.png", mime="image/png")
    elif chart_option == "Average Price by Property Type":
        st.markdown("#### Average Price by Property Type")
        avg_price_property = df.groupby("property_type")["price"].mean().reset_index()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(avg_price_property["property_type"], avg_price_property["price"])
        ax.set_xlabel("Property Type")
        ax.set_ylabel("Average Nightly Price")
        ax.set_title("Average Price by Property Type")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        st.download_button("Download Graph", data=buf, file_name="avg_price_by_property_type.png", mime="image/png")

# ------------------ Full Report Tab ------------------
with tabs[3]:
    st.subheader("Full Report")
    if "predicted_price" in st.session_state:
        report_nights = st.number_input("Nights booked per month (for report)", 0, 30, 15, key="report_nights")
        revenue_report = st.session_state["predicted_price"] * report_nights
        report_text = f"""Airbnb Price Estimation Report
Date: {date.today().strftime("%B %d, %Y")}

Estimated Nightly Price: €{st.session_state["predicted_price"]:.2f}
Projected Nights Booked per Month: {report_nights}
Estimated Monthly Revenue: €{revenue_report:.2f}

Market Trends Insights:
- Average nightly prices by city and overall price distribution are available in the Market Trends Dashboard.

Thank you for using the Airbnb Price Estimator.
"""
        st.text_area("Report", report_text, height=300)
        st.download_button("Download Report", report_text, file_name="airbnb_report.txt", mime="text/plain")
    else:
        st.info("Please estimate the nightly price first to generate a full report.")

