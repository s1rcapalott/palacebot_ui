import logging
import re
# import geoname_api
import os
import json


class Validator:
    US_STATES = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 
        'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 
        'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 
        'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 
        'WI', 'WY'
    
    }
    #think of it as a global constant so there isnt a need to place it inside of the class
    SHOE_PALACE_URL = "https://www.shoepalace.com/"
    
    def __init__(self, user_inputs=None):
        self.user_inputs = user_inputs
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt = "%(asctime)s - %(levelname)s - %(message)s",
            datefmt = "%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
     
    def validate_url(self,url):
        pattern = re.compile(
                r'^(http|https)://'              # Protocol (http or https)
                r'(www\.)?shoepalace\.com'       # Domain must be shoepalace.com, optionally prefixed with www
                r'(/[\w.-]*)*'                   # Optional path after the domain
                r'/?$', re.IGNORECASE            #looks for trailing "/" and ensures that the entire thing isnt case sensitive
                
                )
        if pattern.match(url):
                    return True
                    
        else:
            self.logger.error("Invalid Url")
            return False
        
  
    def validate_keywords(self,keywords):
        if isinstance(keywords, str):
            if ',' in keywords:
                keywords = keywords.split(',')
            else:
                keywords = keywords.split( )
        keywords =[keyword.strip() for keyword in keywords if keyword.strip()]
        for keyword in keywords:
            if not keyword.isalnum():  # Check if each keyword is alphanumeric
                self.logger.error(f"Invalid keyword: {keyword}")
                return False 

        return keywords #gives us a list of or keywords
            

    def validate_phoneNumber(self,phone_number):
        pattern = re.compile(r'^\d{3}-\d{3}-\d{4}')
        if pattern.match(phone_number):
            return True
        else:
            self.logger.error("Invalid Phone Number")
            return False


    def validate_email(self,email):
        # Define a robust regex pattern for email validation
        pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    
        # Check if the email matches the pattern
        if pattern.match(email):
            self.logger.info(f"The email currently being used is {email}")
            return True
        else:
            self.logger.error(f"Invalid Email: {email}")
            return False

  
    def validate_size(self,size):
        pattern= re.compile(r'^\d+(\.\d+)?$')

        if pattern.match(size):
            self.logger.info(f"The current selected size is {size}")
            return True
        else:
            self.logger.error("Invalid size input")
            return False
    
   
    def validate_style_code(self,style_code):
        pattern = re.compile(r'^\w{6}+-\w{3}$')

        if pattern.match(style_code):
            self.logger.info(f"The current selected style code is {style_code}")
            return True
        else:
            self.logger.error("Invalid style code input")
            return False
    
    def validate_quantity(self,new_quantity):
        pattern = re.compile(r'^\d+$')

        if pattern.match(new_quantity):
            self.logger.info(f"The current selected quantity is {new_quantity}")
            return True
        else:
            self.logger.error("Invalid quantity input")
            return False

    def validate_address(self, address):
        #Split address into different components (house number, street name, etc)
        house_number = self.extract_house_number(address)
        street_name = self.extract_street_name(address)
        #Still need to call city, since I need to use geonames api
        state = self.extract_state(address)
        country = self.extract_country(address)
        zipcode = self.extract_zipcode(address)

        #check the validation for each component, if not correct return false

        if not self.validate_house_number(house_number):
            self.logger.error(f"Invalid House Number: {house_number}")
            return False
        if not self.validate_street_name(street_name):
            self.logger.error(f"Invalid Street Name: {street_name}")
            return False
        
        #Still need to add the city

        if not self.validate_state(state):
            self.logger.error(f"Invalid State: {state}")
            return False
        if not self.validate_country(country):
            self.logger.error(f"Invalid Country: {country}")
            return False
        if not self.validate_zipcode(zipcode):
            self.logger.error(f"Invalid zipcode: {zipcode}")
            return False
        
        #if all components are true then return true
        return True
    #we have to also make sure that the address is not a po box address. We can use regex to check for that  ``

    def validate_house_number(self, house_number):
        pattern = re.compile(r'^\d+$')

        if pattern.match(house_number):
            return True
        else:
            self.logger.error(f"Invalid House Number: {house_number}")
            return False
        
    def validate_street_name(self, street_name):
        pattern = re.compile(r'^[a-zA-Z0-9\s\-]+$')

        if pattern.match(street_name):
            return True
        else:
            self.logger.error(f"Invalid Street Name: {street_name}")
            return False
    
    def validate_zipcode(self,zipcode):
        pattern = re.compile(r'^\d{5}(-\d{4})?$')

        if pattern.match(zipcode):
            self.logger.info(f"The current selected zipcode is {zipcode}")
            return True
        else:
            self.logger.error("Invalid zipcode input")
            return False
    
    def validate_country(self,country):
        country = country.strip().title()

        valid_countries = ["United States of America", "USA", "US"]

        if country in valid_countries:
            return True
        else:
            self.logger.error(f"Invalid Country: {country}")
            return False


    def validate_state(self,state):
        if state.upper() in self.US_STATES:
            self.logger.info(f"The current selected state is {state}")
            return True
        else:
            self.logger.error(f"Invalid state input,{state}is not a valid US state")
            return False

    def validate_city(self,city):
        pass
    #use geoname api to check if city is a valid city 

    def validate_payment_method(self, New_payment_method):
        #call all payment method functions to check if the payment method is valid
        card_number = self.extract_card_number(New_payment_method)
        card_expiry = self.extract_card_expiry(New_payment_method)
        card_cvv = self.extract_card_cvv(New_payment_method)
        card_name = self.extract_card_name(New_payment_method)
        card_address = self.extract_card_address(New_payment_method)

        if not self.validate_card_number(card_number):
            self.logger.error(f"Invalid Card Number: {card_number}")
            return False
        if not self.validate_card_expiry(card_expiry):
            self.logger.error(f"Invalid Card Expiry: {card_expiry}")
            return False
        if not self.validate_card_cvv(card_cvv):
            self.logger.error(f"Invalid Card CVV: {card_cvv}")
            return False
        if not self.validate_card_name(card_name):
            self.logger.error(f"Invalid Card Name: {card_name}")
            return False
        if not self.validate_card_address(card_address):
            self.logger.error(f"Invalid Card Address: {card_address}")
            return False
        
        return True


    def validate_card_number(self,card_number):
        #use regex to check if the card number is valid
        pattern = re.compile(r'^\d{13,19}$')

        if pattern.match(card_number):
            return True
        else:
            self.logger.error(f"Invalid Card Number: {card_number}")
            return False

    def validate_card_expiry(self,card_expiry):
        #use regex to check if the expiry is valid
        pattern = re.compile(r'^(0[1-9]|1[0-2])/(?:\d{2}|\d{4})$') # checks for MM/YY and MM/YYYY

        if pattern.match(card_expiry):
            return True
        else:
            self.logger.error(f"Invalid Card Expiry: {card_expiry}")
            return False

    def validate_card_cvv(self,card_cvv):
        #use regex to check if the cvv is valid
        pattern = re.compile(r'^\d{3,4}$')

        if pattern.match(card_cvv):
            return True
        else:
            self.logger.error(f"Invalid Card CVV: {card_cvv}")
            return False


    def validate_card_name(self,card_name):
    #use regex to check if the name is valid
        pattern = re.compile(r"^[a-zA-Z\s'-]+$")

        if pattern.match(card_name):
            return True
        else:
            self.logger.error(f"Invalid Card Name: {card_name}")
            return False

    def validate_card_address(self,card_address):
    #I think for now Im just gonna recall the address function, unless our address is different than our card's address
        if self.validate(card_address):
            return True
        else:
            self.logger.error(f"Invalid Card Address")
            return False

    def validate_card_zip(self,card_zip):
#use geoname api to check if zip is valid and use regex to check if it is a valid zip
#check with regex first and then use genoame api
        pass

    def validate_card_country(self,card_country):
#i mean this is a us only bot so we can just check if the country is US
        pass


    def validate_max_price(self,max_price):
        price = float(max_price)

        if price < 0:
            self.logger.error(f"Price is below 0: {price}")
            return False
        if price > 1000:                #optional
            self.logger.error(f"Price exceeds 1000: {price}")
            return False
        
        return True
    #this function needs to use selenium to verify that the price is not more than the max price
        

    #^clean the above functions because some can forsure be reused as they are essentially the same thing

    #below this section we will clean the user input 

    def validate_proxy_format(self, proxy_str):
        """
    Validates a proxy string like:
    http://user:pass@ip:port OR socks5://ip:port

    Returns True if valid, False otherwise.
    """
        pattern = re.compile(
            r"^(http|https|socks5)://"                    # scheme
            r"(?:(?:\w+:\w+)@)?"                          # optional user:pass@
            r"(?:\d{1,3}\.){3}\d{1,3}"                    # IP address
            r":\d{2,5}$"                                  # port
        )
        return bool(pattern.match(proxy_str.strip()))

    @staticmethod
    def check_for_file(file):# use this function to check if all the files for the application exist.
        try:
            if os.path.exists(file):
                return True
        except FileNotFoundError:
            logging.error(f"File not found: {file}")
            return False
    
    def check_user_data_json(self, user_data_json):
        """
        Validates the user data JSON file.
        Checks if the file exists and if it contains valid data.
        """
        if not self.check_for_file(user_data_json):
            self.logger.error(f"User data JSON file not found: {user_data_json}")
            return False
        
        
        try:
            with open(user_data_json, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'users' in data:
                    return True
                else:
                    self.logger.error("Invalid user data format.")
                    return False
        except json.JSONDecodeError:
            self.logger.error("Error decoding JSON from user data file.")
            return False
