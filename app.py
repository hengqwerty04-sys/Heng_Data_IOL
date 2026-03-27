import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="Heng Data Entry", layout="wide")
st.title("📄 កម្មវិធីស្រង់ទិន្នន័យ (Smart Scan)")

# Load OCR ដោយមិនប្រើ Cache ច្រើនពេក
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en']) # ប្រើតែ en ដើម្បីជៀសវាងបញ្ហា Unsupported Error

reader = load_ocr()

def process_image(img_file):
    img = Image.open(img_file)
    # អានអក្សរ និងលេខ
    results = reader.readtext(np.array(img), detail=0)
    full_text = " ".join(results).upper()
    
    # បង្កើតទិន្នន័យតាម Rule របស់អ្នក
    row = {c: "" for c in "F J K L M X Y Z AM AW AN AP AQ AR AS AT AV AX AY AZ BA BB BK BL BM BN BO BW BX BY CA".split()}
    
    # ស្វែងរក AHs (L770) និងលេខទូរស័ព្ទ
    for t in results:
        if "L" in t.upper(): row['F'] = t.upper()
        if any(char.isdigit() for char in t) and len(t) >= 9: row['Z'] = t

    # បំពេញ Rule ស្វ័យប្រវត្តិ
    row['M'] = "ទេ"
    row['J'] = "ស៊ិន សុភ័ក្រ"
    row['AV'] = "តូប"
    row['AY'] = "Zn"
    row['AZ'] = "ស័ង្កសី"
    row['BA'] = "ដែក"
    row['BB'] = "សាប"
    
    return row

files = st.file_uploader("Upload រូបថតក្រដាសរបស់អ្នក", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if files:
    all_data = []
    for f in files:
        with st.spinner(f'កំពុងអាន៖ {f.name}...'):
            data = process_image(f)
            data['រូបភាព'] = f.name
            all_data.append(data)
    
    df = pd.DataFrame(all_data)
    st.success("រួចរាល់!")
    st.dataframe(df)
    
    # បង្កើត File Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button("📥 ទាញយកជា Excel (.xlsx)", data=output.getvalue(), file_name="data_entry.xlsx")
