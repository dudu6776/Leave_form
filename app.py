import io
import re
import zipfile
from datetime import datetime, timedelta
import streamlit as st

st.set_page_config(page_title="Leave Application Form", page_icon="📄", layout="centered")

st.title("📄 Leave Application Form")
st.write("Fill in the details below to generate your completed leave application.")

# Form inputs
leave_type = st.selectbox(
    "Type of Leave",
    [
        "Annual Leave (AL)",
        "Personal Leave (PL)",
        "Childcare Leave (CL)",
        "Unpaid Leave (UL)",
        "Off Day (OD)",
        "Adoption Leave",
        "Paternity/Maternity Leave (P/M-L)",
        "Shared Parental Leave (SPL)",
        "Others: Please specify",
    ],
)

col1, col2 = st.columns(2)
with col1:
    todays_date_input = st.date_input("Today's Date", datetime.now())
with col2:
    period_from_input = st.date_input("Period From", datetime.now())

# 0.5 Day (Half Day) Leave support
total_days = st.number_input(
    "Total Leave Days", min_value=0.5, value=1.0, step=0.5
)

reason = st.text_input("Reason of Leave", placeholder="e.g. Personal Matters")

# Append half-day tag if applicable
if total_days == 0.5 or total_days % 1 != 0:
    reason_final = f"{reason} (Half Day)" if reason else "(Half Day)"
else:
    reason_final = reason

# Date formatting & calculation
today_date_str = todays_date_input.strftime("%d-%m-%y")
start_date_str = period_from_input.strftime("%d-%m-%y")

start_date = datetime.strptime(start_date_str, "%d-%m-%y")
if total_days <= 0.5:
    end_date_str = start_date_str
else:
    end_date = start_date + timedelta(days=int(total_days) - 1)
    end_date_str = end_date.strftime("%d-%m-%y")

# ==========================================
# In-App Live Preview Section
# ==========================================
st.markdown("---")
st.subheader("👁️ Live Form Preview")

preview_html = f"""
<div style="border:2px solid #0078D4; border-radius:10px; padding:18px; background-color:#FAFAFA; color:#222; font-family:sans-serif;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; color:#0078D4;">Leave Application Form</h3>
        <span style="font-weight:bold;">Date: {today_date_str}</span>
    </div>
    <hr style="margin:12px 0; border:0; border-top:1px solid #CCC;" />
    <p style="font-size:15px; margin-bottom:12px;"><b>Selected Leave Type:</b> {leave_type}</p>
    <table style="width:100%; border-collapse:collapse; background-color:#FFF; font-size:14px;" border="1" cellpadding="8">
        <thead>
            <tr style="background-color:#0078D4; color:white; text-align:center;">
                <th colspan="2">Period</th>
                <th rowspan="2">Reason of Leave</th>
                <th rowspan="2">Total Leave Days</th>
            </tr>
            <tr style="background-color:#0078D4; color:white; text
