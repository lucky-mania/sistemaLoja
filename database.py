import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash
from typing import List, Optional
from models import User, Product, Sale

DATABASE_FILE = 'inventory.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables and default user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT,
            quantidade INTEGER NOT NULL DEFAULT 0,
            valor_compra REAL NOT NULL,
            valor_venda REAL NOT NULL,
            data_entrada DATE NOT NULL,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            valor_venda REAL NOT NULL,
            data_venda DATE NOT NULL,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    ''')
    
    # Create default admin user if not exists
    cursor.execute('SELECT id FROM usuarios WHERE email = ?', ('admin@admin.com',))
    if not cursor.fetchone():
        senha_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha_hash)
            VALUES (?, ?, ?)
        ''', ('Administrador', 'admin@admin.com', senha_hash))
    
    conn.commit()
    conn.close()

# User operations
def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return User(
            id=row['id'],
            nome=row['nome'],
            email=row['email'],
            senha_hash=row['senha_hash'],
            criado_em=row['criado_em']
        )
    return None

def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return User(
            id=row['id'],
            nome=row['nome'],
            email=row['email'],
            senha_hash=row['senha_hash'],
            criado_em=row['criado_em']
        )
    return None

# Product operations
def get_all_products(search: str = "", page: int = 1, per_page: int = 10) -> tuple[List[Product], int]:
    """Get all products with pagination and search"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build query with search
    where_clause = ""
    params = []
    if search:
        where_clause = "WHERE nome LIKE ? OR categoria LIKE ?"
        params = [f'%{search}%', f'%{search}%']
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM produtos {where_clause}"
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]
    
    # Get paginated results
    offset = (page - 1) * per_page
    query = f"SELECT * FROM produtos {where_clause} ORDER BY criado_em DESC LIMIT ? OFFSET ?"
    cursor.execute(query, params + [per_page, offset])
    rows = cursor.fetchall()
    conn.close()
    
    products = []
    for row in rows:
        products.append(Product(
            id=row['id'],
            nome=row['nome'],
            categoria=row['categoria'],
            quantidade=row['quantidade'],
            valor_compra=row['valor_compra'],
            valor_venda=row['valor_venda'],
            data_entrada=row['data_entrada'],
            criado_em=row['criado_em']
        ))
    
    return products, total

def get_product_by_id(product_id: int) -> Optional[Product]:
    """Get product by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM produtos WHERE id = ?', (product_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return Product(
            id=row['id'],
            nome=row['nome'],
            categoria=row['categoria'],
            quantidade=row['quantidade'],
            valor_compra=row['valor_compra'],
            valor_venda=row['valor_venda'],
            data_entrada=row['data_entrada'],
            criado_em=row['criado_em']
        )
    return None

def create_product(product: Product) -> int:
    """Create a new product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO produtos (nome, categoria, quantidade, valor_compra, valor_venda, data_entrada)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (product.nome, product.categoria, product.quantidade, 
          product.valor_compra, product.valor_venda, product.data_entrada))
    product_id = cursor.lastrowid or 0
    conn.commit()
    conn.close()
    return product_id

def update_product(product: Product) -> bool:
    """Update a product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE produtos 
        SET nome = ?, categoria = ?, quantidade = ?, valor_compra = ?, valor_venda = ?, data_entrada = ?
        WHERE id = ?
    ''', (product.nome, product.categoria, product.quantidade, 
          product.valor_compra, product.valor_venda, product.data_entrada, product.id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def delete_product(product_id: int) -> bool:
    """Delete a product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM produtos WHERE id = ?', (product_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def update_product_quantity(product_id: int, new_quantity: int) -> bool:
    """Update product quantity"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE produtos SET quantidade = ? WHERE id = ?', (new_quantity, product_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

# Sales operations
def create_sale(sale: Sale) -> int:
    """Create a new sale and update stock"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Start transaction
    cursor.execute('BEGIN TRANSACTION')
    
    try:
        # Create sale
        cursor.execute('''
            INSERT INTO vendas (produto_id, quantidade, valor_venda, data_venda)
            VALUES (?, ?, ?, ?)
        ''', (sale.produto_id, sale.quantidade, sale.valor_venda, sale.data_venda))
        sale_id = cursor.lastrowid or 0
        
        # Update product stock
        cursor.execute('''
            UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?
        ''', (sale.quantidade, sale.produto_id))
        
        conn.commit()
        conn.close()
        return sale_id
        
    except Exception:
        conn.rollback()
        conn.close()
        raise

def get_all_sales(page: int = 1, per_page: int = 10) -> tuple[List[Sale], int]:
    """Get all sales with pagination"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute('SELECT COUNT(*) FROM vendas')
    total = cursor.fetchone()[0]
    
    # Get paginated results with product names
    offset = (page - 1) * per_page
    cursor.execute('''
        SELECT v.*, p.nome as produto_nome
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        ORDER BY v.criado_em DESC
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    rows = cursor.fetchall()
    conn.close()
    
    sales = []
    for row in rows:
        sales.append(Sale(
            id=row['id'],
            produto_id=row['produto_id'],
            quantidade=row['quantidade'],
            valor_venda=row['valor_venda'],
            data_venda=row['data_venda'],
            criado_em=row['criado_em'],
            produto_nome=row['produto_nome']
        ))
    
    return sales, total

# Dashboard operations
def get_dashboard_stats() -> dict:
    """Get dashboard statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total products in stock
    cursor.execute('SELECT COUNT(*) FROM produtos WHERE quantidade > 0')
    total_products = cursor.fetchone()[0]
    
    # Total invested value
    cursor.execute('SELECT SUM(valor_compra * quantidade) FROM produtos')
    total_invested = cursor.fetchone()[0] or 0
    
    # Total potential sale value
    cursor.execute('SELECT SUM(valor_venda * quantidade) FROM produtos')
    total_potential = cursor.fetchone()[0] or 0
    
    # Total profit from sales
    cursor.execute('''
        SELECT SUM((v.valor_venda - p.valor_compra) * v.quantidade) as lucro_total
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
    ''')
    total_profit = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total_products': total_products,
        'total_invested': total_invested,
        'total_potential': total_potential,
        'total_profit': total_profit
    }

def get_reports_data(start_date: str = "", end_date: str = "") -> dict:
    """Get reports data with date filtering"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build date filter
    date_filter = ""
    date_params = []
    if start_date and end_date:
        date_filter = "WHERE data_entrada BETWEEN ? AND ?"
        date_params = [start_date, end_date]
    
    # Get product entries
    cursor.execute(f'''
        SELECT 'entrada' as tipo, nome, categoria, quantidade, valor_compra as valor, data_entrada as data
        FROM produtos
        {date_filter}
        ORDER BY data_entrada DESC
    ''', date_params)
    entries = cursor.fetchall()
    
    # Get sales with date filter
    sale_date_filter = ""
    if start_date and end_date:
        sale_date_filter = "WHERE v.data_venda BETWEEN ? AND ?"
    
    cursor.execute(f'''
        SELECT 'saida' as tipo, p.nome, p.categoria, v.quantidade, v.valor_venda as valor, v.data_venda as data
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        {sale_date_filter}
        ORDER BY v.data_venda DESC
    ''', date_params)
    exits = cursor.fetchall()
    
    conn.close()
    
    return {
        'entries': [dict(row) for row in entries],
        'exits': [dict(row) for row in exits]
    }
