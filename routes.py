from flask import render_template, request, redirect, url_for, session, flash, jsonify, make_response
from werkzeug.security import check_password_hash
from datetime import datetime
import csv
import io
from app import app
from database import (
    get_user_by_email, get_user_by_id, get_all_products, get_product_by_id,
    create_product, update_product, delete_product, create_sale, get_all_sales,
    get_dashboard_stats, get_reports_data
)
from models import Product, Sale

def login_required(f):
    """Decorator to require login for protected routes"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    """Redirect to dashboard if logged in, otherwise to login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = get_user_by_email(email)
        
        if user and check_password_hash(user.senha_hash, password):
            session['user_id'] = user.id
            session['user_name'] = user.nome
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha inválidos!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard with statistics"""
    stats = get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)

@app.route('/products')
@login_required
def products():
    """Products listing with pagination and search"""
    page = int(request.args.get('page', 1))
    search = request.args.get('search', '')
    per_page = 10
    
    products_list, total = get_all_products(search, page, per_page)
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('products.html', 
                         products=products_list, 
                         current_page=page, 
                         total_pages=total_pages,
                         search=search,
                         total=total)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """Add new product"""
    if request.method == 'POST':
        try:
            # Parse currency values
            valor_compra = float(request.form['valor_compra'].replace('R$', '').replace('.', '').replace(',', '.'))
            valor_venda = float(request.form['valor_venda'].replace('R$', '').replace('.', '').replace(',', '.'))
            
            product = Product(
                nome=request.form['nome'],
                categoria=request.form['categoria'],
                quantidade=int(request.form['quantidade']),
                valor_compra=valor_compra,
                valor_venda=valor_venda,
                data_entrada=request.form['data_entrada']
            )
            
            # Validate
            if not product.nome or not product.categoria:
                flash('Nome e categoria são obrigatórios!', 'error')
                return render_template('add_product.html')
            
            if product.quantidade <= 0:
                flash('Quantidade deve ser maior que zero!', 'error')
                return render_template('add_product.html')
            
            create_product(product)
            flash('Produto cadastrado com sucesso!', 'success')
            return redirect(url_for('products'))
            
        except ValueError:
            flash('Valores monetários inválidos!', 'error')
            return render_template('add_product.html')
    
    return render_template('add_product.html')

@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Edit product"""
    product = get_product_by_id(product_id)
    if not product:
        flash('Produto não encontrado!', 'error')
        return redirect(url_for('products'))
    
    if request.method == 'POST':
        try:
            # Parse currency values
            valor_compra = float(request.form['valor_compra'].replace('R$', '').replace('.', '').replace(',', '.'))
            valor_venda = float(request.form['valor_venda'].replace('R$', '').replace('.', '').replace(',', '.'))
            
            product.nome = request.form['nome']
            product.categoria = request.form['categoria']
            product.quantidade = int(request.form['quantidade'])
            product.valor_compra = valor_compra
            product.valor_venda = valor_venda
            product.data_entrada = request.form['data_entrada']
            
            # Validate
            if not product.nome or not product.categoria:
                flash('Nome e categoria são obrigatórios!', 'error')
                return render_template('edit_product.html', product=product)
            
            if product.quantidade <= 0:
                flash('Quantidade deve ser maior que zero!', 'error')
                return render_template('edit_product.html', product=product)
            
            update_product(product)
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('products'))
            
        except ValueError:
            flash('Valores monetários inválidos!', 'error')
            return render_template('edit_product.html', product=product)
    
    return render_template('edit_product.html', product=product)

@app.route('/products/delete/<int:product_id>')
@login_required
def delete_product_route(product_id):
    """Delete product"""
    if delete_product(product_id):
        flash('Produto excluído com sucesso!', 'success')
    else:
        flash('Erro ao excluir produto!', 'error')
    return redirect(url_for('products'))

@app.route('/sales')
@login_required
def sales():
    """Sales listing"""
    page = int(request.args.get('page', 1))
    per_page = 10
    
    sales_list, total = get_all_sales(page, per_page)
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('sales.html', 
                         sales=sales_list, 
                         current_page=page, 
                         total_pages=total_pages,
                         total=total)

@app.route('/sales/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    """Add new sale"""
    if request.method == 'POST':
        try:
            produto_id = int(request.form['produto_id'])
            quantidade = int(request.form['quantidade'])
            valor_venda = float(request.form['valor_venda'].replace('R$', '').replace('.', '').replace(',', '.'))
            
            # Check if product exists and has enough stock
            product = get_product_by_id(produto_id)
            if not product:
                flash('Produto não encontrado!', 'error')
                return render_template('add_sale.html')
            
            if product.quantidade < quantidade:
                flash(f'Estoque insuficiente! Disponível: {product.quantidade}', 'error')
                return render_template('add_sale.html')
            
            sale = Sale(
                produto_id=produto_id,
                quantidade=quantidade,
                valor_venda=valor_venda,
                data_venda=request.form['data_venda']
            )
            
            create_sale(sale)
            flash('Venda registrada com sucesso!', 'success')
            return redirect(url_for('sales'))
            
        except ValueError:
            flash('Valores inválidos!', 'error')
            return render_template('add_sale.html')
    
    # Get products for dropdown
    products_list, _ = get_all_products()
    return render_template('add_sale.html', products=products_list)

@app.route('/api/product/<int:product_id>')
@login_required
def get_product_api(product_id):
    """API endpoint to get product details"""
    product = get_product_by_id(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'nome': product.nome,
            'quantidade': product.quantidade,
            'valor_venda': product.valor_venda
        })
    return jsonify({'error': 'Product not found'}), 404

@app.route('/reports')
@login_required
def reports():
    """Reports page"""
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    if start_date and end_date:
        reports_data = get_reports_data(start_date, end_date)
        # Combine and sort all transactions
        all_transactions = reports_data['entries'] + reports_data['exits']
        all_transactions.sort(key=lambda x: x['data'], reverse=True)
    else:
        all_transactions = []
    
    return render_template('reports.html', 
                         transactions=all_transactions,
                         start_date=start_date,
                         end_date=end_date)

@app.route('/reports/export')
@login_required
def export_reports():
    """Export reports to CSV"""
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    if not start_date or not end_date:
        flash('Selecione o período para exportar!', 'error')
        return redirect(url_for('reports'))
    
    reports_data = get_reports_data(start_date, end_date)
    all_transactions = reports_data['entries'] + reports_data['exits']
    all_transactions.sort(key=lambda x: x['data'], reverse=True)
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Tipo', 'Produto', 'Categoria', 'Quantidade', 'Valor', 'Data'])
    
    # Write data
    for transaction in all_transactions:
        writer.writerow([
            transaction['tipo'].title(),
            transaction['nome'],
            transaction['categoria'],
            transaction['quantidade'],
            f"R$ {transaction['valor']:.2f}".replace('.', ','),
            transaction['data']
        ])
    
    # Create response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=relatorio_estoque_{start_date}_{end_date}.csv'
    
    return response
