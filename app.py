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

def get_cocktails_you_can_make(inventory):
    available_cocktails = []
    for cocktail in cocktail_data:
        if all(ingredient['name'] in inventory for ingredient in cocktail['ingredients']):
            available_cocktails.append(cocktail)
    return available_cocktails

@app.route("/", methods=["GET", "POST"])
def index():
    if 'inventory' not in session:
        session['inventory'] = []

    if request.method == "POST":
        selected_ingredients = request.form.getlist('ingredients')
        session['inventory'] = selected_ingredients

    inventory = set(session['inventory'])
    cocktails_you_can_make = get_cocktails_you_can_make(inventory)
    return render_template("index.html", sorted_ingredients=sorted_ingredients, inventory=inventory, cocktails_you_can_make=cocktails_you_can_make)

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
    return render_template("all_cocktails.html", sorted_cocktails=sorted_cocktails, cocktails_you_can_make=cocktails_you_can_make)

@app.route("/ingredient_profile/<ingredient_name>")
def ingredient_profile(ingredient_name):
    filtered_cocktails = [cocktail for cocktail in cocktail_data if any(ingredient['name'] == ingredient_name for ingredient in cocktail['ingredients'])]
    inventory = set(session.get('inventory', []))
    cocktails_you_can_make = get_cocktails_you_can_make(inventory)
    filtered_cocktails_you_can_make = [cocktail for cocktail in filtered_cocktails if cocktail in cocktails_you_can_make]
    return render_template("ingredient_profile.html", ingredient_name=ingredient_name, filtered_cocktails=filtered_cocktails, filtered_cocktails_you_can_make=filtered_cocktails_you_can_make)

if __name__ == "__main__":
    app.run(debug=True) #REMOVE DEBUG=TRUE BEFORE DEPLOYMENT