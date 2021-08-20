from app import app
from app.auth import basic_auth, token_auth
from app.models import User, Product
from flask import jsonify, request


@app.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    return jsonify({ 'token': token })


@app.route('/users')
def users():
    users = [u.to_dict() for u in User.query.all()]
    return jsonify(users=users)


@app.route('/users/<int:id>')
def user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())


@app.route('/create-user', methods=['POST'])
def create_user():
    data = request.get_json()
    for key in ['first_name', 'last_name', 'username', 'email', 'password']:
        if key not in data:
            return jsonify({'error': f"The '{key}' key is required to create a new user"}), 400
    check_user = User.query.filter((User.username==data['username']) | (User.email==data['email'])).all()
    if check_user:
        return jsonify({'error': 'A user with that username and/or email already exists'}), 400
    user = User()
    user.from_dict(data)
    
    return jsonify(user.to_dict()), 201


@app.route('/update-user', methods=['POST'])
@token_auth.login_required
def update_user():
    data = request.get_json()
    user = token_auth.current_user()
    user.from_dict(data)
    return jsonify(user.to_dict())


@app.route('/products')
def products():
    products = [u.to_dict() for u in Product.query.all()]
    return jsonify(products=products)


@app.route('/products/<int:id>')
def product(id):
    product = Product.query.get_or_404(id)
    return jsonify(product.to_dict())


@app.route('/add-to-cart/<int:prod_id>', methods=['POST'])
@token_auth.login_required
def add_to_cart(prod_id):
    prod = Product.query.get_or_404(prod_id)
    user = token_auth.current_user()
    user.add_to_cart(prod)
    
    return jsonify(user.to_dict())


@app.route('/remove-from-cart/<int:prod_id>', methods=['DELETE'])
@token_auth.login_required
def remove_from_cart(prod_id):
    prod = Product.query.get_or_404(prod_id)
    user = token_auth.current_user()
    if prod not in user.products:
        return jsonify({"error": f"This product is not in this user's cart: {prod.name}"}), 400
    user.remove_from_cart(prod)
    return jsonify(user.to_dict())
