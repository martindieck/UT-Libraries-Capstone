# Using the pycountry API to obtain two-letter country codes
import pycountry

def get_country_code(country_name):
    """Function to obtain two-letter country code from country name.
    Input: Country name as a string.
    Returns: two-letter country code
    """
    try:
        country = pycountry.countries.search_fuzzy(country_name) # Using fuzzy search to include partial matches as well
        return country[0].alpha_2.lower()
    except LookupError:
        return "none"