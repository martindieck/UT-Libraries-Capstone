import pycountry

def get_country_code(country_name):
    try:
        country = pycountry.countries.search_fuzzy(country_name)
        return country[0].alpha_2.lower()
    except LookupError:
        return "none"