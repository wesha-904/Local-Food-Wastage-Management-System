import streamlit as st
import pandas as pd
import sqlite3

# --- Connect to database ---
conn = sqlite3.connect("food_wastage.db")

st.title("🍽️ Food Donation & Claims Dashboard")

# --- 1. Providers & Receivers per City ---
providers_receivers = pd.read_sql("""
SELECT p.City, 
       COUNT(DISTINCT p.Provider_ID) AS Providers, 
       COUNT(DISTINCT r.Receiver_ID) AS Receivers
FROM providers p
LEFT JOIN receivers r ON p.City = r.City
GROUP BY p.City;
""", conn)

st.subheader("1️⃣ Providers & Receivers per City")
st.dataframe(providers_receivers)
st.bar_chart(providers_receivers.set_index('City'))

# --- 2. Top provider type by contribution ---
top_provider_type = pd.read_sql("""
SELECT p.Type, SUM(f.Quantity) AS Total_Quantity
FROM providers p
JOIN food_listings f ON p.Provider_ID = f.Provider_ID
GROUP BY p.Type
ORDER BY Total_Quantity DESC
LIMIT 1;
""", conn)
st.subheader("2️⃣ Top Provider Type by Contribution")
st.table(top_provider_type)

# --- 3. Provider contacts in a city ---
city_name = st.text_input("Enter city for provider contacts", "adambury")
provider_contacts = pd.read_sql("""
SELECT Name, Contact 
FROM providers
WHERE City = ?;
""", conn, params=(city_name,))
st.subheader(f"3️⃣ Provider Contacts in {city_name.title()}")
st.dataframe(provider_contacts)

# --- 4. Receivers with highest claims ---
top_receivers = pd.read_sql("""
WITH claim_counts AS (
    SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims
    FROM receivers r
    JOIN claims c ON r.Receiver_ID = c.Receiver_ID
    GROUP BY r.Name
)
SELECT Name, Total_Claims
FROM claim_counts
WHERE Total_Claims = (SELECT MAX(Total_Claims) FROM claim_counts);
""", conn)
st.subheader("4️⃣ Receivers with Highest Number of Claims")
st.table(top_receivers)

# --- 5. Total available food quantity ---
total_food = pd.read_sql("SELECT SUM(Quantity) AS Total_Quantity FROM food_listings;", conn)
st.subheader("5️⃣ Total Food Available")
st.metric("Total Quantity", total_food['Total_Quantity'].iloc[0])

# --- 6. City with most food listings ---
top_city_listings = pd.read_sql("""
SELECT p.City, COUNT(f.Food_ID) AS Listings
FROM providers p
JOIN food_listings f ON p.Provider_ID = f.Provider_ID
GROUP BY p.City
ORDER BY Listings DESC
LIMIT 1;
""", conn)
st.subheader("6️⃣ City with Most Food Listings")
st.table(top_city_listings)

# --- 7. Most common food types ---
food_types = pd.read_sql("""
SELECT Food_Type, COUNT(*) AS Count
FROM food_listings
GROUP BY Food_Type
ORDER BY Count DESC;
""", conn)
st.subheader("7️⃣ Most Common Food Types")
st.bar_chart(food_types.set_index('Food_Type'))

# --- 8. Claims per food item ---
claims_per_item = pd.read_sql("""
SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claim_Count
FROM food_listings f
JOIN claims c ON f.Food_ID = c.Food_ID
GROUP BY f.Food_Name;
""", conn)
st.subheader("8️⃣ Claims Per Food Item")
st.dataframe(claims_per_item)

# --- 9. Provider with highest successful claims ---
top_provider_claims = pd.read_sql("""
SELECT p.Name, COUNT(c.Claim_ID) AS Successful_Claims
FROM providers p
JOIN food_listings f ON p.Provider_ID = f.Provider_ID
JOIN claims c ON f.Food_ID = c.Food_ID
WHERE c.Status = 'Completed'
GROUP BY p.Name
ORDER BY Successful_Claims DESC
LIMIT 1;
""", conn)
st.subheader("9️⃣ Top Provider by Successful Claims")
st.table(top_provider_claims)

# --- 10. Claims percentage by status ---
claims_status = pd.read_sql("""
SELECT Status, 
       ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims)), 2) AS Percentage
FROM claims
GROUP BY Status;
""", conn)
st.subheader("🔟 Claims Percentage by Status")
st.dataframe(claims_status)
st.bar_chart(claims_status.set_index('Status'))

# --- 11. Average quantity claimed per receiver ---
avg_claim_per_receiver = pd.read_sql("""
SELECT r.Name, AVG(f.Quantity) AS Avg_Claimed
FROM receivers r
JOIN claims c ON r.Receiver_ID = c.Receiver_ID
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY r.Name;
""", conn)
st.subheader("1️⃣1️⃣ Average Quantity Claimed Per Receiver")
st.dataframe(avg_claim_per_receiver)

# --- 12. Most claimed meal type ---
most_claimed_meal = pd.read_sql("""
SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Claim_Count
FROM food_listings f
JOIN claims c ON f.Food_ID = c.Food_ID
GROUP BY f.Meal_Type
ORDER BY Claim_Count DESC;
""", conn)
st.subheader("1️⃣2️⃣ Most Claimed Meal Type")
st.bar_chart(most_claimed_meal.set_index('Meal_Type'))

# --- 13. Total food donated per provider ---
total_donated = pd.read_sql("""
SELECT p.Name, SUM(f.Quantity) AS Total_Donated
FROM providers p
JOIN food_listings f ON p.Provider_ID = f.Provider_ID
GROUP BY p.Name
ORDER BY Total_Donated DESC;
""", conn)
st.subheader("1️⃣3️⃣ Total Food Donated Per Provider")
st.dataframe(total_donated)

# --- 14. Food Items Near Expiry (Next 3 Days) & 15: Optional additional analysis ---
near_expiry_items = pd.read_sql("""
SELECT Food_Name, Expiry_Date, Quantity
FROM food_listings
WHERE DATE(Expiry_Date) <= DATE('now', '+3 day');
""", conn)
st.subheader("1️⃣4️⃣ Food Items Near Expiry (Next 3 Days)")
st.dataframe(near_expiry_items)

# --- 15. Top 10 Cities by Food Claims ---
top_claiming_cities = pd.read_sql("""
SELECT p.City, COUNT(c.Claim_ID) AS Total_Claims
FROM providers p
JOIN food_listings f ON p.Provider_ID = f.Provider_ID
JOIN claims c ON f.Food_ID = c.Food_ID
GROUP BY p.City
ORDER BY Total_Claims DESC
LIMIT 10;
""", conn)
st.subheader("1️⃣5️⃣ Top 10 Cities by Food Claims")
st.bar_chart(top_claiming_cities.set_index('City'))

# --- End of Dashboard ---
st.write("📊 Dashboard powered by Streamlit & SQLite")
