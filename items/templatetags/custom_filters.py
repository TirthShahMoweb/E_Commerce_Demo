from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Retrieve a value from the dictionary with a given key."""
    key = str(key)  # Convert the key to string
    return dictionary.get(key, 0)  

@register.filter(name='multiply')
def calc(price,quantity):
   return price*quantity