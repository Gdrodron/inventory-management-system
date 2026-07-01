from flask import Flask, render_template, session, request, redirect, flash
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import psycopg2
import os


# =========================
# ENV
# =========================

load_dotenv()


# =========================
# FLASK
# =========================

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "dev-secret")


# =========================
# UPLOAD FOLDER
# =========================

UPLOAD_FOLDER = os.path.join("static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# DATABASE
# =========================

conn = psycopg2.connect(

    host=os.getenv("DB_HOST"),

    database=os.getenv("DB_NAME"),

    user=os.getenv("DB_USER"),

    password=os.getenv("DB_PASSWORD"),

    port=os.getenv("DB_PORT")

)

conn.autocommit = True


# =========================
# LOGIN REQUIRED
# =========================

def login_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/login")

        return f(*args, **kwargs)

    return decorated

# =========================
# ROLE REQUIRED
# =========================

def role_required(*roles):

    def decorator(f):

        @wraps(f)
        def decorated(*args, **kwargs):

            if "role" not in session:
                flash("Please login first.", "warning")
                return redirect("/login")

            if session.get("role", "").lower() not in [r.lower() for r in roles]:
                return render_template("errors/403.html"), 403

            return f(*args, **kwargs)

        return decorated

    return decorator


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    # If user is already logged in
    if "user_id" in session:
        return redirect("/")

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        cur = conn.cursor()

        try:

            cur.execute("""
                SELECT
                    id,
                    username,
                    password,
                    role
                FROM Inventory.users
                WHERE username = %s
            """, (username,))

            user = cur.fetchone()

        finally:
            cur.close()

        if user and check_password_hash(user[2], password):

            session.clear()

            session["user_id"] = user[0]
            session["user"] = user[1]
            session["role"] = (user[3] or "").strip().lower()

            flash("Welcome back!", "success")

            return redirect("/")

        flash("Invalid username or password.", "danger")

    return render_template("login.html")

# =========================
# LOGOUT
# =========================

@app.route("/logout")
@login_required
def logout():

    session.clear()

    flash(
        "Logged out successfully.",
        "success"
    )

    return redirect("/login")


# =========================
# DASHBOARD
# =========================

@app.route("/")
@login_required
def index():

    cur = conn.cursor()

    try:

        # =========================
        # PRODUCTS
        # =========================
        cur.execute("""
            SELECT
                id,
                product_name,
                price_numeric,
                image,
                quantity,
                category
            FROM Inventory.products
            ORDER BY id
        """)

        products = cur.fetchall()


        # =========================
        # DASHBOARD CARDS
        # =========================
        total_products = len(products)

        total_stock = sum(
            product[4] or 0
            for product in products
        )

        inventory_value = sum(
            float(product[2] or 0) * (product[4] or 0)
            for product in products
        )

        low_stock = sum(
            1
            for product in products
            if (product[4] or 0) <= 5
        )


        # =========================
        # PIE CHART
        # Products per Category
        # =========================
        cur.execute("""
            SELECT
                category,
                COUNT(*)
            FROM Inventory.products
            GROUP BY category
            ORDER BY category
        """)

        category_data = cur.fetchall()


        # =========================
        # BAR CHART
        # Stock per Product
        # =========================
        cur.execute("""
            SELECT
                product_name,
                quantity
            FROM Inventory.products
            ORDER BY product_name
        """)

        stock_data = cur.fetchall()



        # =========================
        # CHART DATA
        # =========================
        category_labels = [
            row[0] or "No Category"
            for row in category_data
        ]

        category_values = [
            row[1]
            for row in category_data
        ]


        stock_labels = [
            row[0]
            for row in stock_data
        ]

        stock_values = [
            row[1] or 0
            for row in stock_data
        ]


        # =========================
        # RENDER
        # =========================
        return render_template(
            "index.html",

            products=products,

            total_products=total_products,
            total_stock=total_stock,
            inventory_value=inventory_value,
            low_stock=low_stock,

            category_labels=category_labels,
            category_values=category_values,

            stock_labels=stock_labels,
            stock_values=stock_values
        )


    finally:
        cur.close()
        
# =========================
# ADD PRODUCT
# =========================

@app.route("/add", methods=["GET","POST"])
def add_product():

    if request.method == "POST":

        name = request.form["product_name"]
        category = request.form["category"]
        price = request.form["price"]
        quantity = request.form["quantity"]

        # Image Upload
        image = request.files.get("image")

        if image and image.filename != "":

            filename = secure_filename(image.filename)
            image.save(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )

            image_filename = filename

        else:

            image_filename = None

        cur = conn.cursor()

        cur.execute("""
            INSERT INTO Inventory.products
            (
                product_name,
                price_numeric,
                image,
                quantity,
                category
            )
            VALUES (%s,%s,%s,%s,%s)
            RETURNING id
        """,
        (
            name,
            price,
            image_filename,
            quantity,
            category
        ))

        product_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO Inventory.inventory_transactions
            (
                product_id,
                transaction_type,
                quantity,
                user_id
            )
            VALUES
            (
                %s,
                'ADD PRODUCT',
                %s,
                %s
            )
        """,
        (
            product_id,
            quantity,
            session["user_id"]
        ))

        cur.close()

        flash(
            "Product added successfully!",
            "success"
        )

        return redirect("/")

    return render_template("add.html")

# =========================
# EDIT PRODUCT
# =========================

@app.route("/edit/<int:id>", methods=["GET","POST"])
@login_required
@role_required("Admin")
def edit_product(id):

    cur = conn.cursor()

    try:

        # =========================
        # UPDATE PRODUCT
        # =========================
        if request.method == "POST":

            name = request.form.get("product_name", "").strip()
            category = request.form.get("category", "").strip()
            price = request.form.get("price", 0)
            quantity = request.form.get("quantity", 0)

            cur.execute("""
                UPDATE Inventory.products
                SET
                    product_name = %s,
                    price_numeric = %s,
                    quantity = %s,
                    category = %s
                WHERE id = %s
            """,
            (
                name,
                price,
                quantity,
                category,
                id
            ))

            flash(
                "Product updated successfully!",
                "success"
            )

            return redirect("/")

        # =========================
        # LOAD PRODUCT
        # =========================
        cur.execute("""
            SELECT
                id,
                product_name,
                price_numeric,
                quantity,
                category
            FROM Inventory.products
            WHERE id = %s
        """, (id,))

        product = cur.fetchone()

        if not product:

            flash(
                "Product not found.",
                "danger"
            )

            return redirect("/")

        return render_template(
            "edit.html",
            product=product
        )

    finally:

        cur.close()

# =========================
# DELETE PRODUCT
# =========================

@app.route("/delete/<int:id>", methods=["POST"])
@login_required
@role_required("Admin")
def delete_product(id):

    cur = conn.cursor()

    try:

        # Check if product exists
        cur.execute("""
            SELECT id
            FROM Inventory.products
            WHERE id = %s
        """, (id,))

        product = cur.fetchone()

        if not product:

            flash(
                "Product not found.",
                "danger"
            )

            return redirect("/")

        # Delete product
        cur.execute("""
            DELETE FROM Inventory.products
            WHERE id = %s
        """, (id,))

        flash(
            "Product deleted successfully!",
            "success"
        )

    finally:

        cur.close()

    return redirect("/")


# =========================
# STOCK IN
# =========================

@app.route("/stock-in/<int:id>", methods=["POST"])
@login_required
@role_required("Admin")
def stock_in(id):

    cur = conn.cursor()

    try:

        # Check if product exists
        cur.execute("""
            SELECT id
            FROM Inventory.products
            WHERE id = %s
        """, (id,))

        product = cur.fetchone()

        if not product:

            flash(
                "Product not found.",
                "danger"
            )

            return redirect("/")

        # Increase stock
        cur.execute("""
            UPDATE Inventory.products
            SET quantity = quantity + 1
            WHERE id = %s
        """, (id,))

        # Save transaction
        cur.execute("""
            INSERT INTO Inventory.inventory_transactions
            (
                product_id,
                transaction_type,
                quantity,
                user_id
            )
            VALUES
            (
                %s,
                'STOCK IN',
                1,
                %s
            )
        """,
        (
            id,
            session["user_id"]
        ))

        flash(
            "Stock added successfully!",
            "success"
        )

    finally:

        cur.close()

    return redirect("/")

# =========================
# STOCK OUT
# =========================

@app.route("/stock-out/<int:id>", methods=["POST"])
@login_required
@role_required("Admin")
def stock_out(id):

    cur = conn.cursor()

    try:

        # Check if product exists
        cur.execute("""
            SELECT
                id,
                quantity
            FROM Inventory.products
            WHERE id = %s
        """, (id,))

        product = cur.fetchone()

        if not product:

            flash(
                "Product not found.",
                "danger"
            )

            return redirect("/")

        # Check if stock is available
        if product[1] <= 0:

            flash(
                "No stock available to deduct.",
                "warning"
            )

            return redirect("/")

        # Decrease stock
        cur.execute("""
            UPDATE Inventory.products
            SET quantity = quantity - 1
            WHERE id = %s
        """, (id,))

        # Save transaction
        cur.execute("""
            INSERT INTO Inventory.inventory_transactions
            (
                product_id,
                transaction_type,
                quantity,
                user_id
            )
            VALUES
            (
                %s,
                'STOCK OUT',
                1,
                %s
            )
        """,
        (
            id,
            session["user_id"]
        ))

        flash(
            "Stock deducted successfully!",
            "success"
        )

    finally:

        cur.close()

    return redirect("/")

# =========================
# TRANSACTIONS
# =========================

@app.route("/transactions")
@login_required
def transactions():

    cur = conn.cursor()

    cur.execute("""
        SELECT

            t.id,
            p.product_name,
            t.transaction_type,
            t.quantity,
            t.transaction_date,
            u.username

        FROM Inventory.inventory_transactions t

        JOIN Inventory.products p
            ON p.id = t.product_id

        JOIN Inventory.users u
            ON u.id = t.user_id

        ORDER BY t.transaction_date DESC

    """)

    transactions = cur.fetchall()

    cur.close()

    return render_template(
        "transactions.html",
        transactions=transactions
    )


# =========================
# REPORTS
# =========================

@app.route("/reports")
@login_required
def reports():

    cur = conn.cursor()

    try:

        # Products
        cur.execute("""
            SELECT
                id,
                product_name,
                price_numeric,
                image,
                quantity,
                category
            FROM Inventory.products
            ORDER BY id
        """)

        products = cur.fetchall()

        # Summary
        total_products = len(products)

        total_stock = sum(p[4] or 0 for p in products)

        inventory_value = sum(
            float(p[2] or 0) * (p[4] or 0)
            for p in products
        )

        low_stock = sum(
            1
            for p in products
            if (p[4] or 0) <= 5
        )

        # Pie Chart
        cur.execute("""
            SELECT
                category,
                COUNT(*)
            FROM Inventory.products
            GROUP BY category
            ORDER BY category
        """)

        category_data = cur.fetchall()

        # Bar Chart
        cur.execute("""
            SELECT
                product_name,
                quantity
            FROM Inventory.products
            ORDER BY product_name
        """)

        stock_data = cur.fetchall()

        category_labels = [r[0] or "No Category" for r in category_data]
        category_values = [r[1] for r in category_data]

        stock_labels = [r[0] for r in stock_data]
        stock_values = [r[1] or 0 for r in stock_data]

        return render_template(

            "reports.html",

            products=products,

            total_products=total_products,
            total_stock=total_stock,
            inventory_value=inventory_value,
            low_stock=low_stock,

            category_labels=category_labels,
            category_values=category_values,

            stock_labels=stock_labels,
            stock_values=stock_values

        )

    finally:
        cur.close()


# =========================
# ERROR PAGES
# =========================

@app.errorhandler(404)
def not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(403)
def forbidden(error):
    return render_template("errors/403.html"), 403


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500        

# =========================
# RUN
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )