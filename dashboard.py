import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit_authenticator as stauth

# Set page config
st.set_page_config(page_title="📊 Insurance Dashboard", layout="wide")

# -------------------------------
# GCP Credentials from Secrets
# -------------------------------
gcp_secrets = st.secrets["gcp_service_account"]

credentials = Credentials.from_service_account_info(
    {
        "type": gcp_secrets["type"],
        "project_id": gcp_secrets["project_id"],
        "private_key_id": gcp_secrets["private_key_id"],
        "private_key": gcp_secrets["private_key"],
        "client_email": gcp_secrets["client_email"],
        "client_id": gcp_secrets["client_id"],
        "auth_uri": gcp_secrets["auth_uri"],
        "token_uri": gcp_secrets["token_uri"],
        "auth_provider_x509_cert_url": gcp_secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": gcp_secrets["client_x509_cert_url"],
    },
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
)

gc = gspread.authorize(credentials)

# -------------------------------
# Authentication Setup
# -------------------------------
auth_config = st.secrets["auth_config"]

names = [auth_config["usernames"]["mohit"]["name"], auth_config["usernames"]["adil"]["name"]]
usernames = ["mohit", "adil"]
passwords = [auth_config["usernames"]["mohit"]["password"], auth_config["usernames"]["adil"]["password"]]

hashed_passwords = passwords  # already hashed

authenticator = stauth.Authenticate(
    names,
    usernames,
    hashed_passwords,
    auth_config["cookie"]["name"],
    auth_config["cookie"]["key"],
    auth_config["cookie"]["expiry_days"]
)

name, authentication_status, username = authenticator.login("Login", "main")

# -------------------------------
# Auth Logic
# -------------------------------
if authentication_status is False:
    st.error("❌ Username or password is incorrect")
elif authentication_status is None:
    st.warning("⚠️ Please enter your username and password")
elif authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name} 👋")

    # -------------------------------
    # Load Google Sheet Data
    # -------------------------------
    sheet_id = "1MBI2PXlrVXIeeLFUyfNDCiuUG_-Lnm0PdMgxzg_kmcg"
    daily_sheet = "Daily"
    periods_sheet = "Periods"

    @st.cache_data(ttl=600)
    def load_data():
        sh = gc.open_by_key(sheet_id)
        df_daily = pd.DataFrame(sh.worksheet(daily_sheet).get_all_records())
        df_periods = pd.DataFrame(sh.worksheet(periods_sheet).get_all_records())
        return df_daily, df_periods

    df_daily, df_periods = load_data()

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
