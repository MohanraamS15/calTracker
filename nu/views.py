from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def index(request):
    return render(request, 'index.html')

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

        context = {
            "tdee": tdee,
            "protein": protein,
            "fat": fat,
            "carbs": carbs,
            "fiber": fiber,
        }

        return render(request, "result.html", context)

    return render(request, "profile.html")
