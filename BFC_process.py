import streamlit as st
import pandas as pd 
import random
from datetime import date
import datetime
from UI import * 
import plotly.express as px 
from streamlit_option_menu import option_menu 
from PIL import Image
import os
import pyexcel as p
import re
import io
import warnings
warnings.filterwarnings('ignore')

image = Image.open('bfc.png')

st.set_page_config(page_title='Dashboard', page_icon=image, layout='wide', initial_sidebar_state='auto')
UI()
st.divider()
todayDate = datetime.date.today()
randomNum=(random.randint(0,10000))
# IMAGE
st.sidebar.image(image,caption='Nam:0983658980',use_column_width=True)

# HIDE STREAMLIT
hide_style ='''
            <style>
               #MainMenu {visibility:hidden}
               footer {visibility:hidden}
               header {visibility:hidden}
            </style>
            '''
st.markdown(hide_style,unsafe_allow_html=True)

@st.cache_resource
# process file
# Function to process the uploaded file and return a DataFrame
def process_file(file):
    try:
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        elif file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            st.error("Invalid file type. Expected CSV or XLSX file.")
            return None
        return df
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None
    

def process_import_file(file):
    file_type = None
    try:
        # Convert file to dataframe
        if file.name.endswith('.xlsx'):
            xls = pd.ExcelFile(file)
            if len(xls.sheet_names) == 1:
                sheet_name = xls.sheet_names[0]
            else:
                sheet_name = 'Sheet1'  # Use 'Sheet1' as the default if there are multiple sheets
            df = pd.read_excel(file, sheet_name=sheet_name, header=1)
            df.drop(['Unnamed: 5', 'Unnamed: 6', 'Unnamed: 8', '出口国家代码'], axis=1, inplace=True) # FOR IMPORT ONLY
            # ADD 'TYPE' COLUMN 
            df.insert(6, 'Loại', '')      # IMPORT            
            file_type = 'xlsx'

        elif file.name.endswith('.csv'):
            df = pd.read_csv(file, sheet_name='Sheet1', header=1)
            df.drop(['Unnamed: 5', 'Unnamed: 6', 'Unnamed: 8', '出口国家代码'], axis=1, inplace=True) # FOR IMPORT ONLY
            # ADD 'TYPE' COLUMN 
            df.insert(6, 'Loại', '')      # IMPORT
            file_type = 'csv'
        else:
            st.error("Invalid file type. Expected CSV or XLSX file.")
            return 'Please upload the file', 'Please upload the file'
        return df, file_type
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None, None


def process_export_file(file):
    file_type = None
    try:
        # Convert file to dataframe
        if file.name.endswith('.xlsx'):
            xls = pd.ExcelFile(file)
            if len(xls.sheet_names) == 1:
                sheet_name = xls.sheet_names[0]
            else:
                sheet_name = 'Sheet1'  # Use 'Sheet1' as the default if there are multiple sheets
            df = pd.read_excel(file, sheet_name=sheet_name, header=1)
            df.insert(8, 'Loại', '')      # EXPORT
            file_type = 'xlsx'

        elif file.name.endswith('.csv'):
            df = pd.read_csv(file, sheet_name='Sheet1', header=1)
            df.insert(8, 'Loại', '')      # EXPORT
            file_type = 'csv'
        else:
            st.error("Invalid file type. Expected CSV or XLSX file.")
            return 'Please upload the file', 'Please upload the file'
        return df, file_type
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None, None

    
def convert_df(df):
    # Create a writable file-like object in memory
    excel_buffer = io.BytesIO()
    # Save the DataFrame to the file-like object
    df.to_excel(excel_buffer, index=False)
    # Reset the buffer's position to the start for reading
    excel_buffer.seek(0)
    # Return the bytes of the Excel file
    return excel_buffer.getvalue()

# convert files
def convert_xls_to_xlsx(file_path):
    # Get the filename and extension
    filename, ext = os.path.splitext(file_path)
    # Create the new file name with .xlsx extension
    new_file_path = f"{filename}.xlsx"
    # Convert the .xls file to .xlsx using pyexcel
    p.save_book_as(file_name=file_path, dest_file_name=new_file_path)

# top analytics
def Analytics():
   total_record = (df['Miêu_tả_sản_phẩm'].count())
   all_price_ = float(df['Đơn_giá'].sum())
   all_total = float(df['Hoá_đơn'].sum())

   total1,total2,total3= st.columns(3,gap='small')
   with total1:
      st.info('Total Record', icon="🔍")
      st.metric(label = 'BFC', value= f"{total_record}")
      y_col = st.selectbox('Select y column', options=df.columns[3:], key='y_col1')
      st.info(f'{y_col} by each month', icon="🔍")
      fig1 = px.line(df, x=df['Month'], y=y_col)
      fig1.update_layout(width=300)
      st.plotly_chart(fig1)
   with total2:
      st.info('Selling Price', icon="🔍")
      st.metric(label='BFC', value=f"{all_price_:,.0f}")
      options = [col for col in df.columns if col != 'Unnamed: 0']
      value = st.selectbox('Select value column', options=options, key='value')
      name  = st.selectbox('Select name column', options=options, key='name')
      st.info(f'Relationship between {value} and {name}', icon="🔍")
      fig2 = px.pie(df, values=value, names=name)
      fig2.update_layout(width=300)
      st.plotly_chart(fig2)
   with total3:
      st.info('Expected Profit', icon="🔍")
      st.metric(label= 'BFC',value=f"{all_total:,.0f}")
    # options = ['Cty_nhập', 'Cty_nhập(TA)', 'Mã_số_thuế', 'Nhà_cung_cấp', 'Xuất_xứ', 'HScode', 'Đơn_vị', 'Thành_tiền', 'Đơn_giá']
      string_columns = df.select_dtypes(include=['object']).columns.tolist()
      y_col = st.selectbox('Select y column', options=string_columns, key='y_col3')
      st.info(f'{y_col} by each month', icon="🔍")
      try:
         fig3 = px.scatter(df, x=df['Month'], y=y_col, size=df['Số_lượng'])
         fig3.update_layout(width=300)
         st.plotly_chart(fig3)
      except ValueError:
         y_col = st.selectbox('Select y column (updated)', options=options[1:], key='y_col3.2')
         fig3 = px.scatter(df, x=df['Month'], y=y_col, size=df['Số_lượng'])
         fig3.update_layout(width=300)
         st.plotly_chart(fig3)
         

def Convert():
    # List of .xls files in the current directory
    xls_files = [file for file in os.listdir('.') if file.endswith('.xls')]
    # Convert each .xls file to .xlsx
    for xls_file in xls_files:
        convert_xls_to_xlsx(xls_file)


# Function to convert weight from bag to kilogram
def convert_to_kilogram(description, total, unit):
    # Check if the unit is already "Kilogram" and return the original values
    if unit.lower() in ['kg', 'kilogram']:
        return total, unit
    # Search for weight information in the description
    weight_match = re.search(r'(\d+(\.\d+)?)\s*(k?g|gr|gram|kilogram)', description, re.IGNORECASE)  # k?g = kg|g (the '?' make the 'k' optional)
    # Use regular expression (re.search) to find the weight information in the description string.
    # The pattern: \d+(\.\d+)?          matches a number with an optional decimal point.
    # The pattern: \s*                  matches any whitespace characters (if present) between the number and the unit.
    # The pattern: (kg|g|gr|gram|kilogram) matches the unit, which can be any of the specified options (case-insensitive).
    if weight_match:
        weight_value = float(weight_match.group(1))
        weight_unit = weight_match.group(3).lower()
        # Convert 'Total' and 'Unit' columns based on weight_unit
        if weight_unit.lower() in ['kg', 'kgm', 'kilogram', 'kilograms']:
            return total * weight_value, 'Kilogram'
        elif weight_unit.lower() in ['g', 'gr', 'gram']:
            return total * (weight_value / 1000), 'Kilogram'
    # If we find weight information in the description, extract the numeric value and the unit from the matched pattern.
    # If unit = "kg" "kilogram," update the 'Total' col by multiplying it with the weight value and set the 'Unit' column to "Kilogram."
    # If unit = "g" "gram,"      update the 'Total' col by multiplying it with the weight value divided by 1000 (to convert grams to kilograms) and set the 'Unit' column to "Kilogram."
    # If weight information not found, return original total and unit
    return total, unit



# SIDE BAR
with st.sidebar:
    selected = option_menu(
        menu_title='Menu', #required (default:None)
        options=['Preprocess','Merge','Analyze'], #required
        icons=['house','book','pen'], #optional -> find on Bootstrap
        menu_icon='cast', #optional
        default_index=0 #optional
    )


if selected == 'Preprocess':
    Convert()

    pre_process_type = st.sidebar.selectbox('What type of pre-processing data do you need ?', ('Dried Fruit','Food Additive'))

    if pre_process_type == 'Dried Fruit':
        # PROCESS FILE
        file_uploads = st.file_uploader('Upload your file', accept_multiple_files=True)
        dfs = {}  # Dictionary to store DataFrames
        if file_uploads is not None:
            for file_upload in file_uploads:
                df, file_type = process_export_file(file_upload)
                if df is not None:
                    filename = file_upload.name
                    dfs[filename] = df  # Store the DataFrame in the dictionary
            # Show the uploaded DataFrames
            for filename, df in dfs.items():
                # PRE-PROCESS 
                st.write(f"DataFrame before pre-processing {filename}:",df)
                df = df.iloc[:, 0:17]
                # df.rename(columns={'日期':'Time','申报号':'Mã_tờ_khai','进口商（越南语)':'Cty_nhập','进口商英文':'Cty_nhập(TA)',    # FOR IMPORT ONLY
                #                 '进口商地址越语':'Địa_chỉ','税务代码':'Mã_số_thuế','出口商':'Nhà_cung_cấp','出口商地址':'Địa_chỉ(ncc)',
                #                 '出口国':'Xuất_xứ','HS编码':'HScode','商品描述':'Sản_phẩm','数量':'Số_lượng','数量单位':'Đơn_vị',
                #                 '重量':'Cân_nặng','金额':'Thành_tiền','金额单位':'Tiền_tệ','单价':'Đơn_giá'},inplace=True)
                df.rename(columns={'日期':'Time','申报号':'Mã_tờ_khai','进口商':'Công_ty_nhập','进口商地址':'Địa_chỉ',               ## FOR EXPORT ONLY
                                '进口国代码':'Nước_nhập','出口商':'Nhà_cung_cấp','出口商ID':'Mã_số_thuế','出口国)':'Xuất_xứ',
                                'HS编码':'HScode','商品描述':'Miêu_tả_sản_phẩm','数量':'Số_lượng', '数量单位':'Đơn_vị','重量':'Khối_lượng',
                                '发票金额（美元）':'Hoá_đơn','单价':'Đơn_giá','金额单位':'Tiền_tệ','出口税额':'Thuế_xuất'},inplace=True)
                
                # ADD AND RENAME COLUMNS
                df.insert(df.columns.get_loc('Miêu_tả_sản_phẩm') + 1, 'SảnPhẩm', '')
                df.insert(df.columns.get_loc('Miêu_tả_sản_phẩm') + 1, 'PhânLoại', '')
                # df.rename(columns={'Mã_xuất_khẩu':'Mã_số_thuế'},inplace=True)
                # df['Mã_số_thuế'] = df['Mã_số_thuế'].astype(str)
                # # = df.rename(columns={'Mã_tờ_khai': 'Mã_số_thuế'}, inplace=True).astype({'Mã_số_thuế': str})

                # df = df[(df['Sản_phẩm'].str.contains('beverage|food additives|food supplement|supplement|food additive|Phụ gia thực phẩm|thực phẩm|sx thực phẩm|chế biến thực phẩm|confectionery materials', flags=re.IGNORECASE, regex=True)) 
                #         & (~df['Sản_phẩm'].str.contains('không dùng trong thực phẩm|not used in food', flags=re.IGNORECASE, regex=True))]
                # check valid row 
                df['Miêu_tả_sản_phẩm'].fillna('', inplace=True)
                st.write(f'Number of rows before filtering: {df.shape[0]}')
                df = df[(df['Miêu_tả_sản_phẩm'].str.contains('chuối|đu đủ|dứa|banana|pineapple|papaya', flags=re.IGNORECASE, regex=True))]
                st.write(f'Number of rows after filtering: {df.shape[0]}')

                df['HScode'] = df['HScode'].astype(str).apply(lambda x: '0' + x if x.startswith('8') else x)
                df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d')
                df['Day'] = df['Time'].dt.day
                df['Month'] = df['Time'].dt.month
                df['Year'] = df['Time'].dt.year
                # Get the column to be moved
                col1 = df.pop('Day')
                col2 = df.pop('Month')
                col3 = df.pop('Year')
                # Insert cols at the desired position (index 0)
                df.insert(1, 'Day', col1)
                df.insert(2, 'Month', col2)
                df.insert(3, 'Year', col3)
                df.drop(['Time'], axis=1, inplace=True)
                st.write(f"DataFrame after pre-processing and before processing {filename}:",df)
                # END PRE-PROCESS 

                # SET DATATYPES FOR COLUMNS
                df = df.astype({'Day': str, 'Month': str, 'Year': str, 'Mã_tờ_khai': int, 'Công_ty_nhập': str, 'Địa_chỉ': str,
                'Nước_nhập': str, 'Loại': str, 'Mã_số_thuế':str, 'Xuất_xứ':str, 'HScode':str, 'Miêu_tả_sản_phẩm':str, 'SảnPhẩm':str, 
                'PhânLoại':str, 'Số_lượng':float, 'Đơn_vị':str, 'Khối_lượng':float,'Hoá_đơn':float, 'Đơn_giá':float, 'Tiền_tệ':str})
                df['Số_lượng'] = df['Số_lượng'].round(2)
                df['Khối_lượng'] = df['Khối_lượng'].round(2)
                df['Hoá_đơn'] = df['Hoá_đơn'].round(2)
                df['Đơn_giá'] = df['Đơn_giá'].round(2)

                # PROCESS

                # EXPORT
                # df.loc[ df['Nhà_cung_cấp'].str.contains('CÁ NHÂN TỔ CHỨC KHÔNG CÓ MÃ SỐ THUẾ', flags=re.IGNORECASE, regex=True), 'Loại'  ] = 'Hộ Kinh Doanh Cá Thể'
                # df.loc[ df['Nhà_cung_cấp'].str.contains('DỊCH VỤ HÀNG KHÔNG| tiếp vận| dịch vụ hàng hoá', flags=re.IGNORECASE, regex=True), 'Loại'  ] = 'Xuất Uỷ Thác'
                # df.loc[ ~(df['Nhà_cung_cấp'].str.contains('CÁ NHÂN TỔ CHỨC KHÔNG CÓ MÃ SỐ THUẾ', flags=re.IGNORECASE, regex=True)) & ~(df['Nhà_cung_cấp'].str.contains('DỊCH VỤ HÀNG KHÔNG| tiếp vận| dịch vụ hàng hoá', flags=re.IGNORECASE, regex=True)), 'Loại'  ] = 'Xuất Trực Tiếp'
                # IMPORT
                df.loc[ df['Nhà_cung_cấp'].str.contains('CÁ NHÂN TỔ CHỨC KHÔNG CÓ MÃ SỐ THUẾ|KHÔNG CÓ MÃ SỐ THUẾ', flags=re.IGNORECASE, regex=True), 'Loại'  ] = 'Hộ Kinh Doanh Cá Thể'
                df.loc[ df['Nhà_cung_cấp'].str.contains('DỊCH VỤ HÀNG KHÔNG| tiếp vận| dịch vụ hàng hoá|KHACH LE SAN BAY TAN SON NHAT|KHACH LE SAN BAY QUOC TE TAN SON NHAT|KHACH LE|HANH KHACH TREN CAC CHUYEN BAY QUOC TE', flags=re.IGNORECASE, regex=True), 'Loại'  ] = 'Xuất Uỷ Thác'
                df.loc[ ~(df['Nhà_cung_cấp'].str.contains('CÁ NHÂN TỔ CHỨC KHÔNG CÓ MÃ SỐ THUẾ', flags=re.IGNORECASE, regex=True)) & ~(df['Nhà_cung_cấp'].str.contains('DỊCH VỤ HÀNG KHÔNG| tiếp vận| dịch vụ hàng hoá|KHACH LE SAN BAY TAN SON NHAT|KHACH LE SAN BAY QUOC TE TAN SON NHAT|KHACH LE|HANH KHACH TREN CAC CHUYEN BAY QUOC TE', flags=re.IGNORECASE, regex=True)), 'Loại'  ] = 'Xuất Trực Tiếp'

                # Assuming you have an exchange rate dictionary
                exchange_rates = {
                    'USD': 1.0,  # USD to USD exchange rate (always 1)
                    'AUD': 0.67, # Exchange rate for AUD to USD
                    'EUR': 1.11, # Exchange rate for EUR to USD
                    'GBP': 1.29,  # Exchange rate for GBP to USD
                    'VND':0.000042,   # Exchange rate for VND to USD
                    'CAD':0.75,       # Exchange rate for CAD to USD
                    'CHF':1.14,       # Exchange rate for CHF to USD
                    'CNY':0.14,       # Exchange rate for CNY to USD
                    'HKD':0.13,       # Exchange rate for HKD to USD
                    'JPY':0.0070      # Exchange rate for JPY to USD
                }
                # Function to convert prices to USD based on the currency
                def convert_total_to_usd(row):
                    currency = row['Tiền_tệ']
                    exchange_rate = exchange_rates.get(currency, 1.0)  # Default to 1 if currency not found
                    return row['Hoá_đơn'] * exchange_rate
                def convert_perUnit_to_usd(row):
                    currency = row['Tiền_tệ']
                    exchange_rate = exchange_rates.get(currency, 1.0)  # Default to 1 if currency not found
                    return row['Đơn_giá'] * exchange_rate
                # Apply the function to the DataFrame to convert 'Đơn_giá' to USD
                df['Hoá_đơn'] = df.apply(convert_total_to_usd, axis=1)
                df['Đơn_giá'] = df.apply(convert_perUnit_to_usd, axis=1)
                df.loc[ df['Tiền_tệ'].isin(['AUD','EUR','GBP','VND','CAD','CHF','CNY','HKD','JPY']), 'Tiền_tệ'] = 'USD'
           
                # Set the 'Sản_phẩm' column to lowercase to make the comparison case-insensitive
                df['Miêu_tả_sản_phẩm'] = df['Miêu_tả_sản_phẩm'].str.lower()
                # Fill missing values in the 'Sản_phẩm' column with an empty string
                df['Miêu_tả_sản_phẩm'].fillna('', inplace=True)

                # CHECK NULL VALUE
                # st.write(f'The number of null value in column "MST" are: {(df["Mã_số_thuế"]==0).sum()}') # for INT datatype
                # st.write(f'The number of "0" in column "Mã_số_thuế" are: {df["Mã_số_thuế"].value_counts()["0"]}') # for STR datatype

                # SẢN PHẨM
                # Find rows where the 'Sản_phẩm' column contains 'banana' or 'chuối' (case-insensitive)
                banana_rows = df[(df['Miêu_tả_sản_phẩm'].str.contains('chuối|banana|bananas', flags=re.IGNORECASE, regex=True)) & (~df['Miêu_tả_sản_phẩm'].str.contains('fruit|hoa quả|mix|mixed|includes|include|gồm', flags=re.IGNORECASE, regex=True))]
                # Set the 'SảnPhẩm' column to 'Banana' for the matching rows
                df.loc[banana_rows.index, 'SảnPhẩm'] = 'Chuối'

                # Find rows where the 'Sản_phẩm' column contains papaya (case-insensitive)
                papaya_rows = df[(df['Miêu_tả_sản_phẩm'].str.contains('đu đủ|papaya', flags=re.IGNORECASE, regex=True)) & (~df['Miêu_tả_sản_phẩm'].str.contains('fruit|hoa quả|mix|mixed|includes|include|gồm', flags=re.IGNORECASE, regex=True))]
                # Set the 'SảnPhẩm' column to 'Banana' for the matching rows
                df.loc[papaya_rows.index, 'SảnPhẩm'] = 'Đu Đủ'

                # Find rows where the 'Sản_phẩm' column contains pineapple (case-insensitive)
                pineapple_rows = df[(df['Miêu_tả_sản_phẩm'].str.contains('dứa|pineapple', flags=re.IGNORECASE, regex=True)) & (~df['Miêu_tả_sản_phẩm'].str.contains('fruit|hoa quả|mix|mixed|includes|include|gồm', flags=re.IGNORECASE, regex=True))]
                # Set the 'SảnPhẩm' column to 'Banana' for the matching rows
                df.loc[pineapple_rows.index, 'SảnPhẩm'] = 'Dứa'

                # Find rows where the 'Sản_phẩm' column contains mix (case-insensitive)
                mix_rows = df[df['Miêu_tả_sản_phẩm'].str.contains('fruit|hoa quả|mix|mixed|includes|include|gồm', flags=re.IGNORECASE, regex=True)]
                # Set the 'SảnPhẩm' column to 'Banana' for the matching rows
                df.loc[mix_rows.index, 'SảnPhẩm'] = 'Mix'

                st.write(df['SảnPhẩm'].value_counts())
                
                # PHÂN LOẠI
                # SẤY KHÔ
                saykho = df[df['Miêu_tả_sản_phẩm'].str.contains('khô', flags=re.IGNORECASE, regex=True)]
                df.loc[saykho.index, 'PhânLoại'] = 'Sấy Khô'

                # SẤY DẺO
                saydeo = df[df['Miêu_tả_sản_phẩm'].str.contains('dẻo|soft', flags=re.IGNORECASE, regex=True)]
                df.loc[saydeo.index, 'PhânLoại'] = 'Sấy Dẻo'

                # SẤY GIÒN
                saygion = df[df['Miêu_tả_sản_phẩm'].str.contains('crispy|giòn', flags=re.IGNORECASE, regex=True)]
                df.loc[saygion.index, 'PhânLoại'] = 'Sấy Giòn'

                # LEFTOVER
                leftover = df[~(df.index.isin(saykho.index) | df.index.isin(saydeo.index) | df.index.isin(saygion.index))]
                df.loc[leftover.index, 'PhânLoại'] = 'Sấy'

                # TRANSFORM THE UNIT TO KILOGRAM
                # Apply the function to update 'Total' and 'Unit' columns
                df['Số_lượng'], df['Đơn_vị'] = zip(*df.apply(lambda row: convert_to_kilogram(row['Miêu_tả_sản_phẩm'], row['Số_lượng'], row['Đơn_vị']), axis=1))
                # Make the value consistent (= Kilogram)
                df.loc[df['Đơn_vị'].isin(['Kilogram','Kilograms','KGM','Kg','kg','KILOGRAMS']),'Đơn_vị'] = 'Kilogram'

                st.write(f"DataFrame after processing {filename}:",df)
                # END PROCESS

                
                xlsx = convert_df(df)
                fname = st.text_input('Save file name as: ',key=f'{filename}')
                if fname:  # Check if fname is not empty
                    xlsx = convert_df(df)
                    st.download_button(
                        label="Download data as XLSX format",
                        data=xlsx,
                        file_name=f'{fname}.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'  # Set MIME type to XLSX
                    )
            

    if pre_process_type == 'Food Additive':
        # PROCESS FILE
        file_uploads = st.file_uploader('Upload your file', accept_multiple_files=True)
        dfs = {}  # Dictionary to store DataFrames
        if file_uploads is not None:
            for file_upload in file_uploads:
                df, file_type = process_import_file(file_upload)
                if df is not None:
                    filename = file_upload.name
                    dfs[filename] = df  # Store the DataFrame in the dictionary
            # Show the uploaded DataFrames
            for filename, df in dfs.items():
                # PRE-PROCESS 
                st.write(f"DataFrame before pre-processing {filename}:",df)
                st.write('Total rows and columns of dataFrame before pre-processing:',df.shape)
                df = df.iloc[:, 0:18]
                # df.columns = ['Time', 'Mã_tờ_khai', 'Cty_nhập', 'Cty_nhập(TA)', 'Địa_chỉ', 'Mã_số_thuế',
                #               'Nhà_cung_cấp', 'Địa_chỉ(ncc)', 'Xuất_xứ', 'HScode', 'Tên_sản_phẩm',
                #               'Số_lượng', 'Đơn_vị', 'Cân_nặng', 'Thành_tiền', 'Đơn_vị', 'Đơn_giá']
                df.rename(columns={'日期':'Time','申报号':'Mã_tờ_khai','进口商（越南语)':'Công_ty_nhập','进口商英文':'Công_ty_nhập(TA)',    # FOR IMPORT ONLY
                                '进口商地址越语':'Địa_chỉ','税务代码':'Mã_số_thuế','出口商':'Nhà_cung_cấp','出口商地址':'Địa_chỉ(ncc)',
                                '出口国':'Xuất_xứ','HS编码':'HScode','商品描述':'Sản_phẩm','数量':'Số_lượng','数量单位':'Đơn_vị',
                                '重量':'Khối_lượng','金额':'Thành_tiền','金额单位':'Tiền_tệ','单价':'Đơn_giá'},inplace=True)
                
                # CHECK VALID ROW
                st.write(f'Number of rows before filtering: {df.shape[0]}')
                df = df[(df['Sản_phẩm'].str.contains('gelatin|gelatine', flags=re.IGNORECASE, regex=True))]
                st.write(f'Number of rows after filtering: {df.shape[0]}')

                df = df[(df['Sản_phẩm'].str.contains('beverage|food additives|food supplement|supplement|food additive|flavor|Phụ gia thực phẩm|thực phẩm|sx thực phẩm|chế biến thực phẩm|confectionery materials', flags=re.IGNORECASE, regex=True)) 
                    & (~df['Sản_phẩm'].str.contains('không dùng trong thực phẩm|not used in food|viên nang|không chứa trong thực phẩm', flags=re.IGNORECASE, regex=True))]
                
                df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d')
                df['Day'] = df['Time'].dt.day
                df['Month'] = df['Time'].dt.month
                df['Year'] = df['Time'].dt.year
                # Get the column to be moved
                col1 = df.pop('Day')
                col2 = df.pop('Month')
                col3 = df.pop('Year')
                # Insert cols at the desired position (index 0)
                df.insert(1, 'Day', col1)
                df.insert(2, 'Month', col2)
                df.insert(3, 'Year', col3)
                df.drop(['Time'], axis=1, inplace=True)
                st.write(f"DataFrame after pre-processing and before processing {filename}:",df)
                st.write('Total rows and columns of dataFrame after pre-processing',df.shape)
                # END PRE-PROCESS 
                st.write("Column names in DataFrame:", df.columns)

                # SET DATATYPES FOR COLUMNS
                df = df.astype({'Day': str, 'Month': str, 'Year': str, 'Mã_tờ_khai': int, 'Công_ty_nhập': str, 'Công_ty_nhập(TA)':str, 'Địa_chỉ': str,
                'Mã_số_thuế':str, 'Nhà_cung_cấp':str, 'Địa_chỉ(ncc)':str, 'Xuất_xứ':str, 'HScode':str, 'Sản_phẩm':str,  
                'Số_lượng':float, 'Đơn_vị':str, 'Khối_lượng':float,'Thành_tiền':float, 'Tiền_tệ':str, 'Đơn_giá':float})
                df['Số_lượng'] = df['Số_lượng'].round(2)
                df['Khối_lượng'] = df['Khối_lượng'].round(2)
                df['Thành_tiền'] = df['Thành_tiền'].round(2)
                df['Đơn_giá'] = df['Đơn_giá'].round(2)

                # TRANSFORM THE UNIT TO KILOGRAM
                # Apply the function to update 'Total' and 'Unit' columns
                df['Số_lượng'], df['Đơn_vị'] = zip(*df.apply(lambda row: convert_to_kilogram(row['Sản_phẩm'], row['Số_lượng'], row['Đơn_vị']), axis=1))
                
                # Make the value consistent (= Kilogram)
                df.loc[df['Đơn_vị'].isin(['Kilogram','Kilograms','KGM']),'Đơn_vị'] = 'Kilogram'


                st.write(f"DataFrame after processing {filename}:",df)
                # END PROCESS


                xlsx = convert_df(df)
                fname = st.text_input('Save file name as: ',key=f'{filename}')
                if fname:  # Check if fname is not empty
                    xlsx = convert_df(df)
                    st.download_button(
                        label="Download data as XLSX format",
                        data=xlsx,
                        file_name=f'{fname}.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'  # Set MIME type to XLSX
                    )


dfs = []
# Function to process the uploaded file
def process_file(file):
    df = pd.read_excel(file)  # Assuming the file is in Excel format, you can adjust this based on the actual file type
    return df

if selected == 'Merge':
  
    # File Upload
    file_uploads = st.file_uploader('Upload your files', accept_multiple_files=True)

    # Step 1: Read each uploaded file and store the data as separate DataFrames
    if file_uploads is not None:
        for file_upload in file_uploads:
            df = process_file(file_upload)
            if df is not None:
                dfs.append(df)  # Append the DataFrame to the list
    # Step 2: Concatenate the DataFrames along the rows axis (axis=0)
    if dfs:
        combined_df = pd.concat(dfs, axis=0, ignore_index=True)
        # Step 3: Display or use the combined DataFrame as needed
        st.write("Combined DataFrame:", combined_df)
        name = st.text_input('Save file name as: ')
        if name:
            excel = convert_df(combined_df)
            st.download_button(
                            label="Download data combined as XLSX format",
                            data=excel,
                            file_name=f'{name}.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'  # Set MIME type to XLSX
            )
    else:
        st.warning("Please upload some files first.")



if selected == 'Analyze':

    process_type = st.sidebar.selectbox('What type of processing/analyzing data do you need ?', ('Visualize the dataset', 'Filter by requirements', 'Add fruit rows'))
    if process_type == 'Add fruit rows':
        # # PROCESS FILE + ANALYZE
        # file_upload = st.file_uploader('Upload your file')
        # df = pd.DataFrame()
        # if file_upload is not None:
        #     df, file_type = process_file(file_upload)

        st.info('Default dataset: Fruit.xlsx')
        df = pd.read_excel('Fruit.xlsx')
        # PROCESS FILE
        file_uploads = st.file_uploader('Upload your file', accept_multiple_files=True)
        dfs = {}  # Dictionary to store DataFrames
        if file_uploads is not None:
            for file_upload in file_uploads:
                df, file_type = process_file(file_upload)
                if df is not None:
                    filename = file_upload.name
                    dfs[filename] = df  # Store the DataFrame in the dictionary
            # Show the uploaded DataFrames
            for filename, df in dfs.items():
                Analytics()
            
            # FORM 
            st.sidebar.header("Add New Record")
            options_form=st.sidebar.form("Option Form")
            # day=options_form.slider("Day",1,31,disabled=False)
            # month=options_form.slider("Month",1,12,disabled=False)
            # year=options_form.number_input("Year",disabled=False)
            date_details = options_form.date_input("Select time", todayDate)
            code=options_form.text_input("Code",max_chars=12,disabled=False)
            import_company=options_form.text_input("Import Company",value='BFC',disabled=False)
            address=options_form.text_input("Company Address",disabled=False)
            import_country=options_form.text_input("Import Country",value='Vietnam',disabled=False)
            supplier=options_form.text_input("Supplier",disabled=False)
            tax=options_form.number_input("Tax Code", max_value=12,disabled=False)
            origin =options_form.selectbox("Origin",
            {"United States","Germany",'Japan','China','Slovenia','Thailand','China','Spain','Singapore','India'})
            export_type =options_form.selectbox("Export Type",
            {"Xuất Trực Tiếp","Hộ Kinh Doanh Cá Thể","Xuất Uỷ Thác"})
            hscode =options_form.text_input("Tax Code",max_chars=8,placeholder='HScode requires 8 digits',disabled=False)
            product =options_form.text_input("Product Name",value='Orange',disabled=False)
            description =options_form.text_input("Product Description",value='',disabled=False)
            product_type =options_form.selectbox("Product Type",
            {"Sấy","Sấy Khô","Sấy Giòn","Sấy Dẻo"})
            quantity = options_form.number_input("Quantity",min_value=0,disabled=False)
            unit = options_form.selectbox("Unit",{"KG","Ton",'Bag'})
            weight = options_form.number_input("Weight",min_value=0,disabled=False)
            price = options_form.number_input("Price per unit",min_value=0.1,step=0.1,disabled=False)
            currency=options_form.text_input("Currency",value='USD',disabled=True)
            add_data = options_form.form_submit_button(label="Add")

        #when button is clicked
            if add_data:
                if import_company != "" and supplier != "" and product != "" and quantity != "":
                    
                    df = pd.concat([df, pd.DataFrame.from_records([{ 
                    'Day': date_details.day,
                    'Month':date_details.month,
                    'Year':date_details.year,
                    'Date': date_details,
                    'Mã_tờ_khai':code,
                    'Công_ty_nhập':import_company,
                    'Địa_chỉ':address,
                    'Nước_nhập': import_country,
                    'Nhà_cung_cấp': supplier,
                    'Mã_số_thuế': tax,
                    'Xuất_xứ': origin,
                    'Loại': export_type,
                    'HScode': hscode,
                    'Product': product,
                    'Miêu_tả_sản_phẩm':description,
                    'PhânLoại':product_type,
                    'Số_lượng': float(quantity),
                    'Đơn_vị': unit,
                    'Khối_lượng': float(weight),
                    'Hoá_đơn': float(quantity*price),
                    'Đơn_giá': currency,
                    'Tiền_tệ': float(price)
                    }])])
                    try:
                        df.to_excel("Fruit.xlsx",index=False)
                    except:
                        st.warning("Unable to write, Please close your dataset !!")
                else:
                    st.sidebar.error("Fields required")

            with st.expander("Records"):
                selected = st.multiselect('Filter :', df.columns[1:])
                st.dataframe(df[selected],use_container_width=True)

            # with st.expander("Cross Tab"):
            #     tab = pd.crosstab([df['Product']],df['Số_lượng'], margins=True)
            #     st.dataframe(tab) 
            #     tab2 = pd.crosstab([df['Product']],df['Xuất_xứ'], margins=True)
            #     st.dataframe(tab2) 

    if process_type == 'Filter by requirements':
        # Upload a file
        file_upload = st.file_uploader("Upload a file (XLSX or CSV)", type=["xlsx", "csv"])

        # Check if a file is uploaded
        if file_upload is not None:
            # Process the file and get the DataFrame
            df = process_file(file_upload)
            # Check if the DataFrame is not None
            if df is not None:
                # Clean and reconstruct selected columns
                string_columns = df.select_dtypes(include=['object']).columns.tolist()
                for col in df.columns:
                    if col in string_columns:
                        df[col] = df[col].apply(lambda x: re.sub(r'(\W)', r' \1 ', str(x)))
                # Display cleaned DataFrame
                st.write(df)
                # Select a column for filtering
                col = st.selectbox('Select column for filtering', string_columns)
                # User input for filtering
                with st.expander(f'Filtering in details for {col}'):
                    fruit = st.text_input(f'What things do you need in {col} ?')
                    # User input for filtering exceptions
                    exceptions = st.text_input(f'Any exceptions with your things in {col} ? (comma-separated, e.g., no,none. Do not have -> type no/none)')     # multiple exceptions
                    # Split the input into a list of exceptions
                    exception_list = [e.strip() for e in exceptions.split(',') if e.strip()]
                    # exception = st.text_input(f'Any exception with your things in {col} ? (do not have -> type no/none)')  # single exception
                    add_fruit_col = st.toggle(f'Add {fruit} as new column ?')
                    if add_fruit_col:
                        index_fruit_col = st.slider(f'Select the position of {fruit} column',0,len(df.columns))
                        df.insert(index_fruit_col, 'Product', fruit)

                # Check if the selected column exists in the DataFrame
                if col in df.columns:
                    # Apply filter based on user input
                    df[col].fillna('', inplace=True)
                    # if exception.lower() in ['no', 'none']:                                                           # single exception
                    for word in exception_list:                                                                         # multiple exceptions
                        if word.lower in ['no','none']:                                                                 # multiple exceptions
                            df = df[df[col].str.contains(fruit, flags=re.IGNORECASE, regex=True)]
                        else: 
                            df = df[df[col].str.contains(fruit, flags=re.IGNORECASE, regex=True)]
                            df = df[~(df[col].str.contains(fr'\b{word}\b', flags=re.IGNORECASE, regex=True))]
                            # df = df[~df[col].str.lower().isin([e.lower() for e in exception_list])]                     # multiple exceptions
                            # df = df[~(df[col].str.contains(fr'\b{exception}\b', flags=re.IGNORECASE, regex=True))]    # single exception
                    # Display the filtered DataFrame
                    with st.expander(f'Check our statistics with your dataframe'):
                        st.write('Check null value in columns:', df.isnull().sum())
                        st.write('Check number of values in columns:', df[col].value_counts())
                        st.write('Check the statistics of dataframe', df.describe())
                    with st.expander('We plan to embed these common statistical commands below'):
                        statistics = '''
                        Some common commands for performing statistical analysis with a Pandas DataFrame:  
                        
                            Descriptive Statistics:

                            df.describe(): Provides summary statistics for numeric columns.
                            df.mean(): Computes the mean for each numeric column.
                            df.median(): Computes the median for each numeric column.
                            df.std(): Computes the standard deviation for each numeric column.
                            df.min(): Computes the minimum value for each numeric column.
                            df.max(): Computes the maximum value for each numeric column.
                            Frequency Counts:

                            df['column'].value_counts(): Counts the frequency of unique values in a specific column.
                            df.groupby('column')['another_column'].count(): Counts occurrences based on grouping.
                            Correlation and Covariance:

                            df.corr(): Computes the correlation matrix for all numeric columns.
                            df.cov(): Computes the covariance matrix for all numeric columns.
                            Filtering and Aggregation:

                            df[df['column'] > value]: Filters rows based on a condition.
                            df.groupby('column').agg({'other_column': 'mean'}): Aggregates data based on grouping.
                            Quantiles:

                            df.quantile(q=0.25): Computes the 25th percentile for numeric columns.
                            df.quantile(q=[0.25, 0.75]): Computes multiple quantiles.
                            Histograms and Plots:

                            df['column'].hist(): Generates a histogram for a specific column.
                            df.plot(kind='box'): Creates a box plot.
                            Skewness and Kurtosis:

                            df.skew(): Computes the skewness of numeric columns.
                            df.kurtosis(): Computes the kurtosis of numeric columns.
                            Sampling:

                            df.sample(n=5): Randomly samples n rows from the DataFrame.
                            df.sample(frac=0.25): Randomly samples a fraction of rows.
                            Correlation Heatmap:

                            You can use libraries like Seaborn to create correlation heatmaps.
                            Cross-tabulation:

                            pd.crosstab(df['column1'], df['column2']): Generates a cross-tabulation table.
                            Missing Data:

                            df.isnull(): Checks for missing values in the DataFrame.
                            df.dropna(): Removes rows with missing values.
                            df.fillna(value): Fills missing values with a specified value.
                            Percentile Rank:

                            df.rank(pct=True): Computes the percentile rank of values.
                            Resampling (for Time Series Data):

                            df.resample('D').sum(): Resamples time series data at daily frequency and aggregates it.'''
                        st.markdown(statistics)

                    st.write(f'We have found: {df.shape[0]} rows fit with your requirements !')
                    st.write(df)

                else:
                    st.warning(f"Column '{col}' does not exist in the DataFrame.")


                xlsx = convert_df(df)
                fname = st.text_input('Save file name as:')
                if fname:  # Check if fname is not empty
                    xlsx = convert_df(df)
                    st.download_button(
                        label="Download data as XLSX format",
                        data=xlsx,
                        file_name=f'{fname}.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'  # Set MIME type to XLSX
                    )

    if process_type == 'Visualize the dataset':
        st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
        fl = st.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xlsx", "xls"])
        if fl is not None:
            filename = fl.name
            st.write(filename)
            
            # Check the file type and read accordingly
            if filename.endswith('.csv') or filename.endswith('.txt'):
                df = pd.read_csv(fl, encoding="utf-8", delimiter=',')  # Modify delimiter if needed
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                df = pd.read_excel(fl)  # No need to specify encoding for Excel files
        else:
            os.chdir(r"/Users/vuhainam/Documents/PROJECT_DA/BFC/ProcessData/FullProcess")
            df = pd.read_excel("Fruit.xlsx")  # No need to specify encoding for Excel files

        col1, col2 = st.columns((2))
        df["Date"] = pd.to_datetime(df["Date"])

        # Getting the min and max date 
        startDate = pd.to_datetime(df["Date"]).min()
        endDate = pd.to_datetime(df["Date"]).max()

        with col1:
            date1 = pd.to_datetime(st.date_input("Start Date", startDate))

        with col2:
            date2 = pd.to_datetime(st.date_input("End Date", endDate))

        df = df[(df["Date"] >= date1) & (df["Date"] <= date2)].copy()

        st.sidebar.header("Choose your filter: ")
        # Filter as 'Nước nhập'
        import_country = st.sidebar.multiselect("Pick your Country", df["Nước_nhập"].unique())
        if not import_country:
            df2 = df.copy()
        else:
            df2 = df[df["Nước_nhập"].isin(import_country)]

        # Filter as 'Nhà cung cấp'
        exporter = st.sidebar.multiselect("Pick the Exporter", df2["Nhà_cung_cấp"].unique())
        if not exporter:
            df3 = df2.copy()
        else:
            df3 = df2[df2["Nhà_cung_cấp"].isin(exporter)]

        # Filter as 'Loại xuất'
        type_export = st.sidebar.multiselect("Pick the Type",df3["Loại"].unique())


        # Filter the data based on Import Country, Exporter and Export Type
        if not import_country and not exporter and not type_export:
            filtered_df = df
        elif not import_country and not exporter:
            filtered_df = df[df["Loại"].isin(type_export)]
        elif not exporter and not type_export:
            filtered_df = df[df["Nước_nhập"].isin(import_country)]
        elif import_country and exporter:
            filtered_df = df3[df["Nhà_cung_cấp"].isin(exporter) & df3["Nước_nhập"].isin(import_country)]
        elif import_country and type_export:
            filtered_df = df3[df["Nước_nhập"].isin(import_country) & df3["Loại"].isin(type_export)]
        elif exporter and type_export:
            filtered_df = df3[df["Nhà_cung_cấp"].isin(exporter) & df3["Loại"].isin(type_export)]
        elif exporter:
            filtered_df = df3[df3["Nhà_cung_cấp"].isin(exporter)]
        else:
            filtered_df = df3[df3["Nhà_cung_cấp"].isin(exporter) & df3["Nước_nhập"].isin(import_country) & df3["Loại"].isin(type_export)]

        product = filtered_df.groupby(by = ["Product"], as_index = False)["Hoá_đơn"].sum()

        with col1:
            st.subheader("Sales by Product")
            fig = px.bar(product, x = "Product", y = "Hoá_đơn", text = ['${:,.2f}'.format(x) for x in product["Hoá_đơn"]],
                        template = "seaborn")
            st.plotly_chart(fig,use_container_width=True, height = 200)

        # HECTOR ADD
        # Add a slider to allow the user to select the top N HS codes
        n_hscode = st.slider("Select Top HS Codes", 1, len(filtered_df['HScode'].unique()), 3)
        # Filter the DataFrame to select the top N HS codes
        top_hscode = filtered_df[filtered_df['HScode'].isin(filtered_df['HScode'].unique()[:n_hscode])]

        # EXPLAIN CODE
        # filtered_df['HScode'].unique()[:n_hscode] = array of HSCODE
        # filtered_df['HScode'].isin(filtered_df['HScode'].unique()[:n_hscode]) = series with boolean values (true->get,false->skip)
        # filtered_df[filtered_df['HScode'].isin(filtered_df['HScode'].unique()[:n_hscode])] = dataframe with a filtered condition

        with col2:
            st.subheader("Sales by HScode")
            fig = px.pie(top_hscode, values="Hoá_đơn", names="HScode", hole=0.5)
            fig.update_traces(text=top_hscode["HScode"], textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        cl1, cl2 = st.columns((2))
        with cl1:
            with st.expander("View Product Data"):
                st.write(product.style.background_gradient(cmap="Blues"))
                csv = product.to_csv(index = False).encode('utf-8')
                st.download_button("Download Data", data = csv, file_name = "Product.csv", mime = "text/csv",
                                    help = 'Click here to download the data as a CSV file')

        with cl2:
            with st.expander("View Country-HScode Data"):
                country = filtered_df.groupby(by = ["Nước_nhập",'HScode'], as_index = False)["Hoá_đơn"].sum()
                st.write(country.style.background_gradient(cmap="Oranges"))
                csv = country.to_csv(index = False).encode('utf-8')
                st.download_button("Download Data", data = csv, file_name = "Country-HScode.csv", mime = "text/csv",
                                help = 'Click here to download the data as a CSV file')
                
        filtered_df["month_year"] = filtered_df["Date"].dt.to_period("M")
        st.subheader('Time Series Analysis')

        linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Hoá_đơn"].sum()).reset_index()
        fig2 = px.line(linechart, x = "month_year", y="Hoá_đơn", labels = {"Hoá_đơn": "Amount"},height=500, width = 1000,template="gridon")
        st.plotly_chart(fig2,use_container_width=True)

        with st.expander("View TimeSeries Data"):
            st.write(linechart.T.style.background_gradient(cmap="Blues"))
            csv = linechart.to_csv(index=False).encode("utf-8")
            st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

        # Create a treem based on Region, category, sub-Category
        st.subheader("Hierarchical view of Product using TreeMap")
        fig3 = px.treemap(filtered_df, path = ["Product","PhânLoại","Nước_nhập"], values = "Hoá_đơn",hover_data = ["Hoá_đơn"],
                        color = "Nước_nhập")
        fig3.update_layout(width = 800, height = 650)
        st.plotly_chart(fig3, use_container_width=True)

        chart1, chart2 = st.columns((2))
        with chart1:
            st.subheader('Sales by Export Type')
            fig = px.pie(filtered_df, values = "Hoá_đơn", names = "Loại", template = "plotly_dark")
            fig.update_traces(text = filtered_df["Loại"], textposition = "inside")
            st.plotly_chart(fig,use_container_width=True)

        with chart2:
            st.subheader('Sales by Product')
            fig = px.pie(filtered_df, values = "Hoá_đơn", names = "Product", template = "gridon")
            fig.update_traces(text = filtered_df["Product"], textposition = "inside")
            st.plotly_chart(fig,use_container_width=True)

        import plotly.figure_factory as ff
        with st.expander(":point_right: Summary :point_left:"):
            st.markdown("Correlation between key features")
            df_sample = df[0:5][["Nước_nhập","Nhà_cung_cấp","Product","PhânLoại","Số_lượng","Đơn_vị","Hoá_đơn","Tiền_tệ"]]
            fig = ff.create_table(df_sample, colorscale = "Cividis")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("Monthly sales of product")
            filtered_df["month"] = filtered_df["Date"].dt.month_name()
            sub_category_Year = pd.pivot_table(data = filtered_df, values = "Hoá_đơn", index = ["PhânLoại"],columns = "month")
            st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

        # Create a scatter plot
        data1 = px.scatter(filtered_df, x = "Đơn_giá", y = "Hoá_đơn", size = "Số_lượng")
        data1['layout'].update(title="Relationship between Hoá_đơn and Số_lượng using Scatter Plot.",
                            titlefont = dict(size=20),xaxis = dict(title="Hoá_đơn",titlefont=dict(size=19)),
                            yaxis = dict(title = "Số_lượng", titlefont = dict(size=19)))
        st.plotly_chart(data1,use_container_width=True)

        with st.expander("View Data"):
            st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

        # Download orginal DataSet
        csv = df.to_csv(index = False).encode('utf-8')
        st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")

                

                

