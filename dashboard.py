import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit_authenticator as stauth

st.set_page_config(page_title="📊 Insurance Dashboard", layout="wide")

# -------------------------------
# Load GCP credentials
# -------------------------------
gcp_secrets = st.secrets["gcp_service_account"]
credentials = Credentials.from_service_account_info(dict(gcp_secrets), scopes=[
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
])
gc = gspread.authorize(credentials)

# -------------------------------
# Load Auth Config (YAML format from secrets)
# -------------------------------
auth_config = st.secrets["auth_config"]

authenticator = stauth.Authenticate(
    credentials=auth_config,
    cookie_name=auth_config["cookie"]["name"],
    key=auth_config["cookie"]["key"],
    expiry_days=auth_config["cookie"]["expiry_days"]
)

# Streamlit login
name, authentication_status, username = authenticator.login(location="main", max_concurrent_users=10)

if authentication_status is False:
    st.error("❌ Incorrect username or password")
elif authentication_status is None:
    st.warning("⚠️ Please enter your login credentials")
elif authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name} 👋")

    # -------------------------------
    # Load Data from Google Sheets
    # -------------------------------
    sheet_id = "1MBI2PXlrVXIeeLFUyfNDCiuUG_-Lnm0PdMgxzg_kmcg"

    @st.cache_data(ttl=600)
    def load_data():
        sh = gc.open_by_key(sheet_id)
        df_daily = pd.DataFrame(sh.worksheet("Daily").get_all_records())
        df_periods = pd.DataFrame(sh.worksheet("Periods").get_all_records())
        return df_daily, df_periods

    df_daily, df_periods = load_data()

    # -------------------------------
    # Display Dashboard
    # -------------------------------
    tab1, tab2 = st.tabs(["📅 Daily", "📆 Periods"])

    with tab1:
        st.header("🔹 Daily Metrics")
        st.dataframe(df_daily)
        if not df_daily.empty and "channel" in df_daily.columns and "net_premium" in df_daily.columns:
            st.bar_chart(df_daily.groupby("channel")["net_premium"].sum())

    with tab2:
        st.header("🔹 Period Summary")
        st.dataframe(df_periods)
        if not df_periods.empty and "period" in df_periods.columns and "net_premium" in df_periods.columns:
            st.bar_chart(df_periods.groupby("period")["net_premium"].sum())
