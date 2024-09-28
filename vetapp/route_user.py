import random
from vetapp import app, API_KEY
from flask import render_template,flash,redirect,url_for,session,request,jsonify
from vetapp.models import Customer,db,products,Orders,Order_item,Payment,breed,categories
from werkzeug.security import generate_password_hash,check_password_hash
from vetapp.forms import SignForm
from flask_wtf.csrf import CSRFError
from decimal import Decimal
import json
import requests  



@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

def get_resort_byid(id):
    data = Customer.query.get(id)
    return data

@app.route('/')
def home_page():
    # Query all active customers
    customer_info = db.session.query(Customer).filter(Customer.status == 'active').all()
    
    # Retrieve customer details if customer_id is present in the session
    customer_id = session.get('customer_id')
    if customer_id:
        resort_deets = db.session.query(Customer).filter_by(customer_id=customer_id).first()
    else:
        resort_deets = None
    
    
    Products = db.session.query(products).limit(3).all()

    
    return render_template('user/index.html',resort_deets=resort_deets,customer_info=customer_info,products=Products)




@app.route('/vetapp/signup/',methods=['GET','POST'])
def signuup():
    sign = SignForm()
    if sign.validate_on_submit():
        name = sign.name.data
        email = sign.email.data
        password = sign.password.data
        address = sign.address.data

        hashed = generate_password_hash(password)

        sign_in = Customer(customer_fullname=name,customer_email=email,customer_password=hashed,customer_address=address)

        try:
            ext_customer = db.session.query(Customer).filter(Customer.customer_email==email).first()
            if ext_customer:
                 flash('the email is already in use, choose another please','error')
                 return redirect('/vetapp/signup')
            
            db.session.add(sign_in)
            db.session.commit()

            customer_id = sign_in.customer_id
            session['customer_id'] = customer_id
            flash('Welcome, an account has been created for you')
            return redirect('/') 
        
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect('/vetapp/signup/')
        
    return render_template('registration/signup.html',register=sign)





@app.route('/vetapp/login/', methods=['GET', 'POST'])
def login_app():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pass')
        
        customer = db.session.query(Customer).filter(Customer.customer_email == email).first()
        
        if customer:
            hashed_password = customer.customer_password
            if check_password_hash(hashed_password, password):
                
                session['customer_id'] = customer.customer_id
                
               
                resort_id = session.get('resort_id')
                if resort_id:
                    resortdeets = get_resort_byid(resort_id)
                else:
                    resortdeets = None
                return redirect(url_for('home_page'))
            else:
                flash('Incorrect password', 'error')
        else:
            flash('Email not found', 'error')
    
    return render_template('registration/signin.html')

    



@app.route('/vetapp/logout/')
def center_logout():
    if session.get('customer_id') !=None:
        session.pop('customer_id')
    flash('You are now logged out','success')
    return redirect('/vetapp/login/')

@app.route('/add_to_cart/<int:product_id>', methods=['GET','POST'])
def add_to_cart(product_id):
    customer_id = session.get('customer_id')
    if not customer_id:
        return jsonify({'status': 'error', 'message': 'You need to log in to add items to your cart.'}), 401

    quantity = int(request.form.get('quantity', 1))
    product = products.query.get(product_id)
    if not product:
       return jsonify({'status': 'error', 'message': 'Product not found'}), 404

    # create an order for the customer
    order = Orders.query.filter_by(customer_id=customer_id).first()
    if not order:
        order = Orders(customer_id=customer_id, order_total=0)
        db.session.add(order)
        db.session.commit()

    # Check if the product is already in the order
    
    product = products.query.get(product_id)
    product_price = Decimal(product.product_price)
    if product:
            new_item = Order_item(order_id=order.order_id, product_id=product_id, quantity=quantity,
                                 amount=quantity * product_price )
            db.session.add(new_item)

    # Update order total
    order.order_total = sum(item.amount for item in Order_item.query.filter_by(order_id=order.order_id).all())
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Item added to cart successfully!'})

@app.route('/view_cart')
def view_cart():
    if 'customer_id' not in session:
        return redirect('/vetapp/login/') 

    customer_id = session['customer_id']
    
    order = Orders.query.filter_by(customer_id=customer_id).first()
    if not order:
        return render_template('cart.html', cart_items=[], total_amount=0)

    # Join Order_item with Products to get product details
    cart_items = (
        db.session.query(Order_item,products).join(products, Order_item.product_id == products.product_id).filter(Order_item.order_id == order.order_id).all()
    )
    total_amount = sum(item[0].amount for item in cart_items) 
    resort_deets = db.session.query(Customer).get(customer_id)

    return render_template('cart.html', cart_items=cart_items, total_amount=total_amount, resort_deets=resort_deets)


@app.route('/aboutproduct/<int:id>',methods=['GET','POST'])
def about_product_page(id):
    if session.get('customer_id') != None:
        rid = session.get('customer_id')
        resort_deets = db.session.query(Customer).get(rid)
    else:
        resort_deets = None
    product = db.session.query(products).get(id)
    if product is None:
        return "Product not found", 404
    return render_template('aboutproduct.html',resort_deets=resort_deets,product=product)


@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'customer_id' not in session:
        return redirect('/vetapp/login/')

    customer_id = session['customer_id']
    order = Orders.query.filter_by(customer_id=customer_id).first()

    if order:
        item = Order_item.query.filter_by(product_id=product_id, order_id=order.order_id).first()
        if item:
            try:
                db.session.delete(item)
                db.session.commit()
                order.order_total = sum(i.amount for i in Order_item.query.filter_by(order_id=order.order_id).all())
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error occurred: {e}")  
                return redirect('/error') 
    return redirect('/view_cart') 

@app.route('/product/page/',methods=['GET','POST'])
def product_page_view():
    customer_id = session.get('customer_id')
    if customer_id:
        resort_deets = db.session.query(Customer).filter_by(customer_id=customer_id).first()
    else:
        resort_deets = None
    breeds = breed.query.all() 
    category = categories.query.all() 
    product = products.query.all() 
    return render_template('user/product_page.html',resort_deets=resort_deets,breeds=breeds, categories=category,product=product)

@app.route('/get_products_by_breed/<int:breed_id>', methods=['GET'])
def get_products_by_breed(breed_id):
    product = products.query.filter_by(breed_id=breed_id).all()  
    product_list = [
        {
            'product_name': product.product_name,
            'product_picture': product.product_picture,
            'description': product.description,
            'product_price': product.product_price,
            'product_id': product.product_id
        }
        for product in product
    ]
    return jsonify({'products': product_list})


@app.route('/get_all_products', methods=['GET'])
def get_all_products():
    product = products.query.all() 
    product_list = [
        {
            'product_name': product.product_name,
            'product_picture': product.product_picture,
            'description': product.description,
            'product_price': product.product_price,
            'product_id': product.product_id
        }
        for product in product
    ]
    return jsonify({'products': product_list})



@app.route('/get_products_by_category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    product = products.query.filter_by(category_id=category_id).all()
    products_list = [{
       'product_name': product.product_name,
       'product_picture': product.product_picture,
       'description': product.description,
       'product_price': product.product_price,
       'product_id': product.product_id
    } for product in product]
    
    return jsonify({'products': products_list})


# integrate paystack

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    customer_id = session.get('customer_id')
    
    if not customer_id:
        flash('You need to log in to checkout.', 'warning')
        return redirect('/vetapp/login/')

    order = Orders.query.filter_by(customer_id=customer_id).first()
    if not order:
        flash('No active order found. Please add items to your cart before checking out.', 'warning')
        return redirect('/view_cart')

    if request.method == 'POST':
        total_amount = sum(item.amount for item in Order_item.query.filter_by(order_id=order.order_id).all())
        
        ref = random.randint(1000000000000000, 9000000000000000)
        ref_no = f"VP{ref}"
        payment = Payment(pay_amount=total_amount, order_id=order.order_id,
                          customer_id=customer_id, pay_ref=ref_no)
        db.session.add(payment)
        db.session.commit()

        #paystack url
        
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Content-Type": "application/json",
            "Authorization":API_KEY
        }
        data = {
            "email": Customer.query.get(customer_id).customer_email,
            "amount": int(total_amount * 100), 
            "reference": ref_no,
            "callback_url":'http://127.0.0.1:5151/payment_callback/'
        }
        
        resp_json = requests.post(url,headers=headers,data=json.dumps(data))
        print(resp_json.json())
        resp_dict = resp_json.json()
        
        if resp_dict and resp_dict.get('status') == True:
            auth_url = resp_dict['data']['authorization_url']
            return redirect(auth_url)
        else:
            flash('Unable to initiate payment. Please try again.', 'danger')
            return redirect('/checkout')

    resort_deets = Customer.query.get(customer_id) if customer_id else None
    total_amount = sum(item.amount for item in Order_item.query.filter_by(order_id=order.order_id).all())
    
    return render_template('checkout.html', total_amount=total_amount, resort_deets=resort_deets)



@app.route('/vetplus/paystack')
def pay_ment():
    ref = session.get('ref')
    if ref:
        url = f"https://api.paystack.co/transaction/initialize{ref}"
        headers = {"Content-type":"application/json","Authorization":API_KEY}
        pay = Payment.query.filter(Payment.ref==ref).first()
        data = {"amount":pay.pay_amount*100,"reference":pay.pay_ref,"callback_url":"http://127.0.0.1:5151/payment_callback/"}
        resp_json = requests.post(url,headers=headers,data =json.dumps(data))
        
        resp_dict = resp_json.json()
        if resp_dict and resp_dict.get('status') == True:
            auth_url = resp_dict['data']['authorization_url']
            return redirect(auth_url)
        else:
            flash('Please start your payment process again','warning')
            return redirect('/checkout')
    else:
        flash('Please restart again')


@app.route('/payment_callback/', methods=['GET'])
def payment_callback():
    reference = request.args.get('reference')
    
    if reference:
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": "Bearer sk_test_6658b3b7785e0cb90530cd0f3af8671070a4b278"
        }
        resp_json = requests.get(url, headers=headers)
        response_data = resp_json.json()

        # print("Paystack response:", response_data)

        if response_data.get('data') and response_data['data'].get('status') == 'success':
            payment = Payment.query.filter_by(pay_ref=reference).first()
            if payment:
                # print(f"Current status before update: {payment.status}")
                payment.status = 'paid'

                try:
                    db.session.commit()
                    flash('Order placed and payment successful!', 'success')
                    return redirect('/thank_you')  
                except Exception as e:
                    db.session.rollback()
                    flash(f"Error updating payment status: {str(e)}", 'danger')
                    return redirect('/view_cart')
            else:
                flash('Transaction failed: No payment found.', 'warning')
                return redirect('/view_cart')  
        else:
            flash('Payment verification failed.', 'warning')
            return redirect('/view_cart')
    else:
        flash('No payment reference found. Please try again.', 'warning')
        return redirect('/view_cart')

    
@app.route('/thank_you')
def thank_you():
    return render_template('thankyou.html')