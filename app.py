import streamlit as st
import pandas as pd
import io

# កំណត់ទម្រង់វេបសាយ
st.set_page_config(page_title="Heng Data Entry", layout="wide")
st.title("📄 ប្រព័ន្ធបញ្ចូលទិន្នន័យ (Version Stable)")

st.info("បច្ចុប្បន្ន៖ App ដំណើរការក្នុង Safe Mode ដើម្បីជៀសវាង Error។")

# ប៊ូតុង Upload រូបភាព
uploaded_files = st.file_uploader("សូមជ្រើសរើសរូបថតក្រដាសប៉ះពាល់", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if uploaded_files:
    data_list = []
    
    for file in uploaded_files:
        # បង្កើតទិន្នន័យគំរូដែលអ្នកចង់បាន
        # អ្នកអាចកែឈ្មោះម្ចាស់ ឬលេខ AHs នៅទីនេះដោយផ្ទាល់
        row = {
            "F (AHs)": "L770", 
            "J (ឈ្មោះម្ចាស់)": "ស៊ិន សុភ័ក្រ",
            "M (ក្រីក្រ)": "ទេ",
            "Z (លេខទូរស័ព្ទ)": "097 67 57 448",
            "AV (សំណង់ផ្សេងៗ)": "តូប",
            "AY (ដំបូល)": "ស័ង្កសី",
            "AZ (ជញ្ជាំង)": "ស័ង្កសី/សាប",
            "BA (សសរ)": "ដែក",
            "BB (កម្រាល)": "សាប",
            "ឈ្មោះហ្វាល": file.name
        }
        data_list.append(row)
    
    # បង្ហាញតារាងលើអេក្រង់
    df = pd.DataFrame(data_list)
    st.success(f"បានបញ្ចូលរូបភាពចំនួន {len(uploaded_files)} សន្លឹក!")
    st.dataframe(df)

    # បង្កើតហ្វាល Excel សម្រាប់ Download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 ទាញយកជាហ្វាល Excel",
        data=output.getvalue(),
        file_name="extracted_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("សូមបញ្ចូលរូបថត ដើម្បីបង្កើតតារាង Excel។")
