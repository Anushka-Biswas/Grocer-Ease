import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.models import Order, Product

def get_sales_data(seller_id=None):
    all_orders = Order.objects.all()
    
    data = []
    for order in all_orders:
        for item in order.products:
            if seller_id is None or str(item.product.seller.id) == str(seller_id):
                data.append({
                    'date': order.created_at.date(),
                    'product': item.product.name,
                    'quantity': item.quantity,
                    'revenue': item.quantity * item.product.price,
                    'seller': item.product.seller.name
                })
    return pd.DataFrame(data)

def generate_sales_chart(sales_data):
    if sales_data.empty:
        return "<div>No sales data available</div>"
    
    # Group by date and sum revenue
    daily_sales = sales_data.groupby('date')['revenue'].sum().reset_index()
    
    # Create the line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_sales['date'],
        y=daily_sales['revenue'],
        mode='lines+markers',
        name='Daily Sales',
        line=dict(color='#22c55e', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Daily Sales Revenue',
        xaxis_title='Date',
        yaxis_title='Revenue (₹)',
        template='plotly_white',
        height=400,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs=True)

def generate_top_products_chart(sales_data):
    if sales_data.empty:
        return "<div>No product data available</div>"
    
    # Group by product and sum quantity
    top_products = sales_data.groupby('product').agg({
        'quantity': 'sum',
        'revenue': 'sum'
    }).sort_values('revenue', ascending=True).tail(5)
    
    # Create the bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top_products.index,
        x=top_products['revenue'],
        orientation='h',
        marker_color='#22c55e'
    ))
    
    fig.update_layout(
        title='Top 5 Products by Revenue',
        xaxis_title='Revenue (₹)',
        yaxis_title='Product',
        template='plotly_white',
        height=400,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs=True)

