from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from .utils import fetch_nutrition_from_perplexity
import json
from django.utils import timezone



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
@csrf_exempt
def log_meal(request):
    if request.method == "POST":
        meal_type = request.POST.get("meal_type", "").title()
        food = request.POST.get("food", "").strip()
        quantity = request.POST.get("quantity", "").strip()

        # Block empty food name
        if not food:
            return redirect("log_meal")  # Or show a message if needed

        prompt = f"Find the nutrition info (calories, protein, fat, carbs, fiber) for {quantity} {food}"
        result = fetch_nutrition_from_perplexity(prompt)

        meal = {
            "food": f"{quantity} {food}",
            "raw_response": result,
            "calories": extract_number(result, "Calories"),
            "protein": extract_number(result, "Protein"),
            "fat": extract_number(result, "Fat"),
            "carbs": extract_number(result, "Carbs"),
            "fiber": extract_number(result, "Fiber"),
            "timestamp": timezone.now().strftime("%I:%M %p"),
        }

        if "logged_meals" not in request.session:
            request.session["logged_meals"] = {}

        if meal_type not in request.session["logged_meals"]:
            request.session["logged_meals"][meal_type] = []

        request.session["logged_meals"][meal_type].append(meal)
        request.session.modified = True

    # Show page
    return render(request, "meal_log.html", {
        "logged_meals": request.session.get("logged_meals", {}),
        "totals": calculate_total_macros(request.session.get("logged_meals", {})),
    })


def calculate_total_macros(meals):
    totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "fiber": 0}
    for meal_list in meals.values():
        for item in meal_list:
            totals["calories"] += item.get("calories", 0)
            totals["protein"] += item.get("protein", 0)
            totals["fat"] += item.get("fat", 0)
            totals["carbs"] += item.get("carbs", 0)
            totals["fiber"] += item.get("fiber", 0)
    return totals

    

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
    recommendation_list = []

    if request.method == "POST":
        preference = request.POST.get("preference", "")
        exclusions = request.POST.get("exclusions", "")
        remaining_calories = request.POST.get("remaining_calories", "")
        selected_meal_type = request.POST.get("meal_type", "Breakfast")

        user_prompt = f"""
        Suggest 2 or 3 {preference} meal options under {remaining_calories} calories.
        Exclude these: {exclusions}.
        For each meal, give dish name and macro breakdown: Calories, Protein, Fat, Carbs, Fiber.
        """

        full_response = fetch_nutrition_from_perplexity(user_prompt)

        # Split the response into separate meal blocks (assuming AI response is separated by double newlines)
        raw_meals = [block.strip() for block in full_response.strip().split("\n\n") if block.strip()]

        # Limit to 3 meals max (optional)
        recommendation_list = raw_meals[:3]

    return render(request, "recommend_meal.html", {
        "recommendation_list": recommendation_list
    })


@csrf_exempt
def delete_meal(request):
    if request.method == "POST":
        meal_type = request.POST.get("meal_type")
        index = int(request.POST.get("index"))

        if "logged_meals" in request.session:
            meals = request.session["logged_meals"].get(meal_type, [])
            if 0 <= index < len(meals):
                meals.pop(index)
                request.session.modified = True

        return redirect("log_meal")
