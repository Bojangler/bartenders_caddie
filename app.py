from flask import Flask, render_template, request, session, url_for
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Load cocktail data from JSON file
with open('cocktails.json') as f:
    cocktail_data = json.load(f)

# Extract unique ingredients
all_ingredients = set()
for cocktail in cocktail_data:
    for ingredient in cocktail['ingredients']:
        all_ingredients.add(ingredient['name'])

sorted_ingredients = sorted(all_ingredients)

# Extract unique flavor profiles
all_flavor_profiles = set()
for cocktail in cocktail_data:
    for flavor in cocktail['flavor_profile']:
        all_flavor_profiles.add(flavor)

sorted_flavor_profiles = sorted(all_flavor_profiles)

def get_cocktails_you_can_make(inventory):
    available_cocktails = []
    for cocktail in cocktail_data:
        if all(ingredient['name'] in inventory for ingredient in cocktail['ingredients']):
            available_cocktails.append(cocktail)
    return available_cocktails

def count_additional_cocktails(inventory, ingredient_name):
    return sum(1 for cocktail in cocktail_data if len([ingredient['name'] for ingredient in cocktail['ingredients'] if ingredient['name'] not in inventory]) == 1 and any(ingredient['name'] == ingredient_name for ingredient in cocktail['ingredients']))

@app.route("/", methods=["GET", "POST"])
def index():
    if 'inventory' not in session:
        session['inventory'] = []

    if request.method == "POST":
        selected_ingredients = request.form.getlist('ingredients')
        session['inventory'] = selected_ingredients

    inventory = set(session['inventory'])
    cocktails_you_can_make = get_cocktails_you_can_make(inventory)
    additional_cocktails_counts = {ingredient: count_additional_cocktails(inventory, ingredient) for ingredient in sorted_ingredients}
    
    # Sort ingredients by additional cocktails count in descending order
    sorted_additional_ingredients = sorted(
        [ingredient for ingredient in sorted_ingredients if additional_cocktails_counts[ingredient] > 0],
        key=lambda x: additional_cocktails_counts[x],
        reverse=True
    )
    
    return render_template("index.html", sorted_ingredients=sorted_ingredients, inventory=inventory, cocktails_you_can_make=cocktails_you_can_make, additional_cocktails_counts=additional_cocktails_counts, sorted_additional_ingredients=sorted_additional_ingredients)

@app.route("/cocktail_profile/<cocktail_name>")
def cocktail_profile(cocktail_name):
    cocktail = next((c for c in cocktail_data if c['name'] == cocktail_name), None)
    if cocktail is None:
        return "Cocktail not found", 404
    return render_template("cocktail_profile.html", cocktail=cocktail)

@app.route("/all_cocktails")
def all_cocktails():
    sorted_cocktails = sorted(cocktail_data, key=lambda x: x['name'])
    inventory = set(session.get('inventory', []))
    cocktails_you_can_make = get_cocktails_you_can_make(inventory)
    
    for cocktail in sorted_cocktails:
        missing_ingredients = [ingredient['name'] for ingredient in cocktail['ingredients'] if ingredient['name'] not in inventory]
        cocktail['missing_ingredients'] = missing_ingredients
    
    return render_template("all_cocktails.html", sorted_cocktails=sorted_cocktails, cocktails_you_can_make=cocktails_you_can_make, inventory=inventory, sorted_flavor_profiles=sorted_flavor_profiles)

@app.route("/flavor_profile/<flavor>")
def flavor_profile(flavor):
    filtered_cocktails = [cocktail for cocktail in cocktail_data if flavor in cocktail['flavor_profile']]
    inventory = set(session.get('inventory', []))
    cocktails_you_can_make = get_cocktails_you_can_make(inventory)
    return render_template("all_cocktails.html", sorted_cocktails=filtered_cocktails, cocktails_you_can_make=cocktails_you_can_make, inventory=inventory, sorted_flavor_profiles=sorted_flavor_profiles)

@app.route("/ingredient_profile/<ingredient_name>")
def ingredient_profile(ingredient_name):
    # Filter cocktails that include the given ingredient
    filtered_cocktails = [
        cocktail for cocktail in cocktail_data
        if any(ingredient['name'] == ingredient_name for ingredient in cocktail['ingredients'])
    ]

    # Get a dictionary of associated ingredients and their cocktail counts
    associated_ingredients = {}
    for cocktail in filtered_cocktails:
        for ingredient in cocktail['ingredients']:
            if ingredient['name'] != ingredient_name:
                if ingredient['name'] not in associated_ingredients:
                    associated_ingredients[ingredient['name']] = 0
                associated_ingredients[ingredient['name']] += 1

    # Convert the dictionary to a list of tuples (ingredient, count) and sort by count (descending)
    associated_ingredients = sorted(
        associated_ingredients.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Filter cocktails the user can make
    inventory = set(session.get('inventory', []))
    cocktails_you_can_make = get_cocktails_you_can_make(inventory)
    filtered_cocktails_you_can_make = [
        cocktail for cocktail in filtered_cocktails if cocktail in cocktails_you_can_make
    ]

    # Count the number of distinct cocktails missing only this ingredient
    additional_cocktails_count = count_additional_cocktails(inventory, ingredient_name)

    return render_template(
        "ingredient_profile.html",
        ingredient_name=ingredient_name,
        filtered_cocktails=filtered_cocktails,
        filtered_cocktails_you_can_make=filtered_cocktails_you_can_make,
        additional_cocktails_count=additional_cocktails_count,
        associated_ingredients=associated_ingredients
    )

if __name__ == "__main__":
    app.run(debug=True) #REMOVE DEBUG=TRUE BEFORE DEPLOYMENT