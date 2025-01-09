# GrocerEase

GrocerEase is a comprehensive e-commerce platform designed to revolutionize the grocery shopping experience for customers in India while providing powerful tools for sellers and administrators. This platform bridges the gap between local grocery sellers and tech-savvy consumers, offering a seamless online shopping experience with advanced features for inventory management, price optimization, and demand forecasting.

## Features

### For Customers
- User-friendly product browsing with category filters and search functionality
- Detailed product pages with descriptions, prices, and stock information
- Smart shopping cart management with real-time updates
- Secure checkout process with multiple payment options
- Order history and tracking
- Personalized product recommendations

### For Sellers
- Comprehensive dashboard with sales analytics and key performance indicators
- Inventory management system with stock updates and low stock alerts
- Price optimization tool using market data and AI algorithms
- Demand forecasting based on historical sales and seasonal trends
- Order management and status updates
- Product listing and management with image upload capability

### For Administrators
- Platform-wide analytics and reporting
- User management (customers and sellers)
- Product catalog oversight
- Order tracking and management across all sellers
- System configuration and maintenance tools

## Technology Stack

- Backend: Flask (Python 3.9+)
- Database: MongoDB with MongoEngine ODM
- Frontend: 
  - HTML5
  - CSS3 with Tailwind CSS for responsive design
  - JavaScript with Alpine.js for reactive components
- Authentication: Flask-Login for session management
- Data Visualization: Plotly for interactive charts
- Machine Learning: 
  - ARIMA models for time series forecasting
  - Custom algorithms for price optimization
- External APIs: 
  - SerpAPI for market data retrieval
  - Google Trends API for seasonal trend analysis
- Version Control: Git
- Deployment: Vercel (or your preferred hosting solution)

## Installation and Setup

1. Clone the repository:
   \`\`\`
   git clone https://github.com/yourusername/grocerease.git
   cd grocerease
   \`\`\`

2. Set up a virtual environment:
   \`\`\`
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   \`\`\`

3. Install dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

4. Set up MongoDB:
   - Install MongoDB on your system if you haven't already.
   - Start the MongoDB service.

5. Set up environment variables:
   - Create a `.env` file in the project root directory.
   - Add the following variables:
     \`\`\`
     SECRET_KEY=your_secret_key_here
     MONGODB_URI=mongodb://localhost:27017/grocer_ease
     SERPAPI_API_KEY=your_serpapi_key_here
     \`\`\`

6. Initialize the database with sample data:
   \`\`\`
   python load_sample_data.py
   \`\`\`

7. Run the application:
   \`\`\`
   python run.py
   \`\`\`

8. Open your browser and navigate to `http://localhost:5000`.

## Project Structure

- `app/`: Main application package
  - `routes/`: Contains route handlers for different user roles
  - `static/`: Static files (CSS, JavaScript, uploaded images)
  - `templates/`: HTML templates organized by user role
  - `models.py`: Database models using MongoEngine
  - `analytics.py`: Functions for generating sales analytics
  - `forecasting.py`: Demand forecasting algorithms
  - `price_optimizer.py`: Price optimization logic
- `tests/`: Unit and integration tests
- `config.py`: Application configuration
- `run.py`: Script to run the Flask application
- `load_sample_data.py`: Script to populate the database with initial data

## Key Components

1. **User Authentication**: Implemented using Flask-Login, supporting multiple user roles (Customer, Seller, Admin).

2. **Product Management**: CRUD operations for products, including image uploads and storage.

3. **Shopping Cart**: Real-time cart management with MongoDB for persistence.

4. **Order Processing**: Secure checkout process and order status management.

5. **Analytics Dashboard**: 
   - For Sellers: Individual sales performance, top products, and revenue trends.
   - For Admins: Platform-wide analytics including user growth and overall sales performance.

6. **Price Optimization**: 
   - Utilizes SerpAPI to fetch current market prices for similar products.
   - Implements a genetic algorithm to suggest optimal pricing based on market data and profit margins.

7. **Demand Forecasting**:
   - Uses ARIMA models for time series forecasting.
   - Incorporates seasonal trends from Google Trends API for more accurate predictions.

8. **Responsive Design**: Utilizes Tailwind CSS for a mobile-first, responsive layout.

9. **Error Handling**: Custom 404 and 500 error pages and comprehensive error logging.

## API Endpoints

The application provides RESTful API endpoints for various operations. Key endpoints include:

- `/api/products`: GET, POST, PUT, DELETE operations for products
- `/api/cart`: Shopping cart management
- `/api/orders`: Order placement and retrieval
- `/api/analytics`: Fetch analytics data for sellers and admins
- `/api/forecast`: Generate demand forecasts for products
- `/api/optimize-price`: Calculate optimal price for a product

## Security Measures

- Password hashing using Werkzeug's security features
- CSRF protection for all forms
- Secure session management
- Input validation and sanitization to prevent XSS and injection attacks
- Role-based access control for routes and functionalities

## Testing

To run the test suite:

\`\`\`
python -m unittest discover tests
\`\`\`

## Deployment

For deployment instructions, please refer to the [deployment guide](DEPLOYMENT.md).

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - The web framework used
- [MongoDB](https://www.mongodb.com/) - The database used
- [Tailwind CSS](https://tailwindcss.com/) - For the responsive design
- [Alpine.js](https://alpinejs.dev/) - For reactive JavaScript components
- [Plotly](https://plotly.com/) - For interactive charts and graphs
- [SerpAPI](https://serpapi.com/) - For market data retrieval

