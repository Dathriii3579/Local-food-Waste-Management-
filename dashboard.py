import sqlite3
import pandas as pd
import streamlit as st 

st.set_page_config(page_title="🍴 Food Waste Management Portal", layout="wide")
conn = sqlite3.connect("food_donation.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(claims);")
columns = cursor.fetchall()
for col in columns:
    print(col)

providers = pd.read_csv('/Users/dathril/Desktop/localfoodwaste_managementproject/providers_data (2).csv')
receivers = pd.read_csv('/Users/dathril/Desktop/localfoodwaste_managementproject/receivers_data (1).csv')
food_listings = pd.read_csv('/Users/dathril/Desktop/localfoodwaste_managementproject/food_listings_data.csv')
claims = pd.read_csv('/Users/dathril/Desktop/localfoodwaste_managementproject/claims_data (1).csv')

providers.to_sql("providers", conn, if_exists="replace", index=False)
receivers.to_sql("receivers", conn, if_exists="replace", index=False)
food_listings.to_sql("food_listings", conn, if_exists="replace", index=False)
claims.to_sql("claims", conn, if_exists="replace", index=False)


tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
print(tables)

st.set_page_config(page_title="🍴 Food Waste Management Portal", layout="wide")

st.title("🍴 Local Food Waste Management Dashboard")

# Sidebar navigation
menu = ["Providers", "Receivers", "Food Listings", "Claims", "Insights"]
choice = st.sidebar.selectbox("Navigate", menu)

if choice == "Providers":
    df = pd.read_sql_query("SELECT * FROM providers;", conn)
    st.subheader("Providers Data")
    st.dataframe(df)

elif choice == "Receivers":
    df = pd.read_sql_query("SELECT * FROM receivers;", conn)
    st.subheader("Receivers Data")
    st.dataframe(df)

elif choice == "Food Listings":
    df = pd.read_sql_query("SELECT * FROM food_listings;", conn)
    st.subheader("Food Listings Data")
    st.dataframe(df)

elif choice == "Claims":
    df = pd.read_sql_query("SELECT * FROM claims;", conn)
    st.subheader("Claims Data")
    st.dataframe(df)

# -----------------------------
# Insights (SQL Queries)
# -----------------------------
elif choice == "Insights":
    st.subheader("📊 Analysis & Insights")
    
    # Dictionary of all queries with titles
    insights_queries = {
        "1️⃣ Food Providers per City": {
            "query": "SELECT city, COUNT(*) AS total_providers FROM providers GROUP BY city;",
            "type": "table"
        },
        "2️⃣ Food Receivers per City": {
            "query": "SELECT city, COUNT(*) AS total_receivers FROM receivers GROUP BY city;",
            "type": "table"
        },
        "3️⃣ Food Contribution by Provider Type": {
            "query": """
            SELECT p.type AS provider_type, SUM(f.quantity) AS total_contribution
            FROM providers p
            JOIN food_listings f ON p.provider_id = f.provider_id
            GROUP BY p.type
            ORDER BY total_contribution DESC;
            """,
            "type": "bar"
        },
        "4️⃣ Top 5 Receivers by Total Claimed": {
            "query": """
            SELECT r.name, SUM(f.quantity) AS total_claimed
            FROM receivers r
            JOIN claims c ON r.receiver_id = c.receiver_id
            JOIN food_listings f ON c.food_id = f.food_id
            GROUP BY r.name
            ORDER BY total_claimed DESC
            LIMIT 5;
            """,
            "type": "table"
        },
        "5️⃣ Total Available Food": {
            "query": "SELECT SUM(quantity) AS total_available FROM food_listings;",
            "type": "metric",
            "metric_col": "total_available"
        },
        "6️⃣ City with Highest Food Listings": {
            "query": """
            SELECT p.city, COUNT(f.food_id) AS total_listings
            FROM providers p
            JOIN food_listings f ON p.provider_id = f.provider_id
            GROUP BY p.city
            ORDER BY total_listings DESC
            LIMIT 1;
            """,
            "type": "table"
        },
        "7️⃣ Most Common Food Types": {
            "query": """
            SELECT Food_Type AS food_type, COUNT(*) AS count_food
            FROM food_listings
            GROUP BY Food_Type
            ORDER BY count_food DESC;
            """,
            "type": "bar"
        },
        "8️⃣ Food Claims per Item": {
            "query": """
            SELECT f.food_name, COUNT(c.claim_id) AS total_claims
            FROM claims c
            JOIN food_listings f ON c.food_id = f.food_id
            GROUP BY f.food_name
            ORDER BY total_claims DESC;
            """,
            "type": "table"
        },
        "9️⃣ Provider with Most Successful Claims": {
            "query": """
            SELECT p.provider_id, COUNT(c.claim_id) AS successful_claims
            FROM claims c
            JOIN food_listings f ON f.food_id = c.food_id
            JOIN providers p ON p.provider_id = f.provider_id
            WHERE c.Status = "successful"
            GROUP BY p.provider_id
            ORDER BY successful_claims DESC
            LIMIT 1;
            """,
            "type": "table"
        },
        "10️⃣ Claim Status Distribution (%)": {
            "query": """
            SELECT status, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS percentage
            FROM claims
            GROUP BY status;
            """,
            "type": "table"
        },
        "11️⃣ Average Quantity Claimed per Receiver": {
            "query": """
            SELECT r.name, AVG(f.quantity) AS avg_claimed
            FROM claims c
            JOIN receivers r ON c.receiver_id = r.receiver_id
            JOIN food_listings f ON c.food_id = f.food_id
            GROUP BY r.name;
            """,
            "type": "table"
        },
        "12️⃣ Most Claimed Meal Type": {
            "query": """
            SELECT f.meal_type, SUM(f.quantity) AS total_claimed
            FROM claims c
            JOIN food_listings f ON c.food_id = f.food_id
            GROUP BY f.meal_type
            ORDER BY total_claimed DESC
            LIMIT 1;
            """,
            "type": "table"
        },
        "13️⃣ Total Quantity Donated by Provider": {
            "query": """
            SELECT p.name, SUM(f.quantity) AS total_donated
            FROM providers p
            JOIN food_listings f ON p.provider_id = f.provider_id
            GROUP BY p.name
            ORDER BY total_donated DESC;
            """,
            "type": "table"
        },
    }

    # Sidebar selectbox to choose query
    selected_insight = st.sidebar.selectbox("Choose an Insight", list(insights_queries.keys()))
    data_info = insights_queries[selected_insight]
    df = pd.read_sql_query(data_info["query"], conn)

    # Display based on type
    if data_info["type"] == "table":
        st.dataframe(df)
    elif data_info["type"] == "bar":
        st.bar_chart(df.set_index(df.columns[0]))
    elif data_info["type"] == "metric":
        st.metric(selected_insight, int(df[data_info["metric_col"]][0]))
