# OnlineShopping
Online Shopping Cart

# after clone the code by 
git clone https://github.com/shimaa10/OnlineShopping.git
# install Django 
pip3 install django

# then you can run the website by 
python3 manage.py runserver

# I created superuser (admin user)
username : admin
password : admin 

# Use Cases:
1. Add to cart with logged in user (cart will be saved in browser cookies and database).
2. Add to cart without logged in user (Cart will be saved in browser cookies), In this case the user should log in before checkout.

Note:
Because the data is saved in browser cookies, the update on the cart (add, remove, update) is running in javascript code.
