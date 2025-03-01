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
    for cocktail, ingredients in cocktails.items():
        missing_ingredients = [ingredient for ingredient in ingredients if ingredient not in available_ingredients]
        if len(missing_ingredients) == 0:
            suggestions.append(cocktail)
        elif len(missing_ingredients) <= 2:
            almost_suggestions.append((cocktail, missing_ingredients))
    return suggestions, almost_suggestions

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ingredients_str = request.form["ingredients"]
        ingredients = [ing.strip().lower() for ing in ingredients_str.split(",")]  # Split and clean

        suggested_cocktails, almost_suggested_cocktails = suggest_cocktails(ingredients)

        return render_template("index.html", suggestions=suggested_cocktails, almost_suggestions=almost_suggested_cocktails)
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True) #REMOVE DEBUG=TRUE BEFORE DEPLOYMENT