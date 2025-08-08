import streamlit as st
import pandas as pd
import gspread
import yaml
from google.oauth2.service_account import Credentials
import streamlit_authenticator as stauth

# --- Load secrets ---
gcp_secrets = st.secrets["gcp_service_account"]
credentials = Credentials.from_service_account_info(
    json.loads(gcp_secrets),
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"],
)

gc = gspread.authorize(credentials)

# --- Authentication config ---
config = yaml.safe_load(st.secrets["auth_config"])
authenticator = stauth.Authenticate(
    config,
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

name, authentication_status, username = authenticator.login(
    form_name="Login",
    location="main"
)
