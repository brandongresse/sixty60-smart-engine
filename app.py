from flask import Flask, jsonify, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sixty60_engine.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 1. Product Model (Inventory with Categories & Prices)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "stock_quantity": self.stock_quantity
        }

# 2. Active Delivery Model (Cold Chain & ETA Tracking)
class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_reference = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    has_perishables = db.Column(db.Boolean, default=True) # Dairy, Meat, Frozen
    dispatch_time = db.Column(db.DateTime, default=datetime.utcnow)
    estimated_minutes = db.Column(db.Integer, nullable=False) # Target < 60 mins
    status = db.Column(db.String(50), default="On Route")

    def to_dict(self):
        # Calculate if cold chain risk is breached (> 45 mins for perishables)
        risk_flag = self.has_perishables and self.estimated_minutes > 45
        return {
            "id": self.id,
            "order_reference": self.order_reference,
            "customer_name": self.customer_name,
            "has_perishables": self.has_perishables,
            "estimated_minutes": self.estimated_minutes,
            "cold_chain_risk": risk_flag,
            "status": "HIGH PRIORITY - COLD RISK" if risk_flag else self.status
        }

# Seed Initial Sixty60 Data
def seed_sixty60_data():
    if Product.query.count() == 0:
        products = [
            Product(name="Sixty60 Fresh Whole Milk 2L", category="Dairy", price=35.99, stock_quantity=0), # Out of stock trigger!
            Product(name="Fairview Full Cream Milk 2L", category="Dairy", price=38.99, stock_quantity=15), # Valid Sub 1
            Product(name="Clover Fresh Milk 2L", category="Dairy", price=36.50, stock_quantity=8),       # Valid Sub 2
            FrozenItem := Product(name="Mandela Park Chicken Breasts 1kg", category="Frozen", price=99.99, stock_quantity=5)
        ]
        db.session.bulk_save_objects(products)
        
        deliveries = [
            Delivery(order_reference="S60-9921", customer_name="Thabo M.", has_perishables=True, estimated_minutes=52), # Risk!
            Delivery(order_reference="S60-9922", customer_name="Sarah V.", has_perishables=False, estimated_minutes=25)
        ]
        db.session.bulk_save_objects(deliveries)
        db.session.commit()

with app.app_context():
    db.create_all()
    seed_sixty60_data()

# HTML Dashboard Template (Sixty60 Teal Branding)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sixty60 Smart Engine Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar { background-color: #00b0ff; } /* Sixty60 Blue/Teal vibe */
        .card { border: none; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .table thead { background-color: #1a237e; color: white; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark mb-4">
        <div class="container">
            <span class="navbar-brand mb-0 h1 fw-bold">⚡ Sixty60 Smart Substitution & Cold-Chain Engine</span>
            <span class="text-white small">ShopriteX Innovation Prototype</span>
        </div>
    </nav>

    <div class="container">
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card p-3">
                    <h5 class="fw-bold text-primary">🛒 Smart Out-of-Stock Substitution API</h5>
                    <p class="text-muted small">When an item has 0 stock, query valid category substitutes instantly.</p>
                    <a href="/api/substitute/1" class="btn btn-outline-primary btn-sm" target="_blank">Test Substitution for Item #1 (Milk)</a>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card p-3">
                    <h5 class="fw-bold text-danger">❄️ Cold-Chain Risk Monitor API</h5>
                    <p class="text-muted small">Tracks delivery ETAs for perishable goods to prevent spoilage risks.</p>
                    <a href="/api/deliveries" class="btn btn-outline-danger btn-sm" target="_blank">View Live Delivery Risk Status</a>
                </div>
            </div>
        </div>

        <div class="card p-4">
            <h4 class="mb-3 fw-bold">Live Inventory Catalog & Stock Status</h4>
            <table class="table table-hover align-middle">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Product Name</th>
                        <th>Category</th>
                        <th>Price</th>
                        <th>Stock Level</th>
                        <th>Action / Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in products %}
                    <tr>
                        <td>#{{ item.id }}</td>
                        <td>{{ item.name }}</td>
                        <td><span class="badge bg-secondary">{{ item.category }}</span></td>
                        <td>R {{ "%.2f"|format(item.price) }}</td>
                        <td><strong>{{ item.stock_quantity }} units</strong></td>
                        <td>
                            {% if item.stock_quantity == 0 %}
                                <a href="/api/substitute/{{ item.id }}" class="btn btn-danger btn-sm" target="_blank">Find Substitutes</a>
                            {% else %}
                                <span class="badge bg-success">In Stock</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

# Routes
@app.route('/')
def home():
    products = Product.query.all()
    return render_template_string(HTML_TEMPLATE, products=products)

# 1. Smart Substitution Endpoint (The Core Logic)
@app.route('/api/substitute/<int:product_id>', methods=['GET'])
def get_substitutes(product_id):
    original_item = Product.query.get_or_404(product_id)
    
    # Find items in the same category, with stock > 0, and close in price (+/- R15)
    alternatives = Product.query.filter(
        Product.category == original_item.category,
        Product.id != original_item.id,
        Product.stock_quantity > 0,
        Product.price.between(original_item.price - 15.0, original_item.price + 15.0)
    ).all()

    return jsonify({
        "out_of_stock_item": original_item.to_dict(),
        "suggested_substitutes": [alt.to_dict() for alt in alternatives],
        "message": "Smart substitution engine matched top viable alternatives successfully."
    })

# 2. Cold-Chain Delivery Risk Endpoint
@app.route('/api/deliveries', methods=['GET'])
def get_deliveries():
    deliveries = Delivery.query.all()
    return jsonify([d.to_dict() for d in deliveries])

if __name__ == '__main__':
    app.run(debug=True, port=5001) # Running on port 5001 so it doesn't clash with my other app!