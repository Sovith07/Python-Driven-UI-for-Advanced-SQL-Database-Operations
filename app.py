import numpy as np
import pandas as pd
import streamlit as st
from functions import (connect_to_db,get_basi_info,get_additional_tables,add_new_manual,get_categries,get_suppliers,product_name,product_history,
                       product_reorder,get_pending_reorder,mark_order_as_received)

#sidebar

st.sidebar.title('Inventory Management Studio')
option=st.sidebar.radio('Select options:',['Basic Information','Operational Tasks'])


#main space

st.title('Inventory and Supply Chain Dashboard')
db=connect_to_db()
cursor=db.cursor(dictionary=True)

# basic info page

if option=='Basic Information':
    st.header('Basic Metrics')

    # get bsic info
    basic_info=get_basi_info(cursor)

    col=st.columns(3)
    keys=list(basic_info.keys())


    for i in range(3):
        col[i].metric(keys[i],basic_info[keys[i]])


    col=st.columns(3)
    for i in range(3,6):
        col[i-3].metric(keys[i],basic_info[keys[i]])

    st.divider()

# display table

    table=get_additional_tables(cursor)

    for label,values in table.items():
     st.header(label)
     df=pd.DataFrame(values)
     st.dataframe(df)
     st.divider()


elif option=='Operational Tasks':
  st.header('Operational Tasks')
  seleted_task=st.selectbox('Choose a task',['Add new product','Product history','Place reorder','Recieve Reorder'])
  if seleted_task=='Add new product':
     st.header('Add new product')
     categories=get_categries(cursor)
     supplier=get_suppliers(cursor)

     with st.form("Add_product_form"):
        product_name=st.text_input("Product Name")
        product_category=st.selectbox("Category",categories)
        product_price=st.number_input("Product Price",min_value=0.00)
        product_stock=st.number_input("Product Stock",min_value=0,step=1)
        product_reorder=st.number_input("Product Reorder",min_value=0,step=1)
        supplier_ids=[s['supplier_id'] for s in supplier]
        supplier_names=[s['supplier_name'] for s in supplier]
        
        supplier_id=st.selectbox("Supplier",options=supplier_ids,format_func=lambda x:supplier_names[supplier_ids.index(x)])

        submitted=st.form_submit_button('Add New Product')

        if submitted:
         if not product_name:
              st.error('Pls enter Product name')

         else:
            try:
                add_new_manual(cursor,db, product_name,product_category,product_price,product_stock,product_reorder,supplier_id)
                st.success(f"Product {product_name} has been added")

            except Exception as e:
               st.error(f"Error adding the {product_name}")


      ##----------------------------------------------------------         
  if seleted_task=='Product history':
     st.header('Product Inventory History')
     products=product_name(cursor)
     product_ids=[p['product_id'] for p in products]
     product_names=[p['product_name'] for p in products]
     selected_product=st.selectbox("Select product",options=product_names)
     if selected_product:
        selected_product_id=product_ids[product_names.index(selected_product)]
        history_data=product_history(cursor,selected_product_id)

        if history_data:
           df=pd.DataFrame(history_data)
           st.dataframe(df)
        
        else:
           st.info('No history present')

  #---------------------------------
  if seleted_task=='Place reorder':
     st.header('Place an reorder')
     products=product_name(cursor)
     product_ids=[p['product_id'] for p in products]
     product_names=[p['product_name'] for p in products]

     selected_product_name=st.selectbox("Selected a product",product_names)
     reorder_quantity=st.number_input("Reorder_quantity",min_value=1,step=1)

     if st.button("Place reorder"):
        if not selected_product_name:
           st.error("Please enter a product")
        elif reorder_quantity<=0:
           st.error('Reorder Quantity should be greater than 0')
        
        else:
           selected_product_id=product_ids[product_names.index(selected_product)]
           try:
              product_reorder(db,cursor,selected_product_id,reorder_quantity)
              st.success('product succesfully reordered')
           except Exception as e:
               st.error('Error product cannot be reorderded')

    #----------------------------------
  if seleted_task=='Recieve Reorder':
     st.header('Recieve Reorder')
     pending_orders=get_pending_reorder(cursor)
     if not pending_orders:
        st.info("No pending orders to receive")
    
     else:
        pending_product_ids=[p['reorder_id'] for p in pending_orders]
        pending_product_names=[p['product_name'] for p in pending_orders]

        selected_pending_product=st.selectbox("Select reorder to mark as received",options=pending_product_names)

        if selected_pending_product:
           selected_pending_product_id=pending_product_ids[pending_product_names.index(selected_pending_product)]
           
           if st.button("Marks as Received"):
              try:
                 mark_order_as_received(db,cursor,selected_pending_product_id)
                 st.success('product mark as received')
              except Exception as e:
                 st.error('Product cannot be marked')

                 


            
      
                  

        

               
            

# python -m streamlit run code.py
