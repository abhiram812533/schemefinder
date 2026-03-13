import mysql.connector
from werkzeug.security import generate_password_hash

import os

# Database Configuration (using environment variables)
# Defaults are set to the TiDB credentials provided
db_config = {
    'host': os.getenv('DB_HOST', 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com'),
    'user': os.getenv('DB_USER', '4ZdPwsvVAA22Zwg.root'),
    'password': os.getenv('DB_PASSWORD', 'PpzUNJyDdDhBE0z8'),
    'database': os.getenv('DB_NAME', 'test'),
    'port': int(os.getenv('DB_PORT', 4000)),
    'ssl_verify_cert': True,
    'ssl_verify_identity': True
}

def setup():
    try:
        # 1. Connect to MySQL with SSL
        print(f"Connecting to {db_config['host']}...")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # 2. Use Database
        print(f"Using database '{db_config['database']}'...")
        cursor.execute(f"USE {db_config['database']}")
        
        # 3. Create Tables
        print("Creating final tables...")
        
        # users table with all columns
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            username VARCHAR(100) UNIQUE NULL,
            mobile VARCHAR(15) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('admin', 'user', 'customer') DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        print("Table 'users' verified.")

        # schemes table with all columns
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS schemes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            categories TEXT,
            link VARCHAR(255),
            domain_name VARCHAR(255),
            scheme_type VARCHAR(100),
            age_requirement INT DEFAULT 0,
            min_annual_income DECIMAL(15, 2) DEFAULT 0.00,
            caste_requirement VARCHAR(100) DEFAULT 'No Requirement',
            creator_name VARCHAR(255),
            views INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        print("Table 'schemes' verified.")

        # support_chat table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_chat (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            sender_role ENUM('admin', 'user', 'customer') NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )""")
        print("Table 'support_chat' verified.")
        
        # 4. Create Default Admin
        print("Creating admin user (Mobile: 9999999999, Pass: admin123)...")
        admin_mobile = "9999999999"
        admin_pass = generate_password_hash("admin123")
        
        # Check if admin exists
        cursor.execute("SELECT * FROM users WHERE mobile = %s", (admin_mobile,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (name, mobile, password, role) VALUES (%s, %s, %s, 'admin')", 
                           ("System Admin", admin_mobile, admin_pass))
            conn.commit()
            print("Admin created successfully!")
        else:
            print("Admin already exists.")

        cursor.close()
        conn.close()
        print(f"\nSUCCESS: Database setup complete on {db_config['host']}")
        
    except mysql.connector.Error as err:
        print(f"\nERROR: Could not connect to MySQL. {err}")
        print("Note: If using TiDB Cloud, ensure you have an active internet connection.")

if __name__ == "__main__":
    setup()
