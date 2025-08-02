"""Some prepared variables"""

from countries_dictionary import countries
from countries_dictionary.russia import russia
from countries_dictionary.vietnam import vietnam
import json

json_countries = json.dumps(countries, indent=4)
"""A JSON string converted from the countries dictionary, having an indent level of 4"""

json_russia = json.dumps(russia, indent=4)
"""A JSON string converted from the Russia dictionary, having an indent level of 4"""

json_vietnam = json.dumps(vietnam, indent=4)
"""A JSON string converted from the Vietnam dictionary, having an indent level of 4"""

countries_france_censored = countries
countries_france_censored["Fr*nce"] = countries_france_censored.pop("France")
countries_france_censored = dict(sorted(countries_france_censored.items()))
"""The countries dictionary with the `France` key gets censored `Fr*nce`
(This is only a joke, I don't support hate against France and French)"""

countries_area_sorted = dict(sorted(countries.items(), key=lambda item: item[1]["area"], reverse=True))
"""The countries dictionary sorted by area (from most to least)"""

countries_population_sorted = dict(sorted(countries.items(), key=lambda item: item[1]["population"], reverse=True))
"""The countries dictionary sorted by population (from most to least)"""

russia_subjects_area_sorted = dict(sorted(russia.items(), key=lambda item: item[1]["area"], reverse=True))
"""The Russia dictionary sorted by area (from most to least)"""

russia_subjects_population_sorted = dict(sorted(russia.items(), key=lambda item: item[1]["population"], reverse=True))
"""The Russia dictionary sorted by area (from most to least)"""

vietnam_provinces_area_sorted = dict(sorted(vietnam.items(), key=lambda item: item[1]["area"], reverse=True))
"""The Vietnam dictionary sorted by area (from most to least)"""

vietnam_provinces_population_sorted = dict(sorted(vietnam.items(), key=lambda item: item[1]["population"], reverse=True))
"""The Vietnam dictionary sorted by area (from most to least)"""