from app.models import Order, Product
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import logging
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
import os
import json

logger = logging.getLogger(__name__)

def get_seasonal_data(product_name):
    """Get seasonal trend data for the product using SerpAPI"""
    try:
        params = {
            "engine": "google_trends",
            "q": f"{product_name} india",
            "geo": "IN",
            "date": "today 12-m",
            "api_key": os.getenv("SERPAPI_API_KEY")
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "interest_over_time" in results:
            return results["interest_over_time"]
        
        return None
    except Exception as e:
        logger.error(f"Error fetching seasonal data: {str(e)}")
        return None

def get_market_data(product_name):
    """Get current market data from agricultural websites"""
    try:
        # Example URLs - add more as needed
        urls = [
            "https://agmarknet.gov.in",
            "https://farmer.gov.in/market_prices.aspx"
        ]
        
        market_data = []
        
        for url in urls:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Extract relevant price and demand data
                # This is a simplified example - implement actual parsing logic
                price_elements = soup.find_all(class_="price")
                for element in price_elements:
                    if product_name.lower() in element.text.lower():
                        market_data.append(float(element.text.strip()))
        
        return market_data if market_data else None
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        return None

def calculate_seasonal_factor(seasonal_data, current_date):
    """Calculate seasonal factor based on historical trends"""
    if not seasonal_data:
        return 1.0
    
    try:
        # Convert Google Trends data to seasonal factors
        df = pd.DataFrame(seasonal_data)
        current_month = current_date.month
        
        # Calculate average interest for the current month
        monthly_avg = df[df.index.month == current_month]['interest'].mean()
        overall_avg = df['interest'].mean()
        
        # Calculate seasonal factor (minimum 0.5, maximum 2.0)
        seasonal_factor = max(0.5, min(2.0, monthly_avg / overall_avg))
        return seasonal_factor
    except Exception as e:
        logger.error(f"Error calculating seasonal factor: {str(e)}")
        return 1.0

def forecast_demand(product):
    try:
        # Fetch historical sales data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        orders = Order.objects(
            products__product=product.id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Initialize sales data
        sales_data = []
        
        # If we have historical orders, use them
        if orders:
            for order in orders:
                for item in order.products:
                    if item.product.id == product.id:
                        sales_data.append({
                            'date': order.created_at.date(),
                            'quantity': item.quantity
                        })
        
        # Get external data
        seasonal_data = get_seasonal_data(product.name)
        market_data = get_market_data(product.name)
        
        # Create or supplement sales data with external information
        df = pd.DataFrame(sales_data)
        
        if df.empty:
            # If no historical data, create synthetic data based on market information
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            base_demand = 5.0  # Default base demand
            
            if market_data:
                base_demand = np.mean(market_data)
            
            synthetic_data = []
            for date in dates:
                seasonal_factor = calculate_seasonal_factor(seasonal_data, date)
                quantity = base_demand * seasonal_factor * (0.8 + 0.4 * np.random.random())
                synthetic_data.append({
                    'date': date.date(),
                    'quantity': round(quantity, 2)
                })
            
            df = pd.DataFrame(synthetic_data)
        
        # Prepare data for forecasting
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        df = df.sort_index()
        df = df.resample('D').sum().fillna(method='ffill')
        
        # Add seasonal components if available
        if seasonal_data:
            seasonal_factors = [calculate_seasonal_factor(seasonal_data, date) 
                              for date in df.index]
            df['seasonal_factor'] = seasonal_factors
            df['quantity'] = df['quantity'] * df['seasonal_factor']
        
        # Fit ARIMA model with dynamic order selection
        best_aic = float('inf')
        best_order = (1, 1, 1)
        
        # Try different ARIMA parameters
        for p in range(0, 3):
            for d in range(0, 2):
                for q in range(0, 3):
                    try:
                        model = ARIMA(df['quantity'], order=(p, d, q))
                        results = model.fit()
                        if results.aic < best_aic:
                            best_aic = results.aic
                            best_order = (p, d, q)
                    except:
                        continue
        
        # Fit final model with best parameters
        final_model = ARIMA(df['quantity'], order=best_order)
        results = final_model.fit()
        
        # Generate forecast for next 30 days
        forecast = results.forecast(steps=30)
        
        # Apply seasonal adjustments to forecast
        forecast_dates = [end_date + timedelta(days=i) for i in range(30)]
        if seasonal_data:
            seasonal_factors = [calculate_seasonal_factor(seasonal_data, date) 
                              for date in forecast_dates]
            forecast = forecast * np.array(seasonal_factors)
        
        # Create forecast dictionary with adjusted values
        forecast_dict = {
            date: max(0, round(value, 2))
            for date, value in zip(forecast_dates, forecast)
        }
        
        logger.info(f"Generated forecast for product {product.id} using {'historical' if orders else 'synthetic'} data")
        return forecast_dict
    
    except Exception as e:
        logger.error(f"Error in forecast_demand: {str(e)}")
        raise

