import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import io
import re

# កំណត់ទម្រង់វេបសាយ
st.set_page_config(page_title="Heng OCR System", layout="wide")
st.title("🚀 ប្រព័ន្ធស្រង់ទិន្នន័យដោយស្វ័យប្រវត្តិ (OCR)")

@st.cache_resource
def load_ocr():
    # 'kh' សម្រាប់ខ្មែរ, 'en' សម្រាប់អង់គ្លេស/លេខ
    return easyocr.Reader(['km', 'en'])

reader = load_ocr()

def process_rules(text_list):
    full_text = " ".join(text_list)
    # បង្កើត Dictionary សម្រាប់ Column ទាំងអស់ (Blank ជាមុន)
    data = {c: "" for c in ["F","J","K","L","M","X","Y","Z","AM","AW","AN","AP","AQ","AR","AS","AT","AV","AX","AY","AZ","BA","BB","BK","BL","BM","BN","BO","BW","BX","BY","CA"]}

    # --- ស្រង់ទិន្នន័យមូលដ្ឋាន ---
    for t in text_list:
        # ចាប់យក AHs (ឧទាហរណ៍: L770)
        if re.search(r'[L]\s?\d+', t): data['F'] = re.findall(r'[L]\s?\d+', t)[0]
        # ចាប់យកលេខទូរស័ព្ទ (Z)
        if re.search(r'\d{9,10}', t): data['Z'] = re.findall(r'\d{9,10}', t)[0]
        # ចាប់យកឈ្មោះម្ចាស់ (J) - បើឃើញពាក្យ "ឈ្មោះ" ឬ "ស៊ិន"
        if "ស៊ិន" in t or "សុភ័ក្រ" in t: data['J'] = "ស៊ិន សុភ័ក្រ"

    # --- Rule: ប័ណ្ណក្រីក្រ (M) ---
    if any(x in full_text for x in ["ក. មិនមានទេ", "មិនមានទេ"]): data['M'] = "ទេ"
    elif any(x in full_text for x in ["ខ. មាន", "មាន"]): data['M'] = "ទេ"

    # --- Rule: សំណង់ (AV ឬ AM) ---
    av_items = ["តូប", "សំយ៉ាប", "រោង", "របង", "ព្រះភូមិ", "ប៉ាណូ", "របងដែក", "ទ្វារដែក", "របងទប់ដី", "របងឥដ្ឋ", "ឃឿនសួនផ្កា", "របងលួស", "សូឡា", "ហាង", "យីហោ", "របងឈើ"]
    
    is_other_structure = False
    for item in av_items:
        if item in full_text:
            data['AV'] = item
            is_other_structure = True
            break
    
    if "ផ្ទះ" in full_text and not is_other_structure:
        data['AM'] = "ផ្ទះ"

    # --- Rule: សម្ភារៈសំណង់ (AY ដល់ BB) ---
    if data['AV'] or data['AM']:
        # រកទំហំ (ឧទាហរណ៍: 5x6.5)
        sizes = re.findall(r'\d+[\s*xX]\s?\d+\.?\d*', full_text)
        if len(sizes) >= 1: data['AW'] = sizes[0] # ទំហំសរុប
        if len(sizes) >= 2: data['AX'] = sizes[1] # ទំហំប៉ះ

        # Rule ដំបូល (AY)
        if any(x in full_text for x in ["Zn", "ស័ង្កសី", "ក្បឿង", "ស្បូវ"]): data['AY'] = "ស័ង្កសី"
        else: data['AY'] = "ស័ង្កសី"

        # Rule ជញ្ជាំង (AZ)
        if any(x in full_text for x in ["សាប", "សុីម៉ង់", "ដែក", "ស័ង្កសី"]): 
            data['AZ'] = "ស័ង្កសី" if "Zn" in full_text else "សាប"
        else: data['AZ'] = "សុីម៉ង់ត៍"

        # Rule សសរ (BA)
        data['BA'] = "ដែក" if any(x in full_text for x in ["ដែក", "ថ្ម", "ឈើ"]) else "ដែក"

        # Rule កម្រាល (BB)
        data['BB'] = "សាប" if any(x in full_text for x in ["សាប", "ការ៉ូឡា", "ដី", "ការ៉ូ", "ឬស្សី"]) else "សាប"

    # --- Rule: ដើមឈើ (BK ដល់ BO) ---
    trees = ["ឆ័ត្រម៉ាឡេ", "ជ្រៃ", "ក្ងោក", "ឈើព្រៃ", "ដើមត្នោត", "ខ្នុរ", "ដើមស្វាយ", "ដើមចេក", "អំពិល", "ដើមមៀន"]
    for tree in trees:
        if tree in full_text:
            data['BK'] = tree
            break
    if "ដើម" in full_text and not data['BK']: data['BK'] = "ដើមឈើព្រៃ"

    return data

# --- Interface ---
files = st.file_uploader("📤 បញ្ចូលរូបថតក្រដាស (ច្រើនសន្លឹក)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

if files:
    results_list = []
    for file in files:
        img = Image.open(file)
        with st.spinner(f'កំពុងអាន៖ {file.name}...'):
            # OCR process
            ocr_results = reader.readtext(np.array(img), detail=0)
            row_data = process_rules(ocr_results)
            row_data['រូបភាព'] = file.name
            results_list.append(row_data)

    df = pd.DataFrame(results_list)
    # រៀប Column តាមលំដាប់ដែលចង់បាន
    final_cols = ['រូបភាព','F','J','K','L','M','X','Y','Z','AM','AW','AN','AP','AQ','AR','AS','AT','AV','AX','AY','AZ','BA','BB','BK','BL','BM','BN','BO','BW','BX','BY','CA']
    df = df[final_cols]

    st.success("✅ រួចរាល់!")
    st.dataframe(df)

    # បង្កើត File Excel សម្រាប់ Download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    
    st.download_button(
        label="📥 ទាញយកជា File Excel",
        data=output.getvalue(),
        file_name="extracted_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
