# TechShop E-Commerce Platform

TechShop is a comprehensive, feature-rich E-Commerce platform built with Django. It features a modern, responsive user interface and a powerful "Deep Indigo/Slate" glassmorphic administrative dashboard.

## Features
- **Product Catalog:** Categories, brands, variants, and product comparisons.
- **Shopping Experience:** Shopping cart, wishlist, and secure checkout.
- **Order Management:** Order history, tracking, invoices, and automated email receipts.
- **Admin Dashboard:** Modern, custom-styled admin interface for managing inventory, orders, staff, and customers.
- **Design System:** Consistent, premium UI/UX design across both frontend and administrative backend interfaces.

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MeTariqul/MeTariqul-tecshop.git
   cd MeTariqul-tecshop
   ```

2. **Set up a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations:**
   ```bash
   cd techshop
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the development server:**
   ```bash
   # Using the provided batch scripts (Windows)
   ..\run_dev_server.bat
   # Or directly
   python manage.py runserver
   ```

## Design Overview
This project includes a comprehensive UI/UX overhaul. The frontend uses a vibrant, engaging design, while the Django admin dashboard features a custom "Deep Indigo/Slate" glassmorphic theme, complete with Bootstrap 5 integration for responsive, modern layouts.
