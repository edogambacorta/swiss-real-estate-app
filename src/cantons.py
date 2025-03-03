# Swiss Cantons

CANTONS = {
    "AG": "Aargau",
    "AR": "Appenzell Ausserrhoden",
    "AI": "Appenzell Innerrhoden",
    "BL": "Basel-Landschaft",
    "BS": "Basel-Stadt",
    "BE": "Bern",
    "FR": {"de": "Freiburg", "fr": "Fribourg"},
    "GE": {"fr": "Genève", "en": "Geneva"},
    "GL": "Glarus",
    "GR": {"de": "Graubünden", "it": "Grigioni", "rm": "Grischun", "en": "Grisons"},
    "JU": "Jura",
    "LU": {"de": "Luzern", "en": "Lucerne"},
    "NE": "Neuchâtel",
    "NW": "Nidwalden",
    "OW": "Obwalden",
    "SH": "Schaffhausen",
    "SZ": "Schwyz",
    "SO": "Solothurn",
    "SG": "St. Gallen",
    "TG": "Thurgau",
    "TI": "Ticino",
    "UR": "Uri",
    "VS": {"de": "Wallis", "fr": "Valais"},
    "VD": "Vaud",
    "ZG": "Zug",
    "ZH": {"de": "Zürich", "en": "Zurich"}
}

def get_canton_name(canton_code, language='en'):
    """
    Get the canton name for a given canton code and language.
    
    :param canton_code: Two-letter canton code (e.g., 'ZH' for Zurich)
    :param language: Language code ('en', 'de', 'fr', 'it', or 'rm')
    :return: Canton name in the specified language if available, otherwise in the default language
    """
    canton = CANTONS.get(canton_code.upper())
    if isinstance(canton, dict):
        return canton.get(language, canton.get('en', list(canton.values())[0]))
    return canton

def get_all_canton_names(language='en'):
    """
    Get a list of all canton names in the specified language.
    
    :param language: Language code ('en', 'de', 'fr', 'it', or 'rm')
    :return: List of canton names
    """
    return [get_canton_name(code, language) for code in CANTONS.keys()]

def get_canton_code(canton_name):
    """
    Get the canton code for a given canton name.
    
    :param canton_name: Canton name (in any language)
    :return: Two-letter canton code if found, None otherwise
    """
    canton_name_lower = canton_name.lower()
    for code, names in CANTONS.items():
        if isinstance(names, dict):
            if canton_name_lower in [name.lower() for name in names.values()]:
                return code
        elif canton_name_lower == names.lower():
            return code
    return None
