# OnlineShopping
Online Shopping Cart

# Installing Prerequisites
sudo apt update
sudo apt install git python3-pip build-essential python3-venv python3-wheel python3-setuptools

# Clone the code by 
git clone https://github.com/shimaa10/OnlineShopping.git

# Open project path
cd /OnlineShopping

# Create a new Python virtual environment 
python3 -m venv shop-venv

# Activate the virtual environment
source shop-venv/bin/activate

# Install all required Python modules with pip3
pip3 install -r requirements.txt

# Then you can run the website by 
python3 manage.py runserver

# Superuser credentials (admin user)
username : admin
password : admin 

# Normal user credentials
username : Ahmad 
password : ahmad123

# Also, you can create a new user by registeration form

# Use Cases:
1. Add to cart with logged in user (cart will be saved in browser cookies and database).
2. Add to cart without logged in user (Cart will be saved in browser cookies), In this case the user should log in before checkout.

# Note:
Because the data is saved in browser cookies, the update on the cart (add, remove, update) is running in javascript code.
