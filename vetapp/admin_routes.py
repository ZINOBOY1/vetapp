import os
import secrets
from vetapp import app
from flask import render_template, flash, redirect, url_for, session, request, make_response
from vetapp.models import Customer, db, products, Admin, breed, categories,Orders
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from vetapp.forms import SignForm, AdminRegistrationForm, AddProductForm
from flask_wtf.csrf import CSRFError

@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

def is_admin_logged_in():
    return 'admin_id' in session

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('admin_email')
        password = request.form.get('admin_password')
        admin = Admin.query.filter_by(admin_email=email).first()
        
        if admin and check_password_hash(admin.admin_password, password):
            session['admin_id'] = admin.admin_id  
            flash('Login successful!', 'success')
            return redirect(url_for('admin_home'))
        else:
            flash('Invalid email or password!', 'error')

    return render_template('registration/adminlogin.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)  
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/')
def admin_home():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))

    customers = db.session.query(Customer).all()
    recent_orders = Orders.query.order_by(Orders.order_id.desc()).limit(5).all() 

    return render_template('admin/index.html', customers=customers, recent_orders=recent_orders)

@app.route('/admin/register', methods=['GET', 'POST'])
def register():
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.admin_password.data)
        new_admin = Admin(
            admin_fullname=form.admin_fullname.data,
            admin_email=form.admin_email.data,
            admin_password=hashed_password
        )
        db.session.add(new_admin)
        db.session.commit()
        flash('Admin registered successfully!', 'success')
        return redirect(url_for('admin_home'))
    return render_template('registration/adminregister.html', form=form)

@app.route('/admin/addproduct/', methods=['GET', 'POST'])
def add_product():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))

    pform = AddProductForm()
    # Populate the categories and breeds for the select fields
    pform.category_id.choices = [(category.category_id, category.category_name) for category in categories.query.all()]
    pform.breed_id.choices = [(breed.breed_id, breed.breed_name) for breed in breed.query.all()]

    if request.method == 'POST':
        if pform.validate_on_submit():
            name = pform.name.data
            description = pform.description.data
            price = pform.price.data
            picture = request.files.get('picture')
            category_id = pform.category_id.data
            breed_id = pform.breed_id.data

            if picture and picture.filename:
                original_file = secure_filename(picture.filename)
                ext = os.path.splitext(original_file)[1]
                new_filename = secrets.token_hex(10) + ext
                file_path = os.path.join('vetapp/static/uploads/', new_filename)
                picture.save(file_path)
            else:
                new_filename = None

            new_product = products(
                product_name=name,
                description=description,
                product_price=price,
                product_picture=new_filename,
                category_id=category_id,
                breed_id=breed_id
            )

            try:
                db.session.add(new_product)
                db.session.commit()
                flash('Product added successfully!', 'success')
                return redirect(url_for('add_product'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while adding the product. Please try again.', 'error')
                print(e)

    
    result = db.session.execute(db.text("SELECT product_id, product_name, product_price, date_added FROM products"))
    r = result.fetchall()
    breeds = breed.query.all()
    return render_template('admin/addproduct.html', pform=pform, result=r, breeds=breeds)

@app.route('/breed/')
def index():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
    breeds = breed.query.all()
    category = categories.query.all()
    return render_template('admin/manage_breeds.html', categories=category, breeds=breeds, mode='view')

@app.route('/add', methods=['GET', 'POST'])
def add_breed():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
    name = request.form.get('name')
    category_id = request.form.get('category_id')
    if name and category_id:
        new_breed = breed(breed_name=name, category_id=category_id)
        db.session.add(new_breed)
        db.session.commit()
        flash('Breed added successfully!')
    else:
        flash('Name is required!')
    return redirect('/breed/')

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_breed(id):
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
    breeds = breed.query.get_or_404(id)
    db.session.delete(breeds)
    db.session.commit()
    flash('Breed deleted successfully!')
    return redirect('/breed/')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_breed(id):
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
    breeds = breed.query.get_or_404(id)
    category = categories.query.all()
    if request.method == 'POST':
        breeds.breed_name = request.form.get('name')
        breeds.category_id = request.form.get('category_id')
        db.session.commit()
        flash('Breed updated successfully!')
        return redirect('/breed/')
    return render_template('admin/manage_breeds.html', categories=category, breed=breeds, mode='update')




