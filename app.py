from flask import Flask, render_template, request, session, url_for, redirect
import json
import os  # Import os for environment variable access

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_secret_key')  # Use a secure secret key from environment variables

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

def initialize_inventory():
    if "inventory" not in session:
        session["inventory"] = []
        print("Initialized inventory in session.")  # Debugging line

@app.route("/", methods=["GET", "POST"])
def index():
    if 'inventory' not in session:
        session['inventory'] = []
        print("Initialized inventory in session.")  # Debugging line

    if request.method == "POST":
        selected_ingredients = request.form.getlist('ingredients')
        session['inventory'] = selected_ingredients
        print(f"Updated inventory: {session['inventory']}")  # Debugging line

    inventory = set(session['inventory'])
    print(f"Current inventory: {inventory}")  # Debugging line
    cocktails_you_can_make = get_cocktails_you_can_make(inventory)
    additional_cocktails_counts = {ingredient: count_additional_cocktails(inventory, ingredient) for ingredient in sorted_ingredients}
    
    # Sort ingredients by additional cocktails count in descending order
    sorted_additional_ingredients = sorted(
        [ingredient for ingredient in sorted_ingredients if additional_cocktails_counts[ingredient] > 0],
        key=lambda x: additional_cocktails_counts[x],
        reverse=True
    )
    
    return render_template(
        "index.html",
        sorted_ingredients=sorted_ingredients,
        inventory=inventory,
        cocktails_you_can_make=cocktails_you_can_make,
        additional_cocktails_counts=additional_cocktails_counts,
        sorted_additional_ingredients=sorted_additional_ingredients
    )

@app.route("/cocktail_profile/<cocktail_name>")
def cocktail_profile(cocktail_name):
     # Ensure inventory is initialized
    initialize_inventory()

    # Find the cocktail by name
    cocktail = next((c for c in cocktail_data if c['name'] == cocktail_name), None)
    if cocktail is None:
        return "Cocktail not found", 404

    # Get the user's inventory
    inventory = set(session.get('inventory', []))

    # Determine which ingredients are missing
    missing_ingredients = [
        ingredient['name'] for ingredient in cocktail['ingredients']
        if ingredient['name'] not in inventory
    ]

    # Calculate additional cocktails counts for the modal
    additional_cocktails_counts = {
        ingredient: count_additional_cocktails(inventory, ingredient)
        for ingredient in sorted_ingredients
    }

    # Pass the cocktail, inventory, missing ingredients, and modal data to the template
    return render_template(
        "cocktail_profile.html",
        cocktail=cocktail,
        inventory=inventory,
        missing_ingredients=missing_ingredients,
        sorted_ingredients=sorted_ingredients,
        additional_cocktails_counts=additional_cocktails_counts
    )
@app.route("/all_cocktails")
def all_cocktails():
    # Sort cocktails alphabetically
    sorted_cocktails = sorted(cocktail_data, key=lambda c: c['name'])

    # Get the user's inventory
    inventory = set(session.get('inventory', []))

    # Add missing ingredients to each cocktail
    for cocktail in sorted_cocktails:
        cocktail['missing_ingredients'] = [
            ingredient['name'] for ingredient in cocktail['ingredients']
            if ingredient['name'] not in inventory
        ]

    # Filter cocktails the user can make
    cocktails_you_can_make = [
        cocktail for cocktail in sorted_cocktails if not cocktail['missing_ingredients']
    ]

    # Calculate additional cocktails counts for the modal
    additional_cocktails_counts = {
        ingredient: count_additional_cocktails(inventory, ingredient)
        for ingredient in sorted_ingredients
    }

    # Pass the required variables to the template
    return render_template(
        "all_cocktails.html",
        sorted_cocktails=sorted_cocktails,
        cocktails_you_can_make=cocktails_you_can_make,
        sorted_ingredients=sorted_ingredients,
        inventory=inventory,
        additional_cocktails_counts=additional_cocktails_counts
    )

@app.route("/flavor_profile/<flavor>")
def flavor_profile(flavor):
    filtered_cocktails = [cocktail for cocktail in cocktail_data if flavor in cocktail['flavor_profile']]
    inventory = set(session.get('inventory', []))
    cocktails_you_can_make = get_cocktails_you_can_make(inventory)
    return render_template("all_cocktails.html", sorted_cocktails=filtered_cocktails, cocktails_you_can_make=cocktails_you_can_make, inventory=inventory, sorted_flavor_profiles=sorted_flavor_profiles)

@app.route("/ingredient_profile/<ingredient_name>")
def ingredient_profile(ingredient_name):
    # Ensure inventory is initialized
    initialize_inventory()

    # Filter cocktails that include the given ingredient
    filtered_cocktails = [
        cocktail for cocktail in cocktail_data
        if any(ingredient['name'] == ingredient_name for ingredient in cocktail['ingredients'])
    ]

    # Get the user's inventory
    inventory = set(session.get('inventory', []))

    # Add missing ingredients to each cocktail
    for cocktail in filtered_cocktails:
        cocktail['missing_ingredients'] = [
            ingredient['name'] for ingredient in cocktail['ingredients']
            if ingredient['name'] not in inventory
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
    cocktails_you_can_make = [
        cocktail for cocktail in filtered_cocktails if not cocktail['missing_ingredients']
    ]

    # Count the number of distinct cocktails missing only this ingredient
    additional_cocktails_count = count_additional_cocktails(inventory, ingredient_name)

    # Calculate additional cocktails counts for the modal
    additional_cocktails_counts = {
        ingredient: count_additional_cocktails(inventory, ingredient)
        for ingredient in sorted_ingredients
    }

    # Pass the required variables to the template
    return render_template(
        "ingredient_profile.html",
        ingredient_name=ingredient_name,
        filtered_cocktails=filtered_cocktails,
        filtered_cocktails_you_can_make=cocktails_you_can_make,
        additional_cocktails_count=additional_cocktails_count,
        associated_ingredients=associated_ingredients,
        sorted_ingredients=sorted_ingredients,
        inventory=inventory,
        additional_cocktails_counts=additional_cocktails_counts
    )

@app.route("/add_to_inventory", methods=["POST"])
def add_to_inventory():
    print("add_to_inventory route triggered.")  # Debugging line
    ingredient = request.form.get("ingredient")
    print(f"Ingredient received: {ingredient}")  # Debugging line
    if "inventory" not in session:
        session["inventory"] = []
        print("Initialized inventory in session.")  # Debugging line
    if ingredient and ingredient not in session["inventory"]:
        session["inventory"].append(ingredient)
        print(f"Added {ingredient} to inventory.")  # Debugging line
    else:
        print(f"{ingredient} is already in inventory or invalid.")  # Debugging line
    return redirect(url_for("index", expand="ingredients"))

if __name__ == "__main__":
    app.run(debug=True)  # Replace with app.run(debug=True) if you want to run in debug mode