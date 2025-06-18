from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from .utils import fetch_nutrition_from_perplexity
import json

import json 
@csrf_exempt
def index(request):
    nutrition_data = ""
    
    if request.method == "POST":
        user_input = request.POST.get("food_input", "").strip()
        if user_input:
            # 👇 Call your actual function that gets nutrition info
            nutrition_data = fetch_nutrition_from_perplexity(user_input)
        else:
            nutrition_data = "Please enter a valid food item."
    
    return render(request, 'index.html', {'nutrition_data': nutrition_data})


@csrf_exempt
# 👇 TDEE + Macro Calculator Function
def calculate_tdee_and_nutrition(age, gender, height, weight, target_weight, activity_level):
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    tdee = bmr * activity_factors.get(activity_level, 1.2)

    protein = 1.6 * target_weight
    fat = (0.25 * tdee) / 9
    remaining_cal = tdee - (protein * 4 + fat * 9)
    carbs = remaining_cal / 4
    fiber = 25

    return round(tdee), round(protein, 1), round(fat, 1), round(carbs, 1), fiber

# 👇 View to handle /profile form
def profile(request):
    if request.method == "POST":
        current_weight = float(request.POST['current_weight'])
        target_weight = float(request.POST['target_weight'])
        height = float(request.POST['height'])
        age = int(request.POST['age'])
        gender = request.POST['gender']
        activity_level = request.POST['activity_level']
        goal = request.POST['goal']


        tdee, protein, fat, carbs, fiber = calculate_tdee_and_nutrition(
            age, gender, height, current_weight, target_weight, activity_level
        )

        macro_data = {
    "protein": protein,
    "fat": fat,
    "carbs": carbs,
    "fiber": fiber,
}

        context = {
    "tdee": tdee,
    "protein": protein,
    "fat": fat,
    "carbs": carbs,
    "fiber": fiber,
    "macro_data_json": json.dumps(macro_data)
}

        return render(request, "result.html", context)

    return render(request, "profile.html")




@csrf_exempt
def log_meal(request):
    if request.method == "POST":
        meal_type = request.POST.get("meal_type", "")
        food_input = request.POST.get("food_input", "")
        result = fetch_nutrition_from_perplexity(food_input)

        # Dummy parse (you can improve formatting later)
        parsed = {
            "food": food_input,
            "raw_response": result,
            "calories": extract_number(result, "Calories"),
            "protein": extract_number(result, "Protein"),
            "fat": extract_number(result, "Fat"),
            "carbs": extract_number(result, "Carbs"),
            "fiber": extract_number(result, "Fiber"),
        }

        if "logged_meals" not in request.session:
            request.session["logged_meals"] = {}

        if meal_type not in request.session["logged_meals"]:
            request.session["logged_meals"][meal_type] = []

        request.session["logged_meals"][meal_type].append(parsed)
        request.session.modified = True

    # Calculate totals
    totals = {
        "calories": 0,
        "protein": 0,
        "fat": 0,
        "carbs": 0,
        "fiber": 0
    }

    for meals in request.session.get("logged_meals", {}).values():
        for item in meals:
            totals["calories"] += item.get("calories", 0)
            totals["protein"] += item.get("protein", 0)
            totals["fat"] += item.get("fat", 0)
            totals["carbs"] += item.get("carbs", 0)
            totals["fiber"] += item.get("fiber", 0)

    print("DEBUG TOTALS:", totals)

    return render(request, "meal_log.html", {
        "logged_meals": request.session.get("logged_meals", {}),
        "totals": totals
    })

    

# Helper function to extract numbers from string
def extract_number(text, key):
    try:
        import re
        pattern = rf"{key}:\s*([0-9]+(?:\.[0-9]*)?)"
        match = re.search(pattern, text)
        return float(match.group(1)) if match else 0
    except:
        return 0
    

@csrf_exempt
def recommend_meal(request):
    recommendation = ""
    if request.method == "POST":
        preference = request.POST.get("preference", "")
        exclusions = request.POST.get("exclusions", "")
        remaining_calories = request.POST.get("remaining_calories", "")

        user_prompt = f"""
        Create a {preference} meal plan for one meal under {remaining_calories} calories.
        Exclude these ingredients: {exclusions}.
        Provide the dish name and macro breakdown (Calories, Protein, Fat, Carbs, Fiber).
        """

        # Call Gemini or Perplexity
        recommendation = fetch_nutrition_from_perplexity(user_prompt)

    return render(request, 'recommend_meal.html', {"recommendation": recommendation})
