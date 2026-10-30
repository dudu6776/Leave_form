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
            <tr style="background-color:#0078D4; color:white; text-align:center;">
                <th>From</th>
                <th>To</th>
            </tr>
        </thead>
        <tbody>
            <tr style="text-align:center;">
                <td>{start_date_str}</td>
                <td>{end_date_str}</td>
                <td style="text-align:left;">{reason_final}</td>
                <td><b>{total_days}</b></td>
            </tr>
        </tbody>
    </table>
</div>
"""
st.markdown(preview_html, unsafe_allow_html=True)
st.markdown("")

# Mapping of Form Control XML property files to leave keywords
CTRL_PROP_MAP = {
    "xl/ctrlProps/ctrlProp1.xml": ["adoption leave", "adoption"],
    "xl/ctrlProps/ctrlProp2.xml": ["paternity", "maternity", "p/m-l"],
    "xl/ctrlProps/ctrlProp3.xml": ["shared parental", "spl"],
    "xl/ctrlProps/ctrlProp4.xml": ["others"],
    "xl/ctrlProps/ctrlProp5.xml": ["personal leave", "(pl)"],
    "xl/ctrlProps/ctrlProp6.xml": ["childcare leave", "(cl)"],
    "xl/ctrlProps/ctrlProp7.xml": ["annual leave", "(al)"],
    "xl/ctrlProps/ctrlProp8.xml": ["unpaid leave", "(ul)"],
    "xl/ctrlProps/ctrlProp9.xml": ["off day", "(od)"],
}

LEAVE_KEYWORD_MAP = {
    "Annual Leave (AL)": ["annual leave", "(al)"],
    "Personal Leave (PL)": ["personal leave", "(pl)"],
    "Childcare Leave (CL)": ["childcare leave", "(cl)"],
    "Unpaid Leave (UL)": ["unpaid leave", "(ul)"],
    "Off Day (OD)": ["off day", "(od)"],
    "Adoption Leave": ["adoption leave", "adoption"],
    "Paternity/Maternity Leave (P/M-L)": ["paternity", "maternity", "p/m-l"],
    "Shared Parental Leave (SPL)": ["shared parental", "(spl)"],
    "Others: Please specify": ["others"],
}

if st.button("Generate Leave Form", type="primary", use_container_width=True):
    template_path = "Leave_application.xlsx"
    output_filename = f"Leave_Application_{today_date_str.replace('/', '-')}.xlsx"

    target_keywords = LEAVE_KEYWORD_MAP.get(
        leave_type, [leave_type.lower()]
    )

    out_buffer = io.BytesIO()
    with zipfile.ZipFile(template_path, "r") as src, zipfile.ZipFile(
        out_buffer, "w"
    ) as dst:
        for item in src.infolist():
            data = src.read(item.filename)

            # 1. Update cell values in sheet1.xml
            if item.filename == "xl/worksheets/sheet1.xml":
                xml_str = data.decode("utf-8")
                
                # G14 uses Today's Date
                xml_str = re.sub(
                    r'<c r="G14"[^>]*>(.*?)</c>',
                    f'<c r="G14" s="25" t="inlineStr"><is><t>Date: {today_date_str}</t></is></c>',
                    xml_str,
                )
                # A18 uses Period From
                xml_str = re.sub(
                    r'<c r="A18"[^>]*/>',
                    f'<c r
