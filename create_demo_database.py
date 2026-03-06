#!/usr/bin/env python3
"""
Create demo SQLite database for DataLine testing
"""

import sqlite3
import json

def create_demo_database():
    """Create SQLite database with sample data for testing"""
    
    # Connect to database (will be created if it doesn't exist)
    conn = sqlite3.connect('demo_database.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            email TEXT,
            city TEXT,
            salary REAL
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product TEXT,
            amount REAL,
            order_date TEXT,
            status TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insert sample users
    users_data = [
        (1, 'Alice Johnson', 28, 'alice@example.com', 'New York', 75000.0),
        (2, 'Bob Smith', 35, 'bob@example.com', 'Los Angeles', 85000.0),
        (3, 'Carol Davis', 24, 'carol@example.com', 'Chicago', 65000.0),
        (4, 'David Wilson', 42, 'david@example.com', 'Houston', 95000.0),
        (5, 'Eva Brown', 31, 'eva@example.com', 'Phoenix', 72000.0)
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO users (id, name, age, email, city, salary)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', users_data)
    
    # Insert sample orders
    orders_data = [
        (1, 1, 'Laptop', 1200.0, '2024-01-15', 'completed'),
        (2, 2, 'Mouse', 25.0, '2024-01-16', 'completed'),
        (3, 1, 'Keyboard', 80.0, '2024-01-17', 'shipped'),
        (4, 3, 'Monitor', 300.0, '2024-01-18', 'pending'),
        (5, 4, 'Headphones', 150.0, '2024-01-19', 'completed'),
        (6, 2, 'Webcam', 60.0, '2024-01-20', 'shipped'),
        (7, 5, 'Desk Chair', 250.0, '2024-01-21', 'completed'),
        (8, 3, 'USB Hub', 20.0, '2024-01-22', 'pending')
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO orders (id, user_id, product, amount, order_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', orders_data)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("✅ Demo database 'demo_database.db' created successfully!")
    print("📊 Tables created: users, orders")
    print("👥 Sample users: 5")
    print("📦 Sample orders: 8")

if __name__ == "__main__":
    create_demo_database()
