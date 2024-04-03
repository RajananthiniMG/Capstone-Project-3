# Capstone-Project-3
BizCardX: Extracting Business Card Data with OCR

## BizCardX
BizCardX is a web application for extracting business card data using OCR (Optical Character Recognition). It allows users to upload an image of a business card, extract information from it, and save the extracted data to a PostgreSQL database. Users can also modify or delete the extracted data as needed.

## Features
- Upload an image of a business card and extract text using OCR.
- Organize extracted data into categories such as name, designation, contact number, email id, etc.
- Save extracted data to a PostgreSQL database.
- Modify or delete extracted data from the database.

## Technologies Used
Streamlit: Frontend framework for building the web application interface.
Python: Backend programming language for processing data and interacting with the database.
PostgreSQL: Database management system for storing extracted business card data.
EasyOCR: Python library for optical character recognition, used to extract text from images.
Pandas: Python library for data manipulation and analysis.
psycopg2: Python library for PostgreSQL database connectivity.

## Usage
Open the web application in your browser.
Choose an option from the menu:
"Home": Provides information about OCR and the application.
"Upload an Image": Allows you to upload a business card image, extract data, and save it to the database.
"Modify or Delete": Allows you to modify or delete extracted data from the database.
Follow the instructions on the respective pages to perform the desired actions.
