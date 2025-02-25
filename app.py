import streamlit as st
import pandas as pd
import os
from PIL import Image
from io import BytesIO


st.set_page_config(page_title="💽 Data Sweeper", layout='wide')
dark_mode = st.toggle("🌙 Enable Dark Mode")
st.title("💽 Data Sweeper")
st.write("Transform your files between CSV and Excel formats within built-in data cleaning and visualiation!")

uploaded_file = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)
uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg", "bmp", "gif"], accept_multiple_files=True)




if dark_mode:
    dark_css = """
    <style>
    body { background-color: #121212; color: white; }
    .stApp { background-color: #121212; color: white; }
    .stButton>button { background-color: #333333; color: white; }
    .stDownloadButton>button { background-color: #333333; color: white; }
    .stTextInput>div>div>input { background-color: #333333; color: white; }
    .stMultiSelect>div>div>div>input { background-color: #333333; color: white; }
    </style>
    """
    st.markdown(dark_css, unsafe_allow_html=True)

if uploaded_file:
    for file in uploaded_file:
        file_extension = os.path.splitext(file.name)[1].lower()

        if file_extension == ".csv":
            df = pd.read_csv(file)
        elif file_extension == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            continue


        # Display info about teh file
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size / 1024:.2f} KB")

        # Show 5 rows of our df
        st.write("🔍Preview the Head of the Dataframe")
        st.dataframe(df.head())

        # Options for data cleaning 
        st.subheader("🛠️Data Cleaning Options")
        if st.checkbox(f"Remove Duplictaes form {file.name}"):
            col1, col2 =  st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates form {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")

            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols =df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing Values have been Filled!")

        # Choose Specific Columns to Keep or Convert 
        st.subheader("🎯 Select Columns to Convert")
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Create Some Visualizations
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include='number').iloc[:,:2])

        # Convert the File -> CSV to Excel 
        st.subheader("🔁Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer,index=False)
                file.name = file.name.replace(file_extension, ".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                df.to_excel(buffer,index=False)
                file.name = file.name.replace(file_extension, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)


            # Download Button 
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file.name,
                mime=mime_type
            )

if uploaded_files:
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)

        # Resize image preview
        preview_size = (100, 200)  # Small preview size
        img_preview = image.copy()
        img_preview.thumbnail(preview_size)

        st.image(img_preview, caption=f"Uploaded Image: {uploaded_file.name}", use_container_width=False)

        # Dropdown for format selection
        format_options = ["PNG", "JPEG", "BMP", "GIF"]
        selected_format = st.selectbox(f"Select Output Format for {uploaded_file.name}", format_options, key=uploaded_file.name)

        # Convert and Download Button
        if st.button(f"Convert {uploaded_file.name}", key=f"convert_{uploaded_file.name}"):
            img_byte_arr = BytesIO()
            
            # Convert image mode if saving as JPEG
            if selected_format == "JPEG" and image.mode == "RGBA":
                image = image.convert("RGB")
            
            image.save(img_byte_arr, format=selected_format)
            img_byte_arr = img_byte_arr.getvalue()

            st.download_button(
                label=f"Download {uploaded_file.name} as {selected_format}",
                data=img_byte_arr,
                file_name=f"{uploaded_file.name.split('.')[0]}.{selected_format.lower()}",
                mime=f"image/{selected_format.lower()}",
            )

st.success("🎉 All files processed!")
