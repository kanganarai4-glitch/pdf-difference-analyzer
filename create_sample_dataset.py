"""
create_sample_dataset.py

Generates PDF files with embedded header metadata blocks and product comparisons
for both old (NovaPhone X1) and new (NovaPhone X2) folders.
"""

import fitz 
from pathlib import Path 

OLD_DIR =Path ("uploads/old/nova X1")
NEW_DIR =Path ("uploads/new/nova X2")

def create_pdf (file_path ,metadata ,content_lines ):
    file_path =Path (file_path )
    file_path .parent .mkdir (parents =True ,exist_ok =True )

    doc =fitz .open ()
    page =doc .new_page (width =595 ,height =842 )

    y =50 

    page .insert_text ((50 ,y ),"=== DOCUMENT METADATA HEADER ===",fontsize =12 ,color =(0.1 ,0.2 ,0.5 ))
    y +=20 

    for key ,value in metadata .items ():
        text_line =f"{key }: {value }"
        page .insert_text ((50 ,y ),text_line ,fontsize =10 ,color =(0 ,0 ,0 ))
        y +=15 

    y +=10 
    page .insert_text ((50 ,y ),"=== DOCUMENT CONTENT ===",fontsize =12 ,color =(0.1 ,0.2 ,0.5 ))
    y +=25 


    for line in content_lines :
        page .insert_text ((50 ,y ),line ,fontsize =10 ,color =(0.2 ,0.2 ,0.2 ))
        y +=16 
        if y >800 :
            page =doc .new_page (width =595 ,height =842 )
            y =50 

    doc .save (file_path )
    doc .close ()
    print (f"Created PDF: {file_path }")

def generate_all_datasets ():

    meta_features_old ={
    "Order_ID":"ORD-NP-F01",
    "Order_Date":"2025-06-10",
    "Customer_Name":"Enterprise Retail Partners",
    "City":"San Francisco",
    "State":"California",
    "Region":"West",
    "Country":"United States",
    "Category":"Electronics",
    "Sub_Category":"Mobile Phones",
    "Product_Name":"NovaPhone X1"
    }
    content_features_old =[
    "F001","Basic Voice Assistant","Category: Voice",
    "Simple voice commands for calls and alarms","Available",
    "F002","Dual SIM Support","Category: Connectivity",
    "Supports two physical SIM cards simultaneously","Available",
    "F003","Night Mode Camera","Category: Camera",
    "Basic low-light photo enhancement","Available",
    "F004","Portrait Mode","Category: Camera",
    "Software-based background blur using depth sensor","Available"
    ]

    meta_features_new ={
    "Order_ID":"ORD-NP-F01",
    "Order_Date":"2026-08-01",
    "Customer_Name":"Enterprise Retail Partners",
    "City":"San Francisco",
    "State":"California",
    "Region":"West",
    "Country":"United States",
    "Category":"Electronics",
    "Sub_Category":"Mobile Phones",
    "Product_Name":"NovaPhone X2"
    }
    content_features_new =[
    "F001","AI Voice Assistant","Category: Voice",
    "Context-aware assistant with natural language understanding","Available",
    "F002","Dual SIM + eSIM","Category: Connectivity",
    "Supports two physical SIMs plus an eSIM profile","Available",
    "F003","AI Night Mode Camera","Category: Camera",
    "AI-enhanced multi-frame low-light photography","Available",
    "F004","Advanced Portrait","Category: Mode",
    "Camera Hardware depth sensing with adjustable bokeh in real time","Available"
    ]

    create_pdf (OLD_DIR /"NovaPhone_X1_Features.pdf",meta_features_old ,content_features_old )
    create_pdf (NEW_DIR /"NovaPhone_X2_Features.pdf",meta_features_new ,content_features_new )


    meta_specs_old ={
    "Order_ID":"ORD-NP-S02",
    "Order_Date":"2025-06-10",
    "Customer_Name":"Global Mobile Distributors",
    "City":"Los Angeles",
    "State":"California",
    "Region":"West",
    "Country":"United States",
    "Category":"Electronics",
    "Sub_Category":"Mobile Phones",
    "Product_Name":"NovaPhone X1"
    }
    content_specs_old =[
    "Technical Specifications","NovaPhone X1","2025-06-15","6.1 inches",
    "IPS LCD","1080 x 2340","60Hz","Octa-core 2.4 GHz","6GB","128GB",
    "12MP + 8MP","8MP","4000mAh","18W Wired","Side-mounted","Yes (2D)",
    "IP67","Android 13","No","No","Yes","185g","Midnight Black, Ocean Blue","$249"
    ]

    meta_specs_new ={
    "Order_ID":"ORD-NP-S02",
    "Order_Date":"2026-08-01",
    "Customer_Name":"Global Mobile Distributors",
    "City":"Los Angeles",
    "State":"California",
    "Region":"West",
    "Country":"United States",
    "Category":"Electronics",
    "Sub_Category":"Mobile Phones",
    "Product_Name":"NovaPhone X2"
    }
    content_specs_new =[
    "Technical Specifications","NovaPhone X2","2026-08-10","6.5 inches",
    "AMOLED","1200 x 2640","120Hz","Octa-core 3.2 GHz","8GB","256GB",
    "50MP + 12MP","16MP","5000mAh","45W Wired / 15W Wireless","In-display","Yes (3D IR)",
    "IP68","Android 14","Yes","Yes","No","175g","Graphite, Aurora Green, Pearl White","$399"
    ]

    create_pdf (OLD_DIR /"NovaPhone_X1_Specifications.pdf",meta_specs_old ,content_specs_old )
    create_pdf (NEW_DIR /"NovaPhone_X2_Specifications.pdf",meta_specs_new ,content_specs_new )


    meta_sales_old ={
    "Order_ID":"ORD-NP-D03",
    "Order_Date":"2025-06-10",
    "Customer_Name":"Apex Electronics Wholesalers",
    "City":"Seattle",
    "State":"Washington",
    "Region":"West",
    "Country":"United States",
    "Category":"Electronics",
    "Sub_Category":"Mobile Phones",
    "Product_Name":"NovaPhone X1"
    }
    content_sales_old =[
    "Date","Region","Units_Sold","Revenue","Return_Rate",
    "03","Asia","28700","7150300","2.5",
    "03","Europe","12800","3187200","1.8",
    "03","North America","15200","3784800","2.1",
    "04","Asia","25400","6324600","2.3",
    "04","Europe","10900","2714100","1.9"
    ]

    meta_sales_new ={
    "Order_ID":"ORD-NP-D03",
    "Order_Date":"2026-08-01",
    "Customer_Name":"Apex Electronics Wholesalers",
    "City":"Seattle",
    "State":"Washington",
    "Region":"West",
    "Country":"United States",
    "Category":"Electronics",
    "Sub_Category":"Mobile Phones",
    "Product_Name":"NovaPhone X2"
    }
    content_sales_new =[
    "Date","Region","Units_Sold","Revenue","Return_Rate",
    "03","Asia","41200","16438000","1.6",
    "03","Europe","21300","8498700","1.2",
    "03","North America","24500","9775500","1.4",
    "04","Asia","45600","18194400","1.5",
    "04","Europe","23900","9536100","1.1"
    ]

    create_pdf (OLD_DIR /"NovaPhone_X1_Sales_Data.pdf",meta_sales_old ,content_sales_old )
    create_pdf (NEW_DIR /"NovaPhone_X2_Sales_Data.pdf",meta_sales_new ,content_sales_new )


    meta_reviews_old ={
    "Order_ID":"ORD-NP-R04",
    "Order_Date":"2025-06-10",
    "Customer_Name":"Direct Consumer Analytics",
    "City":"Chicago",
    "State":"Illinois",
    "Region":"Central",
    "Country":"United States",
    "Category":"Electronics",
    "Sub_Category":"Mobile Phones",
    "Product_Name":"NovaPhone X1"
    }
    content_reviews_old =[
    "R001","Priya S.","3","2025-07-01",
    "Camera is okay in daylight but struggles at night.",
    "R002","James T.","2","2025-07-05",
    "No 5G support is a dealbreaker for me.",
    "R003","Marta G.","5","2025-07-10",
    "Simple, reliable, does what I need."
    ]

    meta_reviews_new ={
    "Order_ID":"ORD-NP-R04",
    "Order_Date":"2026-08-01",
    "Customer_Name":"Direct Consumer Analytics",
    "City":"Chicago",
    "State":"Illinois",
    "Region":"Central",
    "Country":"United States",
    "Category":"Electronics",
    "Sub_Category":"Mobile Phones",
    "Product_Name":"NovaPhone X2"
    }
    content_reviews_new =[
    "R001","Priya S.","5","2026-08-05",
    "Night mode camera is incredible, so much better than before!",
    "R002","James T.","5","2026-08-06",
    "Finally 5G, and the speed difference is night and day.",
    "R003","Marta G.","4","2026-08-08",
    "Love it but wish it still had a headphone jack."
    ]

    create_pdf (OLD_DIR /"NovaPhone_X1_Customer_Reviews.pdf",meta_reviews_old ,content_reviews_old )
    create_pdf (NEW_DIR /"NovaPhone_X2_Customer_Reviews.pdf",meta_reviews_new ,content_reviews_new )

if __name__ =="__main__":
    generate_all_datasets ()
