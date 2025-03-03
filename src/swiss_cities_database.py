class SwissCitiesDatabase:
    def __init__(self):
        self.cities = {}

    def add_city(self, name, population, canton, location, languages, features):
        self.cities[name] = {
            "Population": population,
            "Canton": canton,
            "Geographic Location": location,
            "Main Language(s)": languages,
            "Notable Features": features
        }

    def get_city_info(self, name):
        return self.cities.get(name, None)

# Initialize and populate the database
swiss_cities = SwissCitiesDatabase()
swiss_cities.add_city("Zürich", 402762, "Zürich", "Northern Switzerland", ["German"], "Financial hub, largest city")
swiss_cities.add_city("Geneva", 203856, "Geneva", "Western Switzerland", ["French"], "International organizations, CERN")
swiss_cities.add_city("Basel", 172258, "Basel-Stadt", "Northwestern Switzerland", ["German"], "Pharmaceutical industry, art and culture")
swiss_cities.add_city("Bern", 133883, "Bern", "Central Switzerland", ["German"], "Capital city, UNESCO World Heritage Old Town")
swiss_cities.add_city("Lausanne", 139111, "Vaud", "Western Switzerland", ["French"], "Olympic Capital, university city")
swiss_cities.add_city("Winterthur", 111851, "Zürich", "Northern Switzerland", ["German"], "Cultural city, museums")
swiss_cities.add_city("Lucerne", 81592, "Lucerne", "Central Switzerland", ["German"], "Tourism, Lake Lucerne")
swiss_cities.add_city("St. Gallen", 75833, "St. Gallen", "Eastern Switzerland", ["German"], "Textile industry, University of St. Gallen")
swiss_cities.add_city("Lugano", 62615, "Ticino", "Southern Switzerland", ["Italian"], "Financial center, Mediterranean flair")
swiss_cities.add_city("Biel/Bienne", 55206, "Bern", "Northwestern Switzerland", ["German", "French"], "Bilingual city, watchmaking industry")
