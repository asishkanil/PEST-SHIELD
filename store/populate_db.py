from store.models import Pest, Pesticide

# Define the pest-to-pesticide mapping
pest_data = {
    "aphids": ["Imidacloprid", "Bifenthrin", "Cyfluthrin", "Lambda-cyhalothrin", "Malathion"],
    "armyworm": ["Bacillus Thuringiensis", "Lambda-cyhalothrin", "Imidacloprid", "Thiamethoxam", "Chlorpyrifos"],
    "beetle": ["Pyrethroid"],
    "bollworm": ["Pyrethroid", "Organophosphates"],
    "grasshopper": ["Organophosphates", "Pyrethroid"],
    "mites": ["Miticide Oils", "Pyrethroid", "Organophosphates"],
    "mosquito": ["Larvicides", "Pyrethroid", "Organophosphates"],
    "sawfly": ["Pyrethroid"],
    "stem borer": ["Pyrethroid", "Organophosphates"],
}

# Insert data into the database
for pest_name, pesticides in pest_data.items():
    pest, _ = Pest.objects.get_or_create(name=pest_name)
    for pesticide_name in pesticides:
        Pesticide.objects.get_or_create(pest=pest, name=pesticide_name)

print("Database populated successfully!")
