import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from app.models import User, Product, Order

def get_user_item_matrix():
    users = User.objects(role='customer')
    products = Product.objects.all()
    
    user_ids = {str(user.id): i for i, user in enumerate(users)}
    product_ids = {str(product.id): i for i, product in enumerate(products)}
    
    data = []
    row_ind = []
    col_ind = []
    
    for order in Order.objects:
        user_index = user_ids.get(str(order.customer.id))
        for product, quantity in order.products:
            product_index = product_ids.get(str(product.id))
            if user_index is not None and product_index is not None:
                data.append(quantity)
                row_ind.append(user_index)
                col_ind.append(product_index)
    
    matrix = csr_matrix((data, (row_ind, col_ind)), shape=(len(users), len(products)))
    return matrix, list(users), list(products)

def get_recommendations(user_id, n_recommendations=5):
    matrix, users, products = get_user_item_matrix()
    
    user_index = next((i for i, u in enumerate(users) if str(u.id) == str(user_id)), None)
    if user_index is None:
        return []
    
    model = NearestNeighbors(metric='cosine', algorithm='brute')
    model.fit(matrix)
    
    distances, indices = model.kneighbors(matrix[user_index].reshape(1, -1), n_neighbors=n_recommendations+1)
    
    recommended_products = []
    for i in indices.flatten()[1:]:
        product = products[i]
        recommended_products.append(product)
    
    return recommended_products
