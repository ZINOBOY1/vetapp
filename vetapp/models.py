from datetime import datetime
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import Numeric

db = SQLAlchemy()

class Admin(db.Model):
    admin_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    admin_fullname = db.Column(db.String(255),nullable=False)
    admin_email=db.Column(db.String(255),nullable=False,unique=True)
    admin_password = db.Column(db.String(255),nullable=False)
    last_logged_in = db.Column(db.DateTime,default=datetime.utcnow)


class categories(db.Model):
    category_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    category_name=db.Column(db.String(255),nullable=False)
    breed_id= db.relationship('breed',backref='categories')
    
    
class breed(db.Model):
    breed_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    breed_name=db.Column(db.String(255),nullable=False)
    category_id = db.Column(db.Integer,db.ForeignKey('categories.category_id'))
    



class products(db.Model):
    product_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    product_name = db.Column(db.String(255),nullable=False)
    product_picture = db.Column(db.String(255),nullable=False)
    description = db.Column(db.Text,nullable=True)
    product_price=db.Column(db.String(255),nullable=False)
    date_added = db.Column(db.DateTime,default=datetime.utcnow)
    status =db.Column(db.Enum('active','disabled'),nullable=False, server_default=("active"))
    breed_id = db.Column(db.Integer,db.ForeignKey('breed.breed_id'))
    customer_id = db.Column(db.Integer,db.ForeignKey('customer.customer_id'))
    category_id = db.Column(db.Integer,db.ForeignKey('categories.category_id'))



class Customer(db.Model):
     customer_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
     customer_fullname = db.Column(db.String(255),nullable=False)
     customer_address=db.Column(db.String(255),nullable=False)
     customer_password=db.Column(db.String(255),nullable=False)
     customer_email=db.Column(db.String(255),nullable=False,unique=True)
     date_reg = db.Column(db.DateTime,default=datetime.utcnow)
     status =db.Column(db.Enum('active','disabled'),nullable=False, server_default=("active"))

    #set relationship

     order = db.relationship('Orders',backref='customer')
     product = db.relationship('products',backref='customer')

class Orders(db.Model):
    order_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    order_date=db.Column(db.DateTime,default=datetime.utcnow)
    order_total = db.Column(Numeric(10, 2), nullable=False, default=0)
    items = db.relationship('Order_item', backref='order')

    customer_id = db.Column(db.Integer,db.ForeignKey('customer.customer_id'))

class Order_item(db.Model):
    item_id = db.Column(db.Integer,primary_key=True,autoincrement=True)

    order_id = db.Column(db.Integer,db.ForeignKey('orders.order_id'))
    product_id = db.Column(db.Integer,db.ForeignKey('products.product_id'))

    quantity = db.Column(db.String(255),nullable=False)
    amount = db.Column(db.Numeric(10,2))

class Payment(db.Model):
    pay_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pay_amount = db.Column(Numeric(10, 2))  # Numeric type for payment amount
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    status = db.Column(db.Enum('pending','paid','failed'),nullable=False, server_default=("pending")) 
    date_pay = db.Column(db.DateTime, default=datetime.utcnow)
    pay_ref = db.Column(db.String(255), nullable=False)




    
