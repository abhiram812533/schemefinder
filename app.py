from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'


# Database Configuration (using environment variables)
# Defaults set to TiDB Cloud
db_config = {
    'host': os.getenv('DB_HOST', 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com'),
    'user': os.getenv('DB_USER', '4ZdPwsvVAA22Zwg.root'),
    'password': os.getenv('DB_PASSWORD', 'PpzUNJyDdDhBE0z8'),
    'database': os.getenv('DB_NAME', 'test'),
    'port': int(os.getenv('DB_PORT', 4000)),
    'ssl_verify_cert': True,
    'ssl_verify_identity': True
}

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyByI5U7dRYhDzLZnjgZVtaQwesqUr0I1c4')
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-flash-latest')

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn, None
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return None, str(err)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/admin/login')
def admin_login_page():
    return render_template('admin_login.html')

@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn, err = get_db_connection()
        if not conn:
            flash(f"Database error: {err}", "error")
            return redirect(url_for('customer_login_page'))

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND role = 'customer'", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user'] = user['name']
            session['role'] = 'customer'
            return redirect(url_for('customer_support_portal'))

        flash("Invalid credentials. Please try again.", "error")
        return redirect(url_for('customer_login_page'))

    return render_template('customer_login.html')

@app.route('/customer/portal')
def customer_support_portal():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('customer_login_page'))

    conn, err = get_db_connection()
    if not conn:
        return f"Database error: {err}", 500
    cursor = conn.cursor(dictionary=True)
   
    cursor.execute("""
        SELECT DISTINCT u.id, u.name, u.mobile,
            (SELECT message FROM support_chat WHERE user_id = u.id ORDER BY created_at DESC LIMIT 1) as last_message,
            (SELECT created_at FROM support_chat WHERE user_id = u.id ORDER BY created_at DESC LIMIT 1) as last_time
        FROM users u
        INNER JOIN support_chat sc ON sc.user_id = u.id
        WHERE u.role = 'user'
        ORDER BY last_time DESC
    """)
    conversations = cursor.fetchall()

   
    messages = []
    target_user = None
    selected_user_id = request.args.get('user_id')
    if selected_user_id:
        cursor2 = conn.cursor(dictionary=True)
        cursor2.execute("""
            SELECT c.*, u.name as user_name 
            FROM support_chat c 
            JOIN users u ON c.user_id = u.id 
            WHERE c.user_id = %s 
            ORDER BY c.created_at ASC
        """, (selected_user_id,))
        messages = cursor2.fetchall()
        
        # Also explicitly fetch the user's details in case they have 0 messages
        cursor2.execute("SELECT id, name, mobile FROM users WHERE id = %s", (selected_user_id,))
        target_user = cursor2.fetchone()
        cursor2.close()

    cursor.close()
    conn.close()
    return render_template('customer_portal.html', conversations=conversations, messages=messages, target_user=target_user)



@app.route('/login', methods=['POST'])
def login():
    mobile = request.form.get('mobile')
    password = request.form.get('password')
    role = request.form.get('role', 'user')

    conn, err = get_db_connection()
    if not conn:
        return f"Database Connection Error: {err}. Please ensure MySQL is running and the 'schemefinder' database is created.", 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE (mobile = %s OR username = %s) AND role = %s", (mobile, mobile, role))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['user'] = user['name']
        session['role'] = user['role']
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    
    flash("Invalid credentials. Access Denied.", "error")
    if role == 'admin':
        return redirect(url_for('admin_login_page'))
    return redirect(url_for('index'))

@app.route('/customer/all_users')
def customer_all_users():
    if 'user' in session and session['role'] == 'customer':
        conn, err = get_db_connection()
        if not conn:
            return f"Database Connection Error: {err}", 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE role = 'user' ORDER BY created_at DESC")
        customers = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('customer_analysis.html', customers=customers)
    return redirect(url_for('customer_login_page'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        
        conn, err = get_db_connection()
        if not conn: return f"Error: {err}", 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], old_password):
            hashed_pw = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_pw, session['user_id']))
            conn.commit()
            flash("Password changed successfully!", "success")
        else:
            flash("Incorrect old password.", "error")
        cursor.close()
        conn.close()
        return redirect(url_for('admin_dashboard' if session['role'] == 'admin' else 'user_dashboard'))
    return render_template('change_password.html')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    mobile = request.form.get('mobile')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        flash("Passwords do not match", "error")
        return redirect(url_for('index'))

    conn, err = get_db_connection()
    if not conn:
        return f"Database Connection Error: {err}", 500
    
    cursor = conn.cursor(dictionary=True)
    
    # Duplicate Check
    cursor.execute("SELECT * FROM users WHERE mobile = %s", (mobile,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        flash("Mobile Number already exists! Please login.", "warning")
        return redirect(url_for('index'))

    hashed_pw = generate_password_hash(password)
    cursor.execute("INSERT INTO users (name, mobile, password, role) VALUES (%s, %s, %s, 'user')", 
                   (name, mobile, hashed_pw))
    conn.commit()
    
    # Auto login
    cursor.execute("SELECT * FROM users WHERE mobile = %s", (mobile,))
    user = cursor.fetchone()
    
    session['user_id'] = user['id']
    session['user'] = user['name']
    session['role'] = user['role']
    
    cursor.close()
    conn.close()
    flash("Registration successful! Welcome.", "success")
    return redirect(url_for('user_dashboard'))

@app.route('/admin/add_customer', methods=['GET', 'POST'])
def add_customer_admin():
    if 'user' in session and session['role'] == 'admin':
        if request.method == 'POST':
            name = request.form.get('name')
            mobile = request.form.get('mobile')
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role', 'user')  # 'user' or 'customer'
            
            hashed_pw = generate_password_hash(password)
            conn, err = get_db_connection()
            if not conn:
                return f"Database Connection Error: {err}", 500
            
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (name, mobile, username, password, role) VALUES (%s, %s, %s, %s, %s)", 
                               (name, mobile, username, hashed_pw, role))
                conn.commit()
                flash(f"Account for {name} ({role}) created successfully!", "success")
                return redirect(url_for('admin_dashboard'))
            except Exception as e:
                flash(f"Error adding customer: {str(e)}", "error")
            finally:
                cursor.close()
                conn.close()
        return render_template('add_customer.html')
    return redirect(url_for('admin_login_page'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        new_pw = request.form.get('new_password')
        
        conn, err = get_db_connection()
        if not conn:
            return f"Database Connection Error: {err}", 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE mobile = %s", (mobile,))
        user = cursor.fetchone()
        
        if user:
            hashed_new = generate_password_hash(new_pw)
            cursor.execute("UPDATE users SET password = %s WHERE mobile = %s", (hashed_new, mobile))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        
        cursor.close()
        conn.close()
        return "Mobile number not found", 404
    return render_template('forgot_password.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' in session and session['role'] == 'admin':
        conn, err = get_db_connection()
        if not conn:
            return f"Database Connection Error: {err}", 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM schemes ORDER BY created_at DESC")
        schemes = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('admin_dashboard.html', schemes=schemes)
    return redirect(url_for('admin_login_page'))

@app.route('/admin/add_scheme', methods=['GET', 'POST'])
def add_scheme():
    if 'user' in session and session['role'] == 'admin':
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            link = request.form.get('link')
            domain = request.form.get('domain')
            type = request.form.get('type')
            age = request.form.get('age', 0)
            income = request.form.get('income', 0)
            caste = request.form.get('caste', 'No Requirement')
            creator = request.form.get('creator')
            categories_list = request.form.getlist('categories')
            categories = ", ".join(categories_list)

            conn, err = get_db_connection()
            if not conn:
                return f"Database Connection Error: {err}", 500
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO schemes (name, description, link, domain_name, scheme_type, categories,
                                     age_requirement, min_annual_income, caste_requirement, creator_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, description, link, domain, type, categories, age, income, caste, creator))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('admin_dashboard'))
        return render_template('add_scheme.html')
    return redirect(url_for('admin_login_page'))

@app.route('/admin/analytics')
def admin_analytics():
    if 'user' in session and session['role'] == 'admin':
        conn, err = get_db_connection()
        if not conn:
            return f"Database Connection Error: {err}", 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, views FROM schemes")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data)
    return "Unauthorized", 401

@app.route('/admin/edit_scheme/<int:id>', methods=['GET', 'POST'])
def edit_scheme(id):
    if 'user' in session and session['role'] == 'admin':
        conn, err = get_db_connection()
        if not conn:
            return f"Database Connection Error: {err}", 500
            
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'GET':
            cursor.execute("SELECT * FROM schemes WHERE id = %s", (id,))
            scheme = cursor.fetchone()
            cursor.close()
            conn.close()
            if not scheme:
                flash("Scheme not found.", "error")
                return redirect(url_for('admin_dashboard'))
            return render_template('edit_scheme.html', scheme=scheme)
            
        elif request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            link = request.form.get('link')
            domain = request.form.get('domain')
            type_val = request.form.get('type')
            age = request.form.get('age', 0)
            income = request.form.get('income', 0)
            caste = request.form.get('caste', 'No Requirement')
            creator = request.form.get('creator')
            categories_list = request.form.getlist('categories')
            categories = ", ".join(categories_list)

            cursor.execute("""
                UPDATE schemes 
                SET name=%s, description=%s, link=%s, domain_name=%s, scheme_type=%s, categories=%s,
                    age_requirement=%s, min_annual_income=%s, caste_requirement=%s, creator_name=%s
                WHERE id = %s
            """, (name, description, link, domain, type_val, categories, age, income, caste, creator, id))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Scheme updated successfully!", "success")
            return redirect(url_for('admin_dashboard'))
            
    return redirect(url_for('admin_login_page'))

@app.route('/admin/delete_scheme/<int:id>', methods=['POST'])
def delete_scheme(id):
    if 'user' in session and session['role'] == 'admin':
        conn, err = get_db_connection()
        if not conn:
            return f"Database Connection Error: {err}", 500
            
        cursor = conn.cursor()
        cursor.execute("DELETE FROM schemes WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Scheme deleted successfully!", "success")
        return redirect(url_for('admin_dashboard'))
        
    return redirect(url_for('admin_login_page'))


@app.route('/user/dashboard')
def user_dashboard():
    if 'user' in session and session['role'] == 'user':
        conn, err = get_db_connection()
        if not conn:
            return f"Database Connection Error: {err}", 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM schemes ORDER BY created_at DESC")
        schemes = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('user_dashboard.html', schemes=schemes)
    return redirect(url_for('index'))

@app.route('/user/eligibility', methods=['GET', 'POST'])
def eligibility_check():
    if 'user' in session:
        if request.method == 'POST':
            user_data = {
                'name': request.form.get('name'),
                'age': int(request.form.get('age')),
                'income': float(request.form.get('income')),
                'caste': request.form.get('caste'),
                'occupation': request.form.get('occupation'),
                'land': float(request.form.get('land', 0))
            }

            conn, err = get_db_connection()
            if not conn:
                return f"Database Connection Error: {err}", 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM schemes")
            schemes = cursor.fetchall()
            cursor.close()
            conn.close()

            eligible_schemes = []
            for scheme in schemes:
                # Strict eligibility check - MUST pass all criteria
                age_req = int(scheme['age_requirement'] or 0)
                income_req = float(scheme['min_annual_income'] or 0)
                caste_req = scheme['caste_requirement'] or 'No Requirement'

                # Hard failure conditions - user is NOT eligible
                if age_req > 0 and user_data['age'] < age_req:
                    continue  # Skip this scheme
                if income_req > 0 and user_data['income'] > income_req:
                    continue  # Skip this scheme
                if str(caste_req) != 'No Requirement' and str(user_data['caste']).lower() not in ['all', str(caste_req).lower()]:
                    continue  # Skip this scheme

                # Calculate dynamic match score for eligible schemes
                # Base score for passing hard filters is 60%
                score = 60
                
                # Age proximity bonus (up to 15%)
                if age_req > 0:
                    age_diff = user_data['age'] - age_req
                    # Perfect target age is exactly the requirement to 5 years older
                    if 0 <= age_diff <= 5:
                        score += 15
                    elif 5 < age_diff <= 15:
                        score += 5
                else:
                    score += 10 # Universal age schemes get a slight bump

                # Category match bonus (up to 15%)
                scheme_categories = str(scheme['categories'] or '').lower()
                user_occupation = str(user_data['occupation'] or '').lower()
                
                if scheme_categories and user_occupation:
                    if user_occupation in scheme_categories:
                        score += 15 # Direct category match (e.g. farmer -> Farmer)

                # Income proximity bonus (up to 9%)
                if income_req > 0:
                    # If they make less than half of the max income, it's a perfect target (highest need)
                    if user_data['income'] <= (income_req * 0.5):
                        score += 9
                    elif user_data['income'] <= (income_req * 0.8):
                        score += 4
                
                # Cap score at 99% for a realistic "high probability" feel, or 100%
                percentage = min(score, 99)
                scheme['match_score'] = percentage
                eligible_schemes.append(scheme)

            # Sort by highest match score first
            eligible_schemes.sort(key=lambda x: x['match_score'], reverse=True)

            return render_template('eligibility_results.html', eligible_schemes=eligible_schemes)
        return render_template('eligibility_form.html')
    return redirect(url_for('index'))

@app.route('/scheme/view/<int:scheme_id>')
def view_scheme(scheme_id):
    conn, err = get_db_connection()
    if not conn:
        return f"Database Connection Error: {err}", 500
    cursor = conn.cursor()
    cursor.execute("UPDATE schemes SET views = views + 1 WHERE id = %s", (scheme_id,))
    conn.commit()
    cursor.execute("SELECT link FROM schemes WHERE id = %s", (scheme_id,))
    scheme = cursor.fetchone()
    cursor.close()
    conn.close()
    if scheme:
        return redirect(scheme[0])
    return redirect(url_for('user_dashboard'))

@app.route('/support/chat', methods=['GET', 'POST'])
def support_chat():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn, err = get_db_connection()
    if not conn: return f"Error: {err}", 500
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        message = request.form.get('message')
        cursor.execute("INSERT INTO support_chat (user_id, sender_role, message) VALUES (%s, %s, %s)",
                       (session['user_id'], session['role'], message))
        conn.commit()

    # Get chat history for this user
    user_id = session['user_id']
    if session['role'] == 'admin':
        # Admin can pass user_id via args to see specific user chat
        target_user = request.args.get('target_user')
        if target_user: user_id = target_user
    
    cursor.execute("""
        SELECT c.*, u.name as user_name 
        FROM support_chat c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.user_id = %s 
        ORDER BY c.created_at ASC
    """, (user_id,))
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('support_chat.html', messages=messages, current_user_id=session['user_id'])

@app.route('/customer/reply', methods=['POST'])
def customer_reply():
    if 'user_id' not in session or session.get('role') not in ['customer', 'admin']:
        return redirect(url_for('customer_login_page'))
    
    target_user_id = request.form.get('target_user_id')
    message = request.form.get('message')
    
    conn, err = get_db_connection()
    if not conn: return f"Error: {err}", 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO support_chat (user_id, sender_role, message) VALUES (%s, %s, %s)",
                   (target_user_id, session['role'], message))
    conn.commit()
    cursor.close()
    conn.close()
    
    redirect_url = url_for('customer_support_portal') + f"?user_id={target_user_id}"
    return redirect(redirect_url)

@app.route('/api/chat', methods=['POST'])
def ai_chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get schemes for context to make the AI smarter
    conn, err = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, categories, description FROM schemes")
        schemes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        schemes_context = "\n".join([f"- {s['name']} ({s['categories']}): {s['description']}" for s in schemes])
    else:
        schemes_context = "No specific scheme details available in DB right now."

    system_prompt = f"""
    You are 'SchemeBot', the high-end AI assistant for the 'SchemeFinder' platform. 
    Your job is to assist users in finding government schemes.
    
    Available Schemes in our system:
    {schemes_context}
    
    Rules:
    1. Be extremely helpful, professional, and friendly.
    2. Suggest specific schemes from the list if they match the user's query.
    3. If they ask about eligibility, tell them to use the 'Eligibility Checker' button on their dashboard for precise results.
    4. Keep responses concise and format them nicely with bullet points if needed.
    """

    try:
        response = ai_model.generate_content([system_prompt, user_message])
        return jsonify({'reply': response.text})
    except Exception as e:
        print(f"AI Error: {str(e)}")
        return jsonify({'reply': "I'm having a minor technical glitch. Please ensure the Gemini API key is properly configured in app.py!"})

if __name__ == '__main__':
    app.run(debug=True)
