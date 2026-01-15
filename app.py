import streamlit as st
import sqlite3
from datetime import datetime

# ---- DATABASE SETUP ----
conn = sqlite3.connect("microinsurance.db")
c = conn.cursor()

# Create tables if not exist
c.execute(
    """CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    guardian_name TEXT,
    referral_code TEXT,
    registered_at TEXT
)"""
)

c.execute(
    """CREATE TABLE IF NOT EXISTS policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    savings_amount REAL,
    coverage_type TEXT,
    payment_frequency TEXT,
    payment_currency TEXT,
    created_at TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
)"""
)

c.execute(
    """CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    claim_type TEXT,
    claim_status TEXT,
    submitted_at TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
)"""
)

conn.commit()

# ---- STREAMLIT APP ----
st.title("Bundled Microinsurance Platform")
st.markdown(
    """This is a microinsurance MVP: bundled savings, life & critical illness coverage."""
)

menu = ["Register", "Create Policy", "Submit Claim", "View Dashboard"]
choice = st.sidebar.selectbox("Menu", menu)

# ---- REGISTER CUSTOMER ----
if choice == "Register":
    st.subheader("Customer Registration")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    guardian = st.text_input("Guardian Name")
    referral = st.text_input("Referral Code (Optional)")

    if st.button("Register"):
        try:
            c.execute(
                "INSERT INTO customers (name,email,guardian_name,referral_code,registered_at) VALUES (?,?,?,?,?)",
                (
                    name,
                    email,
                    guardian,
                    referral,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            conn.commit()
            st.success("Customer registered successfully!")
        except sqlite3.IntegrityError:
            st.error("Email already registered.")

# ---- CREATE POLICY ----
elif choice == "Create Policy":
    st.subheader("Create Microinsurance Policy")
    c.execute("SELECT id, name FROM customers")
    customers = c.fetchall()

    if customers:
        customer_dict = {name: cid for cid, name in customers}
        selected_customer = st.selectbox("Select Customer", list(customer_dict.keys()))
        savings = st.number_input("Savings Amount", min_value=10.0, value=50.0)
        coverage = st.selectbox("Coverage Type", ["Life & Critical Illness"])
        payment_freq = st.selectbox("Payment Frequency", ["Daily", "Weekly", "Monthly"])
        currency = st.selectbox("Payment Currency", ["KES", "USD"])

        if st.button("Create Policy"):
            c.execute(
                "INSERT INTO policies (customer_id,savings_amount,coverage_type,payment_frequency,payment_currency,created_at) VALUES (?,?,?,?,?,?)",
                (
                    customer_dict[selected_customer],
                    savings,
                    coverage,
                    payment_freq,
                    currency,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            conn.commit()
            st.success("Policy created successfully!")
    else:
        st.warning("No customers found. Please register first.")

# ---- SUBMIT CLAIM ----
elif choice == "Submit Claim":
    st.subheader("Submit a Claim")
    c.execute("SELECT id, name FROM customers")
    customers = c.fetchall()

    if customers:
        customer_dict = {name: cid for cid, name in customers}
        selected_customer = st.selectbox("Select Customer", list(customer_dict.keys()))
        claim_type = st.selectbox("Claim Type", ["Life", "Critical Illness"])

        if st.button("Submit Claim"):
            c.execute(
                "INSERT INTO claims (customer_id, claim_type, claim_status, submitted_at) VALUES (?,?,?,?)",
                (
                    customer_dict[selected_customer],
                    claim_type,
                    "Pending",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            conn.commit()
            st.success("Claim submitted successfully!")
    else:
        st.warning("No customers found. Please register first.")

# ---- DASHBOARD ----
elif choice == "View Dashboard":
    st.subheader("Customer & Policy Dashboard")

    st.markdown("**Customers:**")
    c.execute("SELECT * FROM customers")
    data = c.fetchall()
    st.dataframe(data)

    st.markdown("**Policies:**")
    c.execute("SELECT * FROM policies")
    policies = c.fetchall()
    st.dataframe(policies)

    st.markdown("**Claims:**")
    c.execute("SELECT * FROM claims")
    claims = c.fetchall()
    st.dataframe(claims)
