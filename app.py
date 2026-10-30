import io
import re
import zipfile
from datetime import datetime, timedelta
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Leave Application Form", page_icon="📄", layout="centered")

st.title("📄 Leave Application Form")
st.write("Fill in the details below to generate and share your leave application.")

# ==========================================
# 1. Form Inputs
# ==========================================
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

# Half-Day & Total Days input
total_days = st.number_input(
    "Total Leave Days", min_value=0.5, value=1.0, step=0.5
)

# Common reason selector
common_reasons = ["Personal Matters", "Family Vacation", "Medical / Doctor Appointment", "Urgent Household Matter", "Custom..."]
selected_reason = st.selectbox("Reason of Leave", common_reasons)
if selected_reason == "Custom...":
    reason = st.text_input("Specify Reason", placeholder="Enter your reason...")
else:
    reason = selected_reason

# Half-day annotation
if total_days % 1 != 0:
    reason_final = f"{reason} (Half Day)"
else:
    reason_final = reason

# Calculate Period To date
date_str = todays_date_input.strftime("%d-%m-%y")
start_date_str = period_from_input.strftime("%d-%m-%y")

start_date = datetime.strptime(start_date_str, "%d-%m-%y")
if total_days <= 0.5:
    end_date_str = start_date_str
else:
    end_date = start_date + timedelta(days=int(total_days) - 1)
    end_date_str = end_date.strftime("%d-%m-%y")

# ==========================================
# 2. In-App Summary Preview
# ==========================================
st.markdown("---")
st.subheader("🔍 Leave Application Summary")
st.info(f"""
* **Today's Date:** {date_str}
* **Type of Leave:** {leave_type}
* **Period:** {start_date_str} **to** {end_date_str}
* **Total Days:** {total_days} Day(s)
* **Reason:** {reason_final}
""")

# ==========================================
# 3. File Generation Logic
# ==========================================
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

def generate_excel_bytes():
    template_path = "Leave_application.xlsx"
    target_keywords = LEAVE_KEYWORD_MAP.get(leave_type, [leave_type.lower()])

    out_buffer = io.BytesIO()
    with zipfile.ZipFile(template_path, "r") as src, zipfile.ZipFile(
        out_buffer, "w"
    ) as dst:
        for item in src.infolist():
            data = src.read(item.filename)

            # 1. Update cell values in sheet1.xml
            if item.filename == "xl/worksheets/sheet1.xml":
                xml_str = data.decode("utf-8")
                xml_str = re.sub(
                    r'<c r="G14"[^>]*>(.*?)</c>',
                    f'<c r="G14" s="25" t="inlineStr"><is><t>Date: {date_str}</t></is></c>',
                    xml_str,
                )
                xml_str = re.sub(
                    r'<c r="A18"[^>]*/>',
                    f'<c r="A18" s="5" t="inlineStr"><is><t>{start_date_str}</t></is></c>',
                    xml_str,
                )
                xml_str = re.sub(
                    r'<c r="B18"[^>]*/>',
                    f'<c r="B18" s="5" t="inlineStr"><is><t>{end_date_str}</t></is></c>',
                    xml_str,
                )
                xml_str = re.sub(
                    r'<c r="C18"[^>]*/>',
                    f'<c r="C18" s="19" t="inlineStr"><is><t>{reason_final}</t></is></c>',
                    xml_str,
                )
                xml_str = re.sub(
                    r'<c r="H18"[^>]*/>',
                    f'<c r="H18" s="6"><v>{total_days}</v></c>',
                    xml_str,
                )
                xml_str = re.sub(
                    r'<c r="H28"[^>]*>.*?</c>',
                    f'<c r="H28" s="35"><f>SUM(H18:H27)</f><v>{total_days}</v></c>',
                    xml_str,
                )
                data = xml_str.encode("utf-8")

            # 2. Update Form Control Properties
            elif item.filename in CTRL_PROP_MAP:
                prop_keywords = CTRL_PROP_MAP[item.filename]
                is_selected = any(kw in target_keywords for kw in prop_keywords) or any(
                    kw in leave_type.lower() for kw in prop_keywords
                )

                ctrl_xml = data.decode("utf-8")
                ctrl_xml = re.sub(r'\s*checked="Checked"', '', ctrl_xml)
                if is_selected:
                    ctrl_xml = ctrl_xml.
