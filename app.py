import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Heng Data Entry", layout="wide")

st.title("📋 ប្រព័ន្ធបញ្ចូលទិន្នន័យផលប៉ះពាល់ (Heng System)")
st.markdown("---")

# បង្កើត Form សម្រាប់បញ្ចូលទិន្នន័យ
with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        ahs_code = st.text_input("F (លេខ AHs):", placeholder="ឧទាហរណ៍: L770")
        owner_name = st.text_input("J (ឈ្មោះម្ចាស់):", placeholder="ឧទាហរណ៍: ស៊ិន សុភ័ក្រ")
        phone = st.text_input("Z (លេខទូរស័ព្ទ):", placeholder="097xxxxxxx")
        poverty_card = st.selectbox("M (ប័ណ្ណក្រីក្រ):", ["ទេ", "មាន"])

    with col2:
        structure = st.selectbox("AV (ប្រភេទសំណង់):", ["តូប", "ផ្ទះ", "រោង", "របង", "ក្ងោក", "ដើមឈើ"])
        roof = st.selectbox("AY (ដំបូល):", ["ស័ង្កសី", "ក្បឿង", "ស្បូវ", "បេតុង"], index=0)
        wall = st.selectbox("AZ (ជញ្ជាំង):", ["ស័ង្កសី", "សុីម៉ង់ត៍", "ឈើ", "សាប"], index=0)
        column = st.selectbox("BA (សសរ):", ["ដែក", "ថ្ម", "ឈើ"], index=0)
        floor = st.selectbox("BB (កម្រាល):", ["សាប", "ការ៉ូ", "ដី"], index=0)

    photo = st.file_uploader("📸 ថតរូប ឬ Upload ក្រដាស", type=['jpg', 'jpeg', 'png'])
    
    submit = st.form_submit_button("➕ បញ្ចូលទៅក្នុងតារាង")

# បង្កើតកន្លែងផ្ទុកទិន្នន័យបណ្ដោះអាសន្ន (Session State)
if 'data_storage' not in st.session_state:
    st.session_state.data_storage = []

if submit:
    new_entry = {
        "F": ahs_code, "J": owner_name, "Z": phone, "M": poverty_card,
        "AV": structure, "AY": roof, "AZ": wall, "BA": column, "BB": floor,
        "កាលបរិច្ឆេទ": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "រូបភាព": photo.name if photo else "គ្មានរូបភាព"
    }
    st.session_state.data_storage.append(new_entry)
    st.success("✅ បានរក្សាទុកទិន្នន័យម្ចាស់ឈ្មោះ: " + owner_name)

# បង្ហាញតារាង និងប៊ូតុងទាញយក
if st.session_state.data_storage:
    st.markdown("### 📊 តារាងទិន្នន័យដែលបានបញ្ចូល")
    df = pd.DataFrame(st.session_state.data_storage)
    st.dataframe(df)

    # ប៊ូតុងទាញយក Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 ទាញយកជាហ្វាល Excel (.xlsx)",
        data=output.getvalue(),
        file_name=f"Heng_Data_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("🗑 លុបតារាងចោល (Clear All)"):
        st.session_state.data_storage = []
        st.rerun()
