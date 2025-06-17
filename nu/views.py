from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def profile(request):
    if request.method == 'POST':
        current_weight = float(request.POST.get('current_weight'))
        target_weight = float(request.POST.get('target_weight'))
        height = float(request.POST.get('height'))
        age = int(request.POST.get('age'))
        gender = request.POST.get('gender')
        activity_level = request.POST.get('activity_level')
        goal = request.POST.get('goal')

        # BMR Calculation using Mifflin-St Jeor Equation
        if gender == 'male':
            bmr = 10 * current_weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * current_weight + 6.25 * height - 5 * age - 161

        # Activity multiplier
        activity_factors = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }

        activity_factor = activity_factors.get(activity_level, 1.2)
        tdee = bmr * activity_factor  # Total Daily Energy Expenditure

        # Adjust calories based on goal
        if goal == 'lose':
            tdee -= 500
        elif goal == 'gain':
            tdee += 500

        # Nutrient Breakdown
        protein = round((0.8 * current_weight), 1)  # grams
        fat = round((0.3 * tdee) / 9, 1)           # grams
        carbs = round((0.5 * tdee) / 4, 1)         # grams
        fiber = 25  # Default recommended value

        return render(request, 'result.html', {
            'calories': round(tdee),
            'protein': protein,
            'fat': fat,
            'carbs': carbs,
            'fiber': fiber
        })

    return render(request, 'profile.html')
