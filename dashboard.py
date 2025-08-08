import streamlit as st
import pandas as pd
import gspread
import streamlit_authenticator as stauth
from google.oauth2.service_account import Credentials

# --- Load login credentials from Streamlit Secrets ---
config = {
    'usernames': {
        'mohit': {
            'name': st.secrets["auth_config"]["usernames.mohit.name"],
            'password': st.secrets["auth_config"]["usernames.mohit.password"]
        },
        'adil': {
            'name': st.secrets["auth_config"]["usernames.adil.name"],
            'password': st.secrets["auth_config"]["usernames.adil.password"]
        }
    },
    'cookie': {
        'name': st.secrets["auth_config"]["cookie.name"],
        'key': st.secrets["auth_config"]["cookie.key"],
        'expiry_days': int(st.secrets["auth_config"]["cookie.expiry_days"])
    },
    'preauthorized': {
        'emails': []
    }
}

# --- Authenticator setup ---
authenticator = stauth.Authenticate(
    config,
    config['cookie']['name'],
    config['cookie']['key']
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status is False:
    st.error("❌ Incorrect username or password")
elif authentication_status is None:
    st.warning("⚠️ Please enter your login credentials")
elif authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome {name} 👋")

    # --- Page setup ---
    st.set_page_config(page_title="📊 Insurance Dashboard", layout="wide")
    st.title("📈 Insurance Metrics Dashboard")

    # --- Google Sheet Access via Secrets ---
    creds_dict = st.secrets["gcp_service_account"]
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(credentials)

    spreadsheet_key = "1MBI2PXlrVXIeeLFUyfNDCiuUG_-Lnm0PdMgxzg_kmcg"
    book = gc.open_by_key(spreadsheet_key)

    @st.cache_data
    def load_data():
        df_daily = pd.DataFrame(book.worksheet("Daily").get_all_records())
        df_periods = pd.DataFrame(book.worksheet("Periods").get_all_records())
        return df_daily, df_periods

    df_daily, df_periods = load_data()

    # --- Tabs ---
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
