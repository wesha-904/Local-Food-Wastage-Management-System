import streamlit as st
import pandas as pd
import sqlite3
import datetime

# --- Connect to database ---
conn = sqlite3.connect("food_wastage.db")
c = conn.cursor()

def show_dashboard():
    st.title("🍽️ Food Donation & Claims Dashboard")
    st.write("📊 Dashboard powered by Streamlit & SQLite")

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
    SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
    FROM food_listings
    GROUP BY Provider_Type
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
    SELECT Location, COUNT(Food_ID) AS Listings
    FROM food_listings
    GROUP BY Location
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
    SELECT Meal_Type, COUNT(c.Claim_ID) AS Claim_Count
    FROM food_listings f
    JOIN claims c ON f.Food_ID = c.Food_ID
    GROUP BY Meal_Type
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
    SELECT Location, COUNT(c.Claim_ID) AS Total_Claims
    FROM food_listings f
    JOIN claims c ON f.Food_ID = c.Food_ID
    GROUP BY Location
    ORDER BY Total_Claims DESC
    LIMIT 10;
    """, conn)
    st.subheader("1️⃣5️⃣ Top 10 Cities by Food Claims")
    st.bar_chart(top_claiming_cities.set_index('Location'))
    st.write("📊 Dashboard powered by Streamlit & SQLite")

def show_list_food():
    st.title("➕ List New Food Surplus")
    st.markdown("---")
    providers = pd.read_sql("SELECT Provider_ID, Name, City, Type FROM providers;", conn)
    provider_names = providers['Name'].tolist()

    with st.form("list_food_form"):
        st.subheader("Food Item Details")
        provider_name = st.selectbox("Select Provider:", provider_names)
        provider_info = providers[providers['Name'] == provider_name]

        if not provider_info.empty:
            provider_id = int(provider_info['Provider_ID'].iloc[0])
            provider_type = provider_info['Type'].iloc[0]
            location = provider_info['City'].iloc[0]

            food_name = st.text_input("Food Name:")
            food_type = st.selectbox("Food Type:", ["Vegetables", "Fruits", "Prepared Meal", "Snacks", "Bakery", "Dairy"])
            quantity = st.number_input("Quantity:", min_value=1, step=1)
            expiry_date = st.date_input("Expiry Date:", min_value=datetime.date.today())
            meal_type = st.selectbox("Meal Type:", ["Breakfast", "Lunch", "Dinner", "Snack", "Any"])

            submitted = st.form_submit_button("List Food")

            if submitted:
                if food_name and quantity:
                    c.execute("""
                        INSERT INTO food_listings (Provider_ID, Provider_Type, Location, Food_Name, Food_Type, Quantity, Expiry_Date, Meal_Type) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (provider_id, provider_type, location, food_name, food_type, quantity, str(expiry_date), meal_type))
                    conn.commit()
                    st.success("🎉 Food item listed successfully!")
                else:
                    st.error("Please fill in all the details.")
        else:
            st.info("Please add a provider first using the 'Add Provider' page.")

def show_claim_food():
    st.title("🛒 Claim Available Food")
    st.markdown("---")

    receivers = pd.read_sql("SELECT Receiver_ID, Name FROM receivers;", conn)
    receiver_names = receivers['Name'].tolist()

    available_food = pd.read_sql("""
        SELECT Food_ID, Food_Name, Quantity, Expiry_Date, Provider_Type, Location
        FROM food_listings
        WHERE Food_ID NOT IN (SELECT Food_ID FROM claims WHERE Status IN ('Pending', 'Completed'))
        AND DATE(Expiry_Date) > DATE('now')
    """, conn)

    if available_food.empty:
        st.info("No food items are currently available for claiming.")
        return

    with st.form("claim_food_form"):
        st.subheader("Claim Details")
        receiver_name = st.selectbox("Select Receiver:", receiver_names)
        receiver_id = receivers[receivers['Name'] == receiver_name]['Receiver_ID'].iloc[0]

        food_options = available_food.apply(
            lambda row: f"{row['Food_Name']} from {row['Provider_Type']} in {row['Location']} (Qty: {row['Quantity']})", axis=1
        ).tolist()
        
        selected_food_str = st.selectbox("Select Food to Claim:", food_options)
        
        selected_food_id = None
        if selected_food_str:
            selected_food_id = available_food[
                available_food.apply(
                    lambda row: f"{row['Food_Name']} from {row['Provider_Type']} in {row['Location']} (Qty: {row['Quantity']})", axis=1
                ) == selected_food_str
            ]['Food_ID'].iloc[0]

        submitted = st.form_submit_button("Claim Food")

        if submitted:
            if selected_food_id:
                c.execute("""
                    INSERT INTO claims (Food_ID, Receiver_ID, Status, Timestamp) 
                    VALUES (?, ?, ?, ?)
                """, (selected_food_id, receiver_id, 'Pending', datetime.datetime.now()))
                conn.commit()
                st.success("✅ Food claimed successfully! Awaiting provider confirmation.")
            else:
                st.error("Please select a food item to claim.")

def show_add_provider():
    st.title("➕ Add New Provider")
    st.markdown("---")
    with st.form("add_provider_form"):
        st.subheader("Provider Details")
        name = st.text_input("Name:")
        contact = st.text_input("Contact:")
        address = st.text_input("Address:")
        city = st.text_input("City:")
        provider_type = st.selectbox("Type:", ["Restaurant", "Bakery", "Supermarket", "Grocery Store", "Catering Service"])

        submitted = st.form_submit_button("Add Provider")

        if submitted:
            if name and contact and city and provider_type:
                c.execute("""
                    INSERT INTO providers (Name, Contact, Address, City, Type) 
                    VALUES (?, ?, ?, ?, ?)
                """, (name, contact, address, city, provider_type))
                conn.commit()
                st.success(f"✅ Provider '{name}' added successfully!")
            else:
                st.error("Please fill in all the details.")

def show_add_receiver():
    st.title("➕ Add New Receiver")
    st.markdown("---")
    with st.form("add_receiver_form"):
        st.subheader("Receiver Details")
        name = st.text_input("Name:")
        contact = st.text_input("Contact:")
        city = st.text_input("City:")
        receiver_type = st.selectbox("Type:", ["Non-profit", "Community Center", "Individual", "Other"])

        submitted = st.form_submit_button("Add Receiver")

        if submitted:
            if name and contact and city and receiver_type:
                c.execute("""
                    INSERT INTO receivers (Name, Contact, City, Type) 
                    VALUES (?, ?, ?, ?)
                """, (name, contact, city, receiver_type))
                conn.commit()
                st.success(f"✅ Receiver '{name}' added successfully!")
            else:
                st.error("Please fill in all the details.")

# --- Main App Logic ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Dashboard", "List Food", "Claim Food", "Add Provider", "Add Receiver"])

if page == "Dashboard":
    show_dashboard()
elif page == "List Food":
    show_list_food()
elif page == "Claim Food":
    show_claim_food()
elif page == "Add Provider":
    show_add_provider()
elif page == "Add Receiver":
    show_add_receiver()

conn.close()
