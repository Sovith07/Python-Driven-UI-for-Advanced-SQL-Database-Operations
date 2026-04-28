import mysql.connector


def connect_to_db():
    return mysql.connector.connect(host='localhost',user='root',
                              password='Sovith@07',database='dumm_project')

connect_to_db().is_connected()



def get_basi_info(cursor):
    queries={"Total suppliers":""" 
    select count(distinct supplier_id) as Total_suppliers from suppliers;
    """,
         
    "TBasic Information'":"""
    select count(distinct product_id) as Total_products from products;
    """,

    "Total categories dealing":"""
      select count(distinct category) as Total_categories_dealing from products;
    """,

    "Total sales value made in last 3 months":"""
    select round(sum(abs(se.change_quantity)*p.price),2) as total from stock_entries se inner join products p on se.product_id=p.product_id
    where se.change_type='Sale' and entry_date>=(select date_sub(max(entry_date),interval 3 month) from stock_entries);
    """,

    "Total restock value made in last 3 months":"""
    select round(sum(abs(se.change_quantity)*p.price),2) as total from stock_entries se inner join products p on se.product_id=p.product_id
    where se.change_type='Restock' and entry_date>=(select date_sub(max(entry_date),interval 3 month) from stock_entries);
    """,

    "Below reorder and no pending":"""
    select count(distinct product_name) as products_left  from products where stock_quantity<reorder_level and product_id  not in 
    (select distinct product_id from reorders where status='Pending' ) ;"""
         
    }

    result={}
    for label , query in queries.items():
      cursor.execute(query)
      row=cursor.fetchone()
      result[label]=list(row.values())[0]


    return result

def get_additional_tables(cursor):
   query={"Suppliers Contact Details": """SELECT supplier_name, contact_name, email, phone FROM suppliers""",
           "Products with Supplier and Stock": """
           SELECT p.product_name,s.supplier_name,p.stock_quantity,p.reorder_level
           FROM products p JOIN suppliers s ON p.supplier_id = s.supplier_id ORDER BY p.product_name ASC
            """,

            "Products Needing Reorder": """
            SELECT product_name, stock_quantity, reorder_level FROM products WHERE stock_quantity <= reorder_level
          """} 
   tables={}
   for label , query in query.items():
      cursor.execute(query)
      tables[label]=cursor.fetchall()

   return tables
  

def add_new_manual(cursor,db,p_name ,p_category,p_price,p_stock,p_reorder,p_supplier):
   pro_call="call AddNewProductManualID(%s,%s,%s,%s,%s,%s)"
   paras=(p_name ,p_category,p_price,p_stock,p_reorder,p_supplier)
   cursor.execute(pro_call,paras)
   db.commit()


def get_categries(cursor):
   cursor.execute("select distinct category from products order by category asc")
   rows=cursor.fetchall()
   return [row['category'] for row in rows]

def get_suppliers(cursor):
   cursor.execute("select supplier_id,supplier_name from suppliers order by supplier_name asc")
   rows=cursor.fetchall()
   return rows

def product_name(cursor):
   cursor.execute("select  product_id,product_name  from products")
   rows=cursor.fetchall()
   return rows


def product_history(cursor,product_id):
   query=("select * from new_table where product_id=%s order by record_date asc")
   cursor.execute(query,(product_id,))
   return cursor.fetchall()


def product_reorder(db,cursor,product_id,reorder_quantity):
   query="""insert into rerorders(reorder_id,product_id,reorder_quantity,reorder_date,status)
    selelct (max(reorder_id))+1,%s,%s,curdate(),"Ordered" """
   cursor.execute(query,(product_id,reorder_quantity))
   db.commit()


def get_pending_reorder(cursor):
   query="select r.reorder_id,p.product_name from reorders r inner join products p on r.product_id=p.product_id"
   cursor.execute(query)
   return cursor.fetchall()

def mark_order_as_received(cursor,db,reorder_id):
   cursor.callproc("MarkReorderAsReceived",[reorder_id])
   db.commit()
