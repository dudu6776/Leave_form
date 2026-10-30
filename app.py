import io
import re
import zipfile
from datetime import datetime, timedelta
import streamlit as st

st.set_page_config(page_title="Leave Application Form", page_icon="📄")

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

date_input = st.date_input("Date / Period From", datetime.now())
reason = st.text_input("Reason of Leave", placeholder="e.g. Personal Matters")
total_days = st.number_input(
    "Total Leave Days", min_value=1.0, value=1.0, step=0.5
)

# Robust keyword mapping for checkbox shapes
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

if st.button("Generate Leave Form", type="primary"):
    date_str = date_input.strftime("%d-%m-%y")
    start_date = datetime.strptime(date_str, "%d-%m-%y")
    end_date = start_date + timedelta(days=int(total_days) - 1)
    end_date_str = end_date.strftime("%d-%m-%y")

    template_path = "Leave_application.xlsx"
    output_filename = f"{date_str.replace('/', '-')}.xlsx"

    # Zip modification logic to preserve shapes, drawings, and images
    out_buffer = io.BytesIO()
    with zipfile.ZipFile(template_path, "r") as src, zipfile.ZipFile(
        out_buffer, "w"
    ) as dst:
        for item in src.infolist():
            data = src.read(item.filename)

            # Update cell values in sheet1.xml
            if item.filename == "xl/worksheets/sheet1.xml":
                xml_str = data.decode("utf-8")
                xml_str = re.sub(
                    r'<c r="G14"[^>]*>(.*?)</c>',
                    f'<c r="G14" s="25" t="inlineStr"><is><t>Date: {date_str}</t></is></c>',
                    xml_str,
                )
                xml_str = re.sub(
                    r'<c r="A18"[^>]*/>',
                    f'<c r="A18" s="5" t="inlineStr"><is><t>{date_str}</t></is></c>',
                    xml_str,
                )
                xml_str = re.sub(
                    r'<c r="B18"[^>]*/>',
                    f'<c r="B18" s="5" t="inlineStr"><is><t>{end_date_str}</t></is></c>',
                    xml_str,
                )
                xml_str = re.sub(
                    r'<c r="C18"[^>]*/>',
                    f'<c r="C18" s="19" t="inlineStr"><is><t>{reason}</t></is></c>',
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

            # Update VML checkbox layer
            elif item.filename == "xl/drawings/vmlDrawing1.vml":
                vml_text = data.decode("utf-8")

                # Uncheck all existing checkboxes first
                vml_text = re.sub(
                    r"<x:Checked>1</x:Checked>", "<x:Checked>0</x:Checked>", vml_text
                )

                # Find all shape blocks in VML
                shapes = re.findall(
                    r"(<v:shape.*?</v:shape>)", vml_text, re.DOTALL
                )
                target_keywords = LEAVE_KEYWORD_MAP.get(
                    leave_type, [leave_type.lower()]
                )

                for shape in shapes:
                    if 'ObjectType="Checkbox"' in shape:
                        # Strip HTML tags and normalize extra whitespace for reliable matching
                        cleaned_text = re.sub(
                            r"\s+", " ", re.sub(r"<[^>]+>", " ", shape)
                        ).lower()

                        if any(kw in cleaned_text for kw in target_keywords):
                            new_shape = re.sub(
                                r'<x:ClientData ObjectType="Checkbox">(.*?)</x:ClientData>',
                                r'<x:ClientData ObjectType="Checkbox">\g<1><x:Checked>1</x:Checked></x:ClientData>',
                                shape,
                                flags=re.DOTALL,
                            )
                            vml_text = vml_text.replace(shape, new_shape)
                            break

                data = vml_text.encode("utf-8")

            dst.writestr(item, data)

    st.success("Form generated successfully!")
    st.download_button(
        label="📥 Download Excel Form",
        data=out_buffer.getvalue(),
        file_name=output_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
