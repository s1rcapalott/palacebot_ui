import logging 
import json
from Validator import Validator
import uuid


class UserProfile:
    PROFILES_FILE = "profiles.json"

    def __init__(self,first_name,last_name, email, phone_number, address, payment_method):
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%m-%d %H:%M:%S"))
        self.logger.addHandler(handler)

        self.validator = Validator()
        # We use email itself as our "ID"
        self.email = email
        self.phone_number = phone_number
        self.address = address
        self.payment_method = payment_method
        self.first_name = first_name
        self.last_name = last_name

    @property
    def email(self):
        return self._email
    @email.setter
    def email(self, val):
        if self.validator.validate_email(val):
            self._email = val
        else:
            self.logger.error("Invalid email")
            raise ValueError(val)
    @property
    def phonenumber(self):
        return self._phone_number
    @phonenumber.setter
    def phonenumber(self, val):
        if self.validator.validate_phone_number(val):
            self._phone_number = val
        else:
            self.logger.error("Invalid phone number")
            raise ValueError(val)
    
    @property
    def address(self):
        return self._address
    @address.setter
    def address(self, val):
        if self.validator.validate_address(val):
            self._address = val
        else:
            self.logger.error("Invalid address")
            raise ValueError(val)
    
    @property
    def paymentmethod(self):
        return self._payment_method
    
    
    @property
    def url(self):
        return self._url

    

    def to_dict(self):
        return {
            "email": self.email,
            "phone_number": self.phone_number,
            "address": self.address,
            "payment_method": self.payment_method
        }

    @classmethod
    def load_all(cls):
        try:
            with open(cls.PROFILES_FILE) as f:
                data = json.load(f)
            return [cls(**p) for p in data]
        except FileNotFoundError:
            return []

    def save(self):
        # Overwrite any profile with same email, then append this one
        profiles = [p.to_dict() for p in self.load_all() if p.email != self.email]
        profiles.append(self.to_dict())
        with open(self.PROFILES_FILE, "w") as f:
            json.dump(profiles, f, indent=2)
        self.logger.info(f"Profile for {self.email} saved.")


class TaskPreferences:
    TASKS_FILE = "tasks.json"

    def __init__(self, profile_email, url, quantity, style_code, keywords, size, color,
                 max_price=None, proxy_group="default", mode="fast"):
        self.logger = logging.getLogger(__name__)
        # Set up logging
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%m-%d %H:%M:%S"))
        self.logger.addHandler(handler)
        self.validator = Validator()
        self.profile_email = profile_email
        self.url           = url
        self.quantity      = quantity
        self.style_code    = style_code
        self.keywords      = keywords
        self.size          = size
        self.color         = color
        self.max_price     = max_price
        self.proxy_group   = proxy_group
        self.mode          = mode
        self.monitor_delay   = 1
        self.timeout         = 10
        self.error_delay      = 5
        self.id             = str(uuid.uuid4())  # Unique ID for each task

    def to_dict(self):
        return {
            "profile_email": self.profile_email,
            "url":           self.url,
            "quantity":      self.quantity,
            "style_code":    self.style_code,
            "keywords":      self.keywords,
            "size":          self.size,
            "color":         self.color,
            "max_price":     self.max_price,
            "proxy_group":   self.proxy_group,
            "mode":          self.mode,
            "monitor_delay":   1, 
            "timeout":         10,
            "error_delay":      5,
            "id":             self.id 
        }

    @classmethod
    def load_all(cls):
        try:
            with open(cls.TASKS_FILE) as f:
                data = json.load(f)
            return [cls(**t) for t in data]
        except FileNotFoundError:
            return []

    def save(self):
        # For simplicity, we won't dedupe tasks here; you could compare on all fields or add your own task name.
        tasks = self.load_all()
        tasks.append(self)
        with open(self.TASKS_FILE, "w") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=2)
        self.logger.info(f"Task for {self.profile_email} saved.")
    
    