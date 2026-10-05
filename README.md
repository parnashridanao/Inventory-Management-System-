# Inventory Management System

A Flask-based Inventory Management System that allows users to manage products, track stock, search inventory, update product details, and identify low-stock products.

## Features

* Add new products
* View all products
* Search products by name, product ID, or category
* Update product information
* Delete products
* Increase or decrease stock
* Low-stock detection
* Product ID uniqueness validation
* Quantity and price validation
* SQLite database integration
* REST API endpoints
* Automated API testing

## Tech Stack

* Python
* Flask
* SQLite
* HTML/CSS/JavaScript
* REST API

## Project Structure

```text
inventory-management-system/
│
├── app.py
├── test_app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   └── index.html
│
└── screenshots/
```

## Database

The application uses SQLite to store product information.

Each product contains:

* Product ID
* Name
* Category
* Quantity
* Price

The application also identifies products as low-stock when their quantity reaches the configured low-stock limit.

## API Endpoints

### Display Application

```text
GET /
```

### Get Products

```text
GET /api/products
```

Search can be performed using:

```text
GET /api/products?q=product_name
```

### Add Product

```text
POST /api/products
```

Example JSON:

```json
{
    "product_id": "P1",
    "name": "Pen",
    "category": "Stationery",
    "quantity": 50,
    "price": 10
}
```

### Update Product

```text
PUT /api/products/<product_id>
```

### Adjust Stock

```text
POST /api/products/<product_id>/stock
```

Example:

```json
{
    "delta": -5
}
```

### Delete Product

```text
DELETE /api/products/<product_id>
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/inventory-management-system.git
```

### 2. Open the project

```bash
cd inventory-management-system
```

### 3. Create a virtual environment

Windows:

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

The application will start using Flask's development server.

Open the local URL shown in the terminal in your browser.

## Testing

The project includes `test_app.py` for testing the API functionality.

Run:

```bash
python test_app.py
```

The test file checks:

* Application response
* Product creation
* Duplicate product IDs
* Invalid quantities
* Invalid prices
* Empty product IDs
* Invalid quantity values
* Product search
* Product updates
* Stock adjustment
* Product deletion
* Product-not-found errors

## Future Improvements

* User authentication
* Role-based access control
* Inventory dashboard
* Sales and purchase tracking
* Product image support
* Export inventory reports
* Advanced analytics
* Cloud database integration
* Deployment on a cloud platform

## Author

**Parnashri Danao**

BTech Electronics and Computer Science

## License

This project is created for educational and portfolio purposes.
