# filepath: /c:/Users/rossw/Documents/bartenders_caddie/app.py
from flask import Flask, render_template, request

app = Flask(__name__)

# Cocktail Database (Simplified)
cocktails = {
    "Mojito": ["rum", "mint", "lime", "sugar", "soda water"],
    "Margarita": ["tequila", "lime juice", "cointreau"],
    "Old Fashioned": ["bourbon", "sugar", "bitters", "water"],
    "Cosmopolitan": ["vodka", "cointreau", "lime juice", "cranberry juice"],
    "Manhattan": ["rye whiskey", "sweet vermouth", "bitters"],
    "Daiquiri": ["rum", "lime juice", "sugar"],
    "Gin and Tonic": ["gin", "tonic water", "lime"],  # corrected gin and tonic
    "Moscow Mule": ["vodka", "ginger beer", "lime juice"], #Added Moscow Mule
}

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

    if request.method == "POST":
        available_ingredients = request.form.getlist("available_ingredients")
        missing_ingredients = request.form.getlist("missing_ingredients")
        filter_ingredient = request.form.get("filter_ingredient")

        # Move unchecked available ingredients to missing ingredients
        available_ingredients = [ing for ing in available_ingredients if ing in request.form.getlist("available_ingredients")]
        missing_ingredients = [ing for ing in missing_ingredients if ing not in request.form.getlist("missing_ingredients")]

        # Add checked missing ingredients to available ingredients
        available_ingredients += [ing for ing in request.form.getlist("missing_ingredients") if ing not in available_ingredients]

    suggested_cocktails, almost_suggested_cocktails, missing_ingredients, ingredient_cocktail_count = suggest_cocktails(available_ingredients)

    if filter_ingredient:
        suggested_cocktails = [(cocktail, ingredients) for cocktail, ingredients in suggested_cocktails if filter_ingredient in ingredients]
        almost_suggested_cocktails = [(cocktail, missing) for cocktail, missing in almost_suggested_cocktails if filter_ingredient in cocktails[cocktail]]

    return render_template("index.html", suggestions=suggested_cocktails, almost_suggestions=almost_suggested_cocktails, available_ingredients=available_ingredients, missing_ingredients=missing_ingredients, ingredient_cocktail_count=ingredient_cocktail_count, filter_ingredient=filter_ingredient)

if __name__ == "__main__":
    app.run(debug=True) #REMOVE DEBUG=TRUE BEFORE DEPLOYMENT