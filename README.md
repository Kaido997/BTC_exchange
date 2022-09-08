# BTC_exchange
 
This is a simple Bitcoin exchange backend for you can login and register and the system give you a random value of BTC and USD that you can try some trades.

## Thecnologies:
 - DJango
 - MongoDB
 - DJongo

For this project i used MongoDB a NoSQL database for storing all the data like orders and user profiles, DJango for building the all the system and thanks to DJongo
i can communicate changes to Mongo super easly

## Installation
 - Make your virtual enviroment
 
 - Activate
 
 - Install pakages with requirements.txt
 
   ```js
   pip install -r requirements.txt
   ```
 - Launch your mongoDB server on port 27017
 
 - Migrate
 
    ```js
   python manage.py migrate
   ```
 - Create super user
 
   ```js
   python manage.py createsuperuser
   ```
 
## URLS
These are the site urls where you can navigate

- initial page is your order list
- /login/ -> login endpoint
- /register/ -> register endpoint
- /wallet/ -> where you can see your balance and your trend postive number indicates earn 
- /logout/ -> logout endpoint
- /orders/ -> all platform pending orders
- /publish/ -> endopoint where you can publish a new order

