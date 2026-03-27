import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import io
import time

# បញ្ជាក់៖ យើងប្រកាស import easyocr នៅក្នុង Function វិញដើម្បីកុំឱ្យគាំង Server ពេលបើកដំបូង
def get_reader():
    import easyocr
    return easyocr.Reader(['en']) # ប្រើ en ដើម្បីអានលេខ និងកូដ AHs ឱ្យបានលឿន

st.set_page_config(page_title="Heng OCR System", layout="wide")
st.title("🚀 ប្រព័ន្ធស្កេន និងស្រង់ទិន្នន័យក្រដាសប៉ះពាល់")

# បង្កើត Sidebar សម្រាប់កំណត់ Rule
with st.sidebar:
    st.header("⚙️ ការកំណត់ (Rules)")
    default_owner = st.text_input("ឈ្មោះម្ចាស់ (បើរកមិនឃើញ):", "ស៊ិន សុភ័ក្រ")
    default_structure = st.selectbox("ប្រភេទសំណង់:", ["តូប", "ផ្ទះ", "រោង", "របង"])

uploaded_files = st.file_uploader("📤 បញ្ចូលរូបថតក្រដាស (អាចដាក់ច្រើនសន្លឹក)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if uploaded_files:
    # ប៊ូតុងចាប់ផ្ដើមស្កេន
    if st.button("🔍 ចាប់ផ្ដើមស្កេនទិន្នន័យ"):
        reader = get_reader()
        all_results = []
        
        progress_bar = st.progress(0)
        for idx, file in enumerate(uploaded_files):
            with st.spinner(f"កំពុងអានរូបភាពទី {idx+1}..."):
                img = Image.open(file)
                # ស្កេនអក្សរ
                results = reader.readtext(np.array(img), detail=0)
                full_text = " ".join(results).upper()
                
                # បង្កើត Row ទិន្នន័យ (F ដល់ CA)
                row = {c: "" for c in "F J K L M X Y Z AM AW AN AP AQ AR AS AT AV AX AY AZ BA BB BK BL BM BN BO BW BX BY CA".split()}
                
                # --- ចាប់យកទិន្នន័យតាម Rule ---
                row['J'] = default_owner
                row['AV'] = default_structure
                row['M'] = "ទេ" # ប័ណ្ណក្រីក្រ
                
                for t in results:
                    t_up = t.upper()
                    if "L" in t_up and any(c.isdigit() for c in t_up): row['F'] = t_up # AHs
                    if any(c.isdigit() for c in t_up) and len(t_up) >= 9: row['Z'] = t_up # Phone
                
                # បំពេញសម្ភារៈសំណង់ (Default Rules)
                row['AY'] = "ស័ង្កសី"
                row['AZ'] = "ស័ង្កសី"
                row['BA'] = "ដែក"
                row['BB'] = "សាប"
                row['រូបភាព'] = file.name
                
                all_results.append(row)
                progress_bar.progress((idx + 1) / len(uploaded_files))
        
        df = pd.DataFrame(all_results)
        st.success("✅ ស្កេនរួចរាល់!")
        st.dataframe(df)

        # ប៊ូតុងទាញយក Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 ទាញយកជាហ្វាល Excel (.xlsx)", data=output.getvalue(), file_name="Heng_Data_Export.xlsx")
