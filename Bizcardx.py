import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import psycopg2
from PIL import Image
import easyocr
import numpy as np
import re
from io import BytesIO

def Extract_data(Input_image): #This function is to Extract the text from image we Upload here we using EASYOCR library
    image_array = np.array(Input_image)
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_array,detail=0)

    return result,image


def Extracteddata_dict(datas):# in this we are passing the extracted text and converting them as dictioary
    
    dict = {"Name":[], "Designation":[], "Contact Number":[], "Website URL":[], "Email id":[], "Address":[], 
             "Company Name":[], "State and Pincode":[]}
    
    dict["Name"].append(datas[0])
    dict["Designation"].append(datas[1])
    
    for i in range(2,len(datas)):
    
       if datas[i].startswith('+') or (datas[i].replace('-','').isdigit() and '-'in datas[i]):
           dict["Contact Number"].append(datas[i])

       elif "@" in datas[i] and ".com" in datas[i]:
            dict["Email id"].append(datas[i])    

       elif "www" in datas[i] or "Www"  in datas[i]  or "WWW"  in datas[i] or "WwW" in datas[i] or datas[i].endswith(".com"):
           website = datas[i].lower()
           dict["Website URL"].append(website)

       elif "Tamil Nadu" in  datas[i] or "Tamilnadu" in datas[i] or "TamilNadu" in datas[i] or datas[i].isdigit():
           dict["State and Pincode"].append(datas[i])  

       elif re.match (r'^[A-Za-z\s]+$', datas[i]):
           dict["Company Name"].append(datas[i])

       else:
           addressrc =re.sub(r'[,,;]','', datas[i])
           dict["Address"].append(addressrc)   
           
    for key, value in dict.items(): # this loop is created to clear the null values
        if len(value)>0:
            concadenate= " ".join(value)
            dict[key]= [concadenate]

        else:
            value ="NA"  
            dict[key] = [value]

    return dict  

def saveExtracteddata_database(dataframe1): 
    # here we giving the dictionary which we converted as dataframe as input and Saving them in database

    Data_Base = psycopg2.connect(host = "localhost",
                            user = "postgres",
                            password = "BNandy30",
                            port = "5432",
                            database = "Bizcardx") # it is the connection to run SQL in backend

    cursor = Data_Base.cursor() #Cursor is a Temporary Memory or Temporary Work Station.

    Query = '''create table if not exists BussinesCarddetails(Name VARCHAR(80),
                                                             Designation VARCHAR(80),
                                                             "Contact Number" VARCHAR(80),
                                                             "Website URL" VARCHAR(80),
                                                             "Email ID" VARCHAR(100),
                                                             Address VARCHAR(100),
                                                             "Company Name" VARCHAR(80),
                                                             "State and Pincode" VARCHAR(100),
                                                              Image BYTEA)'''
    cursor.execute(Query)
    Data_Base.commit()
   
    for index,row in dataframe1.iterrows():
           # Check if the entry already exists in the database
        cursor.execute("SELECT * FROM BussinesCarddetails WHERE Name = %s", (row['Name'],))
        existing_entry = cursor.fetchone()
        
        if existing_entry:
           st.warning(f"Entry with Name '{row['Name']}' already exists in the database. Skipping insertion.")

        else:
            # Insert the new entry into the database
            insert_Query = '''insert into BussinesCarddetails(Name,
                                                            Designation,
                                                            "Contact Number",
                                                            "Website URL",
                                                            "Email ID",
                                                            Address,
                                                            "Company Name",
                                                            "State and Pincode",
                                                            Image)
                                        
                                                            values(%s,%s,%s,%s,%s,%s,%s,%s,%s::bytea)'''
            values = (row['Name'],
                    row['Designation'],
                    row["Contact Number"],
                    row["Website URL"],
                    row["Email id"],
                    row['Address'],
                    row["Company Name"],
                    row["State and Pincode"],
                    row['Image'])

            cursor.execute(insert_Query,values)
            Data_Base.commit()

    # Here we collecting the data we stored in DB and converting them to datafram to view, modify and delete those data
    select_query = "SELECT * FROM BussinesCarddetails" 

    cursor.execute(select_query)
    Data_Base.commit()
    BussinesCarddetails_table = cursor.fetchall()

    BussinesCarddetails_table = pd.DataFrame(BussinesCarddetails_table, columns = ('Name','Designation','Contact Number',
                                            'Website URL','Email id','Address','Company Name','State and Pincode','Image'))


    return BussinesCarddetails_table
     

# Streamlit Part

st.set_page_config(
    page_title="BizCardX: Extracting Business Card Data with OCR",
    page_icon=":label:",
    layout="wide",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app! Where you can Extract an Text from an Image using OCR"
    }
)
st.title('BizCardX: Extracting Business Card Data with OCR',)

#[theme]
primaryColor="#d8ecbb"
backgroundColor="#e6ffdc"
secondaryBackgroundColor="#6fa659"
textColor="#083b10"


Menu = option_menu(None,["Home","Upload an Image","Modify Or Delete"],
        icons=['house', 'cloud-upload','pencil-square'], 
        menu_icon="cast",
        default_index=0, 
        orientation="horizontal")
    
if Menu == "Home":
            
    col1, col2 = st.columns(2)

    with col1:
         
        st.image(Image.open(r"C:\Users\rajan\OneDrive\Desktop\BizCardX\DatatoExtract\maxresdefault.jpg"))
        st.write("""
    ## What is OCR?
OCR, or Optical Character Recognition, is a technology that allows computers to convert different types of documents, 
such as scanned paper documents, PDF files, or images captured by a digital camera, into editable and searchable data.

## How does OCR work?
Image Acquisition:-
    The process begins with capturing or acquiring an image of the document or text using a scanner, camera, or other imaging device.

Pre-processing:-
    The acquired image may undergo pre-processing steps to enhance its quality and improve OCR accuracy. 
    This may include tasks like noise reduction, image binarization (converting to black and white), deskewing (straightening tilted text), and removing artifacts.

Text Detection:-
    OCR algorithms analyze the image to locate areas containing text. This step involves identifying text 
    regions within the image.

Text Recognition:-
    Once text regions are detected, OCR software analyzes the pixel data within these regions to recognize 
    and interpret individual characters and words. This process involves sophisticated pattern recognition 
    algorithms trained to recognize various fonts, styles, and languages.

Post-processing:-
    After text recognition, post-processing steps may be applied to improve the accuracy of the extracted text.
    This may include tasks like spell checking, word correction, and formatting adjustments.

Output:-
    The final output of OCR is typically editable and searchable text that can be used for various purposes, 
    such as data entry, document indexing, text-to-speech conversion, translation, and more.""")

    with col2:
        
            st.write("""
    # Welcome to BizCardX
    
    BizCardX is a tool for extracting business card data using OCR.
    
    ## Instructions
    - To get started, click on "Upload an Image" in the menu above.
    - You can upload an image of a business card, and BizCardX will extract information from it.
    - After extracting the information, you can choose to save it to a database, modify it, or delete it.
    
    ### About
    This app is designed to simplify the process of digitizing business card information. It utilizes OCR technology to extract text from images and stores the extracted data in a database.
    """)
            
            st.write("""
        ## Technology Used              
            
    #### Streamlit (Frontend):

    - Streamlit is used to create the visual interface that users interact with.
    - It makes it easy to build web applications using Python.
    - With Streamlit, we can add buttons, input fields, and other interactive elements to the application.

    #### Python (Backend):

    - Python handles the behind-the-scenes logic of the application.
    - It processes data, interacts with the database, and performs tasks like image processing.
    - Python libraries like Pandas, NumPy, and EasyOCR help with data manipulation and OCR functionality.

    #### PostgreSQL (Database):

    - PostgreSQL is the database where we store the extracted data from business cards.
    - It stores information like names, contact numbers, and addresses.
    - Python code connects to the PostgreSQL database to save, retrieve, modify, or delete data.""")       
            
    st.write("""
        ### Applications of OCR
Document Digitization: OCR is widely used to convert printed documents into digital formats, making them easily accessible and searchable.
Data Extraction: OCR can extract specific information from documents, such as invoices, forms, and business cards, for automated data entry into databases or systems.
Accessibility: OCR technology enables the conversion of printed text into accessible formats for visually impaired individuals, such as converting printed books into electronic Braille or speech.
Automated Processing: OCR facilitates automation in industries like finance, healthcare, and logistics by enabling the extraction and processing of data from various documents and forms.)
""")            
            
    
    
elif Menu == "Upload an Image":

    with st.container(border=True):

        upload_file = st.file_uploader("Upload a File:", type=["png","jpg","jpeg"]) #here we uploading the image to extract text from it

        col1, col2 = st.columns(2)
    
        with col1:
                
            if upload_file is not None:
                image = Image.open(upload_file)
                st.image(image, caption='Uploaded Business Card Image', use_column_width=True)
                

        with col2:
            
                if st.button('Extract Information'):
                    with st.spinner('Please Wait Extracting text from image...'):
                        ExText_data,Input_image = Extract_data(image)
                        result_dict = Extracteddata_dict(ExText_data)
                        st.write(result_dict)

        button2 =  st.button('Convert to DataFrame')            
        
        if button2:
            with st.spinner('Please Wait while converting Extracted Data to DataFrame...'):
                ExText_data,Input_image = Extract_data(image)
                result_dict = Extracteddata_dict(ExText_data)
                dataframe1 = pd.DataFrame(result_dict,index=[0])
                
                # Convert the input image to bytes
                img_bytes = BytesIO()
                Input_image.save(img_bytes, format='PNG')
                img_bytes = img_bytes.getvalue()
                
                # Store the image bytes in the DataFrame
                dataframe1['Image'] = [img_bytes]

                st.dataframe(dataframe1)

        button3 =  st.button("Save to Database")
        
        if button3:
            with st.spinner('Please Wait while Saving Extracted Data in Database...'):
                Data_Base = psycopg2.connect(host = "localhost",
                            user = "postgres",
                            password = "BNandy30",
                            port = "5432",
                            database = "Bizcardx") # it is the connection to run SQL in backend

                cursor = Data_Base.cursor() #Cursor is a Temporary Memory or Temporary Work Station.

                ExText_data,Input_image = Extract_data(image)
                result_dict = Extracteddata_dict(ExText_data)
                dataframe1 = pd.DataFrame(result_dict,index=[0])
                
                # Convert the input image to bytes
                img_bytes = BytesIO()
                Input_image.save(img_bytes, format='PNG')
                img_bytes = img_bytes.getvalue()
                
                # Store the image bytes in the DataFrame
                dataframe1['Image'] = [img_bytes]
                saveexdata = saveExtracteddata_database(dataframe1)
                st.dataframe(saveexdata)

elif Menu == "Modify Or Delete": 
    
        Data_Base = psycopg2.connect(host = "localhost",
                    user = "postgres",
                    password = "BNandy30",
                    port = "5432",
                    database = "Bizcardx") # it is the connection to run SQL in backend

        cursor = Data_Base.cursor() #Cursor is a Temporary Memory or Temporary Work Station.

        select_query = "SELECT * FROM BussinesCarddetails"

        cursor.execute(select_query)
        Data_Base.commit()
        BussinesCarddetails_table = cursor.fetchall()


        BussinesCarddetails_table = pd.DataFrame(BussinesCarddetails_table, columns = ('Name','Designation','Contact Number',
                                            'Website URL','Email id','Address','Company Name','State and Pincode','Image'))

        col1,col2 = st.columns(2)

        with col1:

           Data_Modify = st.selectbox("****Select the Data to Modifiy or Delete:****",BussinesCarddetails_table["Name"])

        #here we storing the data to modify as dataframe2
        dataframe2 = BussinesCarddetails_table[BussinesCarddetails_table["Name"] == Data_Modify]

        #Here copying those data to another dataframe3 where the modified data will save
        dataframe3 = dataframe2.copy()

        col1,col2 = st.columns(2)

        with col1:

            Modify_Name = st.text_input("NAME", dataframe2["Name"].unique()[0])
            Modify_Designation = st.text_input("DESIGNATION", dataframe2["Designation"].unique()[0])
            Modify_contactno = st.text_input("CONTAACT_NUMBER", dataframe2["Contact Number"].unique()[0])
            Modify_URL = st.text_input("WEBSITE_URL", dataframe2["Website URL"].unique()[0])
            Modify_Emailid = st.text_input("EMAILID", dataframe2["Email id"].unique()[0])

            dataframe3["Name"] = Modify_Name
            dataframe3["Designation"] = Modify_Designation
            dataframe3["Contact Number"] = Modify_contactno
            dataframe3["Website URL"] = Modify_URL
            dataframe3["Email id"] = Modify_Emailid

        with col2:

            Modify_Address = st.text_input("ADDRESS", dataframe2["Address"].unique()[0])
            Modify_Companyname = st.text_input("COMPANY_NAME", dataframe2["Company Name"].unique()[0])
            Modify_state_Pin = st.text_input("STATE_AND_PINCODE", dataframe2["State and Pincode"].unique()[0])
            Modify_Image = st.text_input("IMAGE", dataframe2["Image"].unique()[0])
            
            dataframe3["Address"] = Modify_Address
            dataframe3["Company Name"] = Modify_Companyname
            dataframe3["State and Pincode"] = Modify_state_Pin
            dataframe3["Image"] = Modify_Image

        col1, col2 = st.columns(2) 

        with col1:

            button4 = st.button("MODIFY", use_container_width = True)

            if button4:

                        Data_Base = psycopg2.connect(host = "localhost",
                                    user = "postgres",
                                    password = "BNandy30",
                                    port = "5432",
                                    database = "Bizcardx") # it is the connection to run SQL in backend

                        cursor = Data_Base.cursor() #Cursor is a Temporary Memory or Temporary Work Station.

                        update_query = """UPDATE BussinesCarddetails 
                                SET Name = %s, 
                                    Designation = %s, 
                                    "Contact Number" = %s, 
                                    "Website URL" = %s, 
                                    "Email ID" = %s, 
                                    Address = %s, 
                                    "Company Name" = %s, 
                                    "State and Pincode" = %s, 
                                    Image = %s 
                                WHERE Name = %s"""
                
                # Extract the modified data from the dataframe
                        modified_data = (
                            Modify_Name, Modify_Designation, Modify_contactno, Modify_URL, Modify_Emailid,
                            Modify_Address, Modify_Companyname, Modify_state_Pin, Modify_Image, Data_Modify)
                        
                        cursor.execute(update_query, modified_data)
                        Data_Base.commit()

                        st.dataframe(dataframe3)
                        st.success("Data modified successfully")

        with col2:
                    
            button5 = st.button("DELETE", use_container_width = True)

            if button5:

                        Data_Base = psycopg2.connect(host = "localhost",
                                    user = "postgres",
                                    password = "BNandy30",
                                    port = "5432",
                                    database = "Bizcardx") # it is the connection to run SQL in backend

                        cursor = Data_Base.cursor() #Cursor is a Temporary Memory or Temporary Work Station.

                        delete_query = f"""Delete From BussinesCarddetails WHERE Name = '{Data_Modify}' """
                        
                        cursor.execute(delete_query)
                        Data_Base.commit()

                        st.success("Data Deleted successfully")          
