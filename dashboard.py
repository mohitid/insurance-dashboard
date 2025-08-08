import streamlit as st
import pandas as pd
import yaml
import gspread
from google.oauth2.service_account import Credentials
import streamlit_authenticator as stauth

# --- Load login credentials from YAML ---
with open('config.yaml') as file:
    config = yaml.safe_load(file)

# --- Initialize authenticator ---
authenticator = stauth.Authenticate(
    config,
    config['cookie']['name'],
    config['cookie']['key']
)

# --- Login UI ---
name, authentication_status, username = authenticator.login("Login", "main")

# --- Login Logic ---
if authentication_status is False:
    st.error("❌ Username or password is incorrect")

elif authentication_status is None:
    st.warning("⚠️ Please enter your username and password")

elif authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"✅ Welcome {name}!")

    # --- Page Setup ---
    st.set_page_config(page_title="📊 Insurance Dashboard", layout="wide")
    st.title("📈 Insurance Metrics Dashboard")

    # --- Google Sheet Access via Service Account ---
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    SERVICE_ACCOUNT_FILE = r'C:\Users\Mohit Khushlani\Downloads\endorsement-automation-6ace044178c9.json'

    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=scopes
    )

    gc = gspread.authorize(credentials)

    # --- Spreadsheet Info ---
    spreadsheet_key = "1MBI2PXlrVXIeeLFUyfNDCiuUG_-Lnm0PdMgxzg_kmcg"
    book = gc.open_by_key(spreadsheet_key)

    # --- Load Sheets as DataFrames ---
    @st.cache_data
    def load_data():
        df_daily = pd.DataFrame(book.worksheet("Daily").get_all_records())
        df_periods = pd.DataFrame(book.worksheet("Periods").get_all_records())
        return df_daily, df_periods

    df_daily, df_periods = load_data()

    # --- Dashboard Tabs ---
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
