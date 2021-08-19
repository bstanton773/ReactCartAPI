from app import app, db
from app.models import User, Product

if __name__ == '__main__':
    app.run()


@app.shell_context_processor
def make_context():
    return {'User': User, 'Product': Product, 'db': db}