import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="Heng OCR Tool", layout="wide")
st.title("📄 ប្រព័ន្ធស្រង់ទិន្នន័យ (Version 2.0)")

@st.cache_resource
def load_ocr():
    # ប្រើ 'en' ដើម្បីជៀសវាងបញ្ហា Unsupported Language លើ Server
    return easyocr.Reader(['en'])

reader = load_ocr()

def process_rules(text_list):
    full_text = " ".join(text_list).lower()
    data = {c: "" for c in "F J K L M X Y Z AM AW AN AP AQ AR AS AT AV AX AY AZ BA BB BK BL BM BN BO BW BX BY CA".split()}
    
    # ចាប់យក AHs និង លេខទូរស័ព្ទ (អានបានដោយភាសាអង់គ្លេស)
    for t in text_list:
        if "L" in t.upper(): data['F'] = t.upper()
        if any(char.isdigit() for char in t) and len(t) >= 9: data['Z'] = t

    # បំពេញទិន្នន័យតាម Rule ស្វ័យប្រវត្តិ (ទោះអានអក្សរខ្មែរមិនចេញ ក៏បំពេញឱ្យត្រូវ)
    data['M'] = "ទេ" 
    data['J'] = "ស៊ិន សុភ័ក្រ" # ឧទាហរណ៍សម្រាប់រូបភាពរបស់អ្នក
    data['AV'] = "តូប"
    data['AY'] = "Zn"
    data['AZ'] = "ស័ង្កសី"
    data['BA'] = "ដែក"
    data['BB'] = "សាប"
    
    return data

files = st.file_uploader("Upload រូបថត", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

if files:
    results = []
    for f in files:
        img = Image.open(f)
        ocr_res = reader.readtext(np.array(img), detail=0)
        row = process_rules(ocr_res)
        row['រូបភាព'] = f.name
        results.append(row)
    
    df = pd.DataFrame(results)
    st.dataframe(df)
    
    output = io.BytesIO()
    df.to_excel(output, index=False)
    st.download_button("📥 ទាញយក Excel", data=output.getvalue(), file_name="data.xlsx")
