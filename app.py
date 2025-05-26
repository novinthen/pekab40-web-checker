
import streamlit as st
import pandas as pd
from playwright.sync_api import sync_playwright
import time
import tempfile
import os

st.set_page_config(page_title="IC Eligibility Checker (PEKAB40)", layout="centered")

st.title("PEKAB40 IC Eligibility Checker")
st.write("Upload an Excel file with a column named 'IC'. This tool will check eligibility using https://kelayakan.pekab40.com.my")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if 'IC' not in df.columns:
        st.error("The Excel file must contain a column named 'IC'")
    else:
        results = []

        with st.spinner("Checking eligibility, please wait..."):
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                for index, row in df.iterrows():
                    ic = str(row['IC'])
                    try:
                        page.goto("https://kelayakan.pekab40.com.my/semakan-kelayakan", timeout=30000)
                        page.fill("#nokp", ic)
                        page.click("#btnSemak")
                        page.wait_for_timeout(3000)
                        status = page.locator("#status").inner_text()
                    except Exception:
                        status = "Error"
                    results.append(status)
                    time.sleep(1.5)

                browser.close()

        df["Eligibility Status"] = results

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            output_path = tmp.name
            df.to_excel(output_path, index=False)
            st.success("Eligibility check complete!")
            st.download_button(label="Download Results Excel",
                               data=open(output_path, 'rb').read(),
                               file_name="eligibility_results.xlsx")
