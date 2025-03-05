from flask import Flask, render_template, request
import json

app = Flask(__name__)

# Load cocktail data from JSON file
with open('cocktails.json') as f:
    cocktail_data = json.load(f)

# Extract cocktail names and ingredients
cocktails = {cocktail['name']: [ingredient['name'] for ingredient in cocktail['ingredients']] for cocktail in cocktail_data}

# Extract unique flavor profiles
flavor_profiles = set()
for cocktail in cocktail_data:
    flavor_profiles.update(cocktail.get('flavor_profile', []))

def suggest_cocktails(available_ingredients):
    """
    Suggests cocktails based on available ingredients.
    """
    suggestions = []
    almost_suggestions = []
    missing_ingredients = {}
    ingredient_cocktail_count = {ingredient: 0 for ingredient in available_ingredients}
    
    for cocktail, ingredients in cocktails.items():
        missing = [ingredient for ingredient in ingredients if ingredient not in available_ingredients]
        if len(missing) == 0:
            suggestions.append((cocktail, ingredients))
            for ingredient in ingredients:
                if ingredient in ingredient_cocktail_count:
                    ingredient_cocktail_count[ingredient] += 1
        elif len(missing) <= 2:
            almost_suggestions.append((cocktail, missing))
            for ingredient in missing:
                if ingredient in missing_ingredients:
                    missing_ingredients[ingredient] += 1
                else:
                    missing_ingredients[ingredient] = 1

    return suggestions, almost_suggestions, missing_ingredients, ingredient_cocktail_count

@app.route("/", methods=["GET", "POST"])
def index():
    available_ingredients = []
    missing_ingredients = {}
    ingredient_cocktail_count = {}
    filter_ingredient = None
    filter_flavor_profile = None

    if request.method == "POST":
        available_ingredients = request.form.getlist("available_ingredients")
        missing_ingredients = request.form.getlist("missing_ingredients")
        filter_ingredient = request.form.get("filter_ingredient")
        filter_flavor_profile = request.form.get("filter_flavor_profile")

        # Move unchecked available ingredients to missing ingredients
        available_ingredients = [ing for ing in available_ingredients if ing in request.form.getlist("available_ingredients")]
        missing_ingredients = [ing for ing in missing_ingredients if ing not in request.form.getlist("missing_ingredients")]

        # Add checked missing ingredients to available ingredients
        available_ingredients += [ing for ing in request.form.getlist("missing_ingredients") if ing not in available_ingredients]

    suggested_cocktails, almost_suggested_cocktails, missing_ingredients, ingredient_cocktail_count = suggest_cocktails(available_ingredients)

    if filter_ingredient:
        suggested_cocktails = [(cocktail, ingredients) for cocktail, ingredients in suggested_cocktails if filter_ingredient in ingredients]
        almost_suggested_cocktails = [(cocktail, missing) for cocktail, missing in almost_suggested_cocktails if filter_ingredient in cocktails[cocktail]]

    if filter_flavor_profile:
        suggested_cocktails = [(cocktail['name'], cocktail['ingredients']) for cocktail in cocktail_data if filter_flavor_profile in cocktail.get('flavor_profile', []) and all(ingredient in available_ingredients for ingredient in [ingredient['name'] for ingredient in cocktail['ingredients']])]
        almost_suggested_cocktails = [(cocktail['name'], [ingredient['name'] for ingredient in cocktail['ingredients'] if ingredient['name'] not in available_ingredients]) for cocktail in cocktail_data if filter_flavor_profile in cocktail.get('flavor_profile', []) and any(ingredient['name'] not in available_ingredients for ingredient in cocktail['ingredients']) and len([ingredient['name'] for ingredient in cocktail['ingredients'] if ingredient['name'] not in available_ingredients]) <= 2]

    return render_template("index.html", suggestions=suggested_cocktails, almost_suggestions=almost_suggested_cocktails, available_ingredients=available_ingredients, missing_ingredients=missing_ingredients, ingredient_cocktail_count=ingredient_cocktail_count, filter_ingredient=filter_ingredient, flavor_profiles=sorted(flavor_profiles), filter_flavor_profile=filter_flavor_profile)

if __name__ == "__main__":
    app.run(debug=True) #REMOVE DEBUG=TRUE BEFORE DEPLOYMENT