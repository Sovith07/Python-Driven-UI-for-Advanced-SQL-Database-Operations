select * from products;

select * from shipments;
select * from stock_entries;



-- 1 Total suppliers

select count(distinct supplier_id) as Total_suppliers from suppliers;

-- 2 Total Products

select count(distinct product_id) as Total_products from products;

-- 3 Total categories dealing

select count(distinct category) as Total_categories_dealing from products;

-- 4 Total sales value made in last 3 months

select round(sum(abs(se.change_quantity)*p.price),2) as total from stock_entries se inner join products p on se.product_id=p.product_id
where se.change_type='Sale' and entry_date>=(select date_sub(max(entry_date),interval 3 month) from stock_entries);

-- 5 Total restock value made in last 3 months

select round(sum(abs(se.change_quantity)*p.price),2) as total from stock_entries se inner join products p on se.product_id=p.product_id
where se.change_type='Restock' and entry_date>=(select date_sub(max(entry_date),interval 3 month) from stock_entries);

-- 6 

select count(distinct product_name) as products_left  from products where stock_quantity<reorder_level and product_id  not in 
(select distinct product_id from reorders where status='Pending' ) ;
  
  
  -- 7  Supplier Cntact details
  
  select supplier_id,contact_name,email,phone from suppliers;
  
  -- 8 Product with supplies and stock
  
  select p.product_name,s.supplier_name,p.stock_quantity,p.reorder_level from suppliers s inner join products p 
  on s.supplier_id=p.supplier_id order by p.product_name asc;
  
  -- 9 Prodcuts Needing  reorder

select product_name,stock_quantity,reorder_level from products where stock_quantity<reorder_level

-- 10 Add new product

delimiter $$
create procedure AddNewProductManualID(
in p_name varchar(255),
in p_category varchar(255),
in p_price decimal(10,2),
in  p_stock int,
in  p_reorder int,
in p_supplier int
)

Begin
 declare new_prod_id int;
 declare new_shipment_id int;
 declare new_entry_id int;
 
 SELECT MAX(product_id) + 1 INTO new_prod_id FROM products;
 INSERT INTO products (product_id,product_name,category,price,stock_quantity,reorder_level,supplier_id)
    VALUES (new_prod_id,p_name,p_category,p_price,p_stock,p_reorder,p_supplier);

  SELECT MAX(shipment_id) + 1 INTO new_shipment_id FROM shipments;
  INSERT INTO shipments (shipment_id,product_id,supplier_id,quantity_received,shipment_date)
    VALUES (new_shipment_id,new_prod_id,p_supplier,p_stock,CURDATE());
    
  SELECT MAX(entry_id) + 1 INTO new_entry_id FROM stock_entries;
  INSERT INTO stock_entries (entry_id,product_id,change_quantity,change_type,entry_date)
  VALUES (new_entry_id,new_prod_id,p_stock,'Restock',CURDATE());
  
  End $$
  delimiter;

call AddNewProductManualID('Smart Watch','Electronics',99.99,100,25,5)

select * from products where product_name='Smart Watch'
select * from shipments  where product_id=201
select * from stock_entries  where product_id=201
 
-- distinct categories

select distinct category from products order by category asc

-- suppliers name

select supplier_id,supplier_name from suppliers;

-- find product history [shipment,sales,purchase]

create view new_table as(
with cte as
(select product_id,shipment_date as record_date,quantity_received as quantity,'Shipment' as  record_type,null as change_type from shipments union all
select product_id,entry_date as record_date,change_quantity as quantity,'Stock_entry' as record_type,change_type from stock_entries)
select c.*,p.supplier_id from products p inner join cte c on p.product_id=c.product_id)

-- product name

select product_id,  product_name  from products;

-- place reorder
select * from reorders
insert into rerorders(reorder_id,product_id,reorder_quantity,reorder_date,status)

-- receive reorder

DELIMITER $$

create procedure MarkReorderAsReceived(
in r_id int)
begin 
declare p_id int;
declare qty int;
declare sup_id int;
declare sip_id int;
declare e_id int;

start Transaction;
select product_id,reorder_quantity into p_id,qty from reorders where 
reorder_id=r_id;

select supplier_id into sup_id from products where product_id=p_id;

update reorders set status="Received"
where reorder_id=r_id;

update products set stock_quantity=stock_quantity+qty where product_id=p_id;


select max(shipment_id)+1 into sip_id from shipments;
insert into shipments(shipment_id,product_id,supplier_id,quantity_received,shipment_date)
values(sip_id,p_id,sup_id,qty,curdate());

select max(entry_id)+1 into e_id from stock_entries;
INSERT INTO stock_entries (entry_id,product_id,change_quantity,change_type,entry_date)
values(e_id,p_id,qty,'Restock',curdate());

commit;
end$$
delimiter;

select * from reorders
select r.reorder_id,p.product_name from reorders r inner join products p on r.product_id=p.product_id where r.status='Ordered'; 
