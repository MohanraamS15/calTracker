from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .utils import fetch_nutrition_from_perplexity
import json, re, datetime

def home(request):
    return render(request, 'home.html')  # Make sure home.html exists!

@csrf_exempt
def index(request):
    nutrition_data = ""
    
    if request.method == "POST":
        user_input = request.POST.get("food_input", "").strip()
        if user_input:
            nutrition_data = fetch_nutrition_from_perplexity(user_input)
        else:
            nutrition_data = "Please enter a valid food item."
    
    return render(request, 'index.html', {'nutrition_data': nutrition_data})

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

@csrf_exempt
def signup_view(request):
    """Enhanced signup view with better validation and error handling"""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        
        # Validation
        errors = []
        
        if not username:
            errors.append("Username is required")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters long")
        elif User.objects.filter(username=username).exists():
            errors.append("Username already exists")
            
        if not email:
            errors.append("Email is required")
        elif User.objects.filter(email=email).exists():
            errors.append("Email already registered")
            
        if not password:
            errors.append("Password is required")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters long")
            
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        if errors:
            return render(request, "signup.html", {
                "errors": errors,
                "username": username,
                "email": email
            })
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username, 
                email=email, 
                password=password
            )
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("profile")
            
        except IntegrityError:
            return render(request, "signup.html", {
                "errors": ["An error occurred while creating your account. Please try again."],
                "username": username,
                "email": email
            })
    
    return render(request, "signup.html")

@csrf_exempt
def login_view(request):
    """Enhanced login view with better validation"""
    if request.user.is_authenticated:
        return redirect('log_meal')
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        
        if not username or not password:
            return render(request, "login.html", {
                "error": "Both username and password are required",
                "username": username
            })
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            # Redirect to next page if provided, otherwise to log_meal
            next_page = request.GET.get('next', 'log_meal')
            return redirect(next_page)
        else:
            return render(request, "login.html", {
                "error": "Invalid username or password",
                "username": username
            })
    
    return render(request, "login.html")

@login_required
def logout_view(request):
    """Logout view with confirmation message"""
    username = request.user.username
    logout(request)
    messages.info(request, f"Goodbye, {username}! You have been logged out.")
    return redirect("login")

@login_required
@csrf_exempt
def profile_view(request):
    """Enhanced profile view for authenticated users"""
    if request.method == "POST":
        try:
            # Get and validate user input
            current_weight = float(request.POST.get('current_weight', 0))
            target_weight = float(request.POST.get('target_weight', 0))
            height = float(request.POST.get('height', 0))
            age = int(request.POST.get('age', 0))
            gender = request.POST.get('gender', '')
            activity_level = request.POST.get('activity_level', '')
            goal = request.POST.get('goal', '')

            # Basic validation
            if not all([current_weight, target_weight, height, age, gender, activity_level]):
                messages.error(request, "Please fill in all required fields")
                return render(request, "profile.html")

            if age < 10 or age > 100:
                messages.error(request, "Please enter a valid age (10-100)")
                return render(request, "profile.html")

            if height < 100 or height > 250:
                messages.error(request, "Please enter a valid height in cm (100-250)")
                return render(request, "profile.html")

            # Calculate TDEE and macros
            tdee, protein, fat, carbs, fiber = calculate_tdee_and_nutrition(
                age, gender, height, current_weight, target_weight, activity_level
            )

            # Get calorie split from AI
            prompt = f"""
            I need to split a total of {tdee} kcal into 5 meals:
            - Breakfast
            - Morning Snack
            - Lunch
            - Evening Snack
            - Dinner
            Give the ideal calorie distribution per meal as JSON format only.
            """
            
            response = fetch_nutrition_from_perplexity(prompt)
            
            try:
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    calorie_split = json.loads(match.group())
                else:
                    raise ValueError("No JSON found in response")
            except:
                # Fallback split
                calorie_split = {
                    "Breakfast": int(tdee * 0.25),
                    "Morning Snack": int(tdee * 0.10),
                    "Lunch": int(tdee * 0.30),
                    "Evening Snack": int(tdee * 0.10),
                    "Dinner": int(tdee * 0.25)
                }

            # Store in session
            request.session['calorie_split'] = calorie_split
            request.session['daily_targets'] = {
                "calories": tdee,
                "protein": protein,
                "fat": fat,
                "carbs": carbs,
                "fiber": fiber
            }
            request.session['tdee'] = tdee
            request.session['user_profile'] = {
                "current_weight": current_weight,
                "target_weight": target_weight,
                "height": height,
                "age": age,
                "gender": gender,
                "activity_level": activity_level,
                "goal": goal
            }

            messages.success(request, "Profile updated successfully!")
            return redirect('log_meal')
            
        except ValueError as e:
            messages.error(request, "Please enter valid numeric values")
            return render(request, "profile.html")
        except Exception as e:
            messages.error(request, "An error occurred while updating your profile")
            return render(request, "profile.html")
    
    # Get existing profile data from session if available
    user_profile = request.session.get('user_profile', {})
    return render(request, "profile.html", {"user_profile": user_profile})

@csrf_exempt
def profile(request):
    """Legacy profile view - redirects to authenticated version"""
    if request.user.is_authenticated:
        return redirect('profile_view')
    else:
        return redirect('login')



def extract_number(text, key):
    """Extracts a float number after a keyword like 'calories', 'protein' etc."""
    try:
        pattern = rf"{key}:\s*([0-9]+(?:\.[0-9]*)?)"
        match = re.search(pattern, text, re.IGNORECASE)
        return float(match.group(1)) if match else 0
    except:
        return 0

@login_required
def log_meal(request):
    if 'logged_meals' not in request.session:
        request.session['logged_meals'] = {}

    logged_meals = request.session['logged_meals']
    normalized_meals = {}
    for k, v in logged_meals.items():
        normalized_key = k.replace("_", " ")
        if normalized_key not in normalized_meals:
            normalized_meals[normalized_key] = []
        normalized_meals[normalized_key].extend(v)
    logged_meals = normalized_meals
    request.session['logged_meals'] = logged_meals

    calorie_split = request.session.get('calorie_split', {})
    daily_targets = request.session.get('daily_targets', {})

    if not daily_targets:
        messages.info(request, "Please set up your profile first")
        return redirect('profile_view')

    if request.method == 'POST':
        food = request.POST.get('food', '').strip()
        quantity = request.POST.get('quantity', '').strip()
        meal_type = request.POST.get('meal_type', '').replace("_", " ")

        if not food or not quantity:
            messages.error(request, "Please enter both food and quantity")
            return redirect('log_meal')

        nutrition_query = f"{quantity} {food}"
        response = fetch_nutrition_from_perplexity(f"Nutrition facts for {nutrition_query}")

        nutrition = {
            'calories': extract_number(response, 'calories') or 100,
            'protein': extract_number(response, 'protein') or 5,
            'fat': extract_number(response, 'fat') or 2,
            'carbs': extract_number(response, 'carbs') or 20,
            'fiber': extract_number(response, 'fiber') or 1,
            'food': f"{quantity} {food}",
            'timestamp': datetime.datetime.now().strftime("%I:%M %p")
        }

        if meal_type not in logged_meals:
            logged_meals[meal_type] = []

        logged_meals[meal_type].append(nutrition)
        request.session['logged_meals'] = logged_meals
        request.session.modified = True

        messages.success(request, f"Added {food} to {meal_type}")
        return redirect('log_meal')

    # Totals
    meal_totals = {meal: 0 for meal in calorie_split}
    totals = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0, 'fiber': 0}

    for meal_type, meals in logged_meals.items():
        meal_totals.setdefault(meal_type, 0)
        for meal in meals:
            meal_totals[meal_type] += meal.get('calories', 0)
            totals['calories'] += meal.get('calories', 0)
            totals['protein'] += meal.get('protein', 0)
            totals['fat'] += meal.get('fat', 0)
            totals['carbs'] += meal.get('carbs', 0)
            totals['fiber'] += meal.get('fiber', 0)

    remaining = {
        key: round(daily_targets.get(key, 0) - totals.get(key, 0), 1)
        for key in totals
    }

    context = {
        'logged_meals': logged_meals,
        'totals': totals,
        'remaining': remaining,
        'meal_targets': calorie_split,
        'meal_totals': meal_totals,
        'daily_targets': daily_targets,
    }
    return render(request, 'meal_log.html', context)



# @login_required
# @csrf_exempt
# def recommend_meal(request):
#     recommendation_list = []
#     remaining_calories = request.session.get('daily_targets', {}).get('calories', 2000)

#     if request.method == "POST":
#         preference = request.POST.get("preference", "")
#         exclusions = request.POST.get("exclusions", "")
#         remaining_calories = request.POST.get("remaining_calories", str(remaining_calories))
#         selected_meal_type = request.POST.get("meal_type", "Breakfast")

#         if not preference:
#             messages.error(request, "Please specify your meal preference")
            
#             # Get meal data from session for context
#             logged_meals = request.session.get('logged_meals', {})
#             calorie_split = request.session.get('calorie_split', {})

#             # Calculate meal totals
#             meal_totals = {}
#             for meal_type, meals in logged_meals.items():
#                 meal_totals[meal_type] = sum(meal.get('calories', 0) for meal in meals)

#             # Normalize meal names for consistency
#             normalized_calorie_split = {}
#             for key, value in calorie_split.items():
#                 normalized_key = key.replace(" ", "_")
#                 normalized_calorie_split[normalized_key] = value

#             return render(request, "recommend_meal.html", {
#                 "recommendation_list": recommendation_list,
#                 "remaining_calories": remaining_calories,
#                 "meal_targets": normalized_calorie_split,
#                 "meal_totals": meal_totals
#             })

#         user_prompt = f"""
#         Suggest 2 or 3 {preference} meal options under {remaining_calories} calories for {selected_meal_type}.
#         Exclude these: {exclusions}.
#         For each meal, give dish name and macro breakdown: Calories, Protein, Fat, Carbs, Fiber.
#         Format each suggestion clearly with nutritional information.
#         """

#         try:
#             full_response = fetch_nutrition_from_perplexity(user_prompt)
#             raw_meals = [block.strip() for block in full_response.strip().split("\n\n") if block.strip()]
#             recommendation_list = raw_meals[:3]
            
#             if not recommendation_list:
#                 messages.warning(request, "No recommendations found. Try adjusting your preferences.")
                
#         except Exception as e:
#             messages.error(request, "Unable to get meal recommendations at this time")

#     # Get meal data from session for display
#     logged_meals = request.session.get('logged_meals', {})
#     calorie_split = request.session.get('calorie_split', {})

#     # Calculate meal totals
#     meal_totals = {}
#     for meal_type, meals in logged_meals.items():
#         meal_totals[meal_type] = sum(meal.get('calories', 0) for meal in meals)

#     # Normalize meal names for consistency (replace spaces with underscores)
#     normalized_calorie_split = {}
#     for key, value in calorie_split.items():
#         normalized_key = key.replace(" ", "_")
#         normalized_calorie_split[normalized_key] = value

#     # Also normalize meal_totals keys
#     normalized_meal_totals = {}
#     for key, value in meal_totals.items():
#         normalized_key = key.replace(" ", "_")
#         normalized_meal_totals[normalized_key] = value

#     return render(request, "recommend_meal.html", {
#         "recommendation_list": recommendation_list,
#         "remaining_calories": remaining_calories,
#         "meal_targets": normalized_calorie_split,
#         "meal_totals": normalized_meal_totals
#     })

@login_required
@csrf_exempt
def delete_meal(request):
    if request.method == "POST":
        meal_type = request.POST.get("meal_type")
        index = int(request.POST.get("index"))

        if "logged_meals" in request.session:
            meals = request.session["logged_meals"].get(meal_type, [])
            if 0 <= index < len(meals):
                deleted_meal = meals.pop(index)
                request.session.modified = True
                messages.success(request, f"Removed {deleted_meal.get('food', 'meal')} from {meal_type}")
            else:
                messages.error(request, "Meal not found")

        return redirect("log_meal")

@login_required
def split_tdee_view(request):
    tdee = request.session.get("tdee", 2000)

    prompt = f"""
    I need to split a total of {tdee} kcal into 5 meals:
    - Breakfast
    - Morning Snack
    - Lunch
    - Evening Snack
    - Dinner
    Give the ideal calorie distribution per meal, formatted as JSON only.
    """

    try:
        response = fetch_nutrition_from_perplexity(prompt)

        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            calorie_split = json.loads(match.group())
            request.session['calorie_split'] = calorie_split
        else:
            calorie_split = {"error": "Could not parse response as JSON"}
    except Exception as e:
        calorie_split = {"error": str(e)}

    return render(request, "tdee_split_result.html", {
        "tdee": tdee,
        "response": response,
        "calorie_split": calorie_split
    })



from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# Dummy AI recommendation function (replace this with Gemini API)
def generate_ai_meal_recommendations(meal_type, target_calories, preference, exclusions):
    base_meals = {
        "Breakfast": ["Oats with fruits", "Scrambled eggs with toast", "Banana smoothie"],
        "Morning_Snack": ["Greek yogurt", "Nuts and seeds", "Fruit bowl"],
        "Lunch": ["Grilled chicken with veggies", "Paneer salad", "Brown rice and dal"],
        "Evening_Snack": ["Boiled eggs", "Roasted chickpeas", "Protein shake"],
        "Dinner": ["Grilled fish and salad", "Quinoa with vegetables", "Moong dal khichdi"]
    }

    suggestions = base_meals.get(meal_type, [])[:3]

    if exclusions:
        excluded = [x.strip().lower() for x in exclusions.split(",")]
        suggestions = [m for m in suggestions if not any(e in m.lower() for e in excluded)]

    if preference:
        suggestions = [f"{meal} ({preference})" for meal in suggestions]

    return suggestions if suggestions else ["🥗 No meals matched your preferences. Try fewer restrictions."]

@login_required
@csrf_exempt
def recommend_meal(request):
    # Get data from session
    meal_targets = request.session.get('calorie_split', {})
    logged_meals = request.session.get('logged_meals', {})
    
    # Calculate meal totals
    meal_totals = {}
    for meal_type, meals in logged_meals.items():
        meal_totals[meal_type] = sum(meal.get('calories', 0) for meal in meals)
    
    # Normalize meal names for consistency (replace spaces with underscores for template)
    normalized_meal_targets = {}
    normalized_meal_totals = {}
    
    for key, value in meal_targets.items():
        normalized_key = key.replace(" ", "_")
        normalized_meal_targets[normalized_key] = value
    
    for key, value in meal_totals.items():
        normalized_key = key.replace(" ", "_")
        normalized_meal_totals[normalized_key] = value
    
    # Emoji dictionary for meals
    emoji_dict = {
        'breakfast': '🍳',
        'morning_snack': '🍎', 
        'lunch': '🍽️',
        'evening_snack': '🥨',
        'dinner': '🍛'
    }
    
    recommendation_list = []
    remaining_calories = 600  # default value
    
    if request.method == "POST":
        meal_type = request.POST.get("meal_type")
        remaining_calories = request.POST.get("remaining_calories")
        preference = request.POST.get("preference")
        exclusions = request.POST.get("exclusions", "")

        if not (meal_type and remaining_calories and preference):
            messages.error(request, "Please fill in all required fields.")
            return redirect("recommend_meal")

        try:
            target_kcal = int(remaining_calories)
        except ValueError:
            messages.error(request, "Invalid number for calories.")
            return redirect("recommend_meal")

        # Generate AI meal recommendations using your existing function
        recommendation_list = generate_ai_meal_recommendations(
            meal_type, target_kcal, preference, exclusions
        )
        
        # If no recommendations, provide fallback
        if not recommendation_list:
            recommendation_list = ["🥗 No meals matched your preferences. Try adjusting your criteria."]

    return render(request, "recommend_meal.html", {
    "meal_targets": normalized_meal_targets,
    "meal_totals": normalized_meal_totals,  # Changed from meal_totals to normalized_meal_totals
    "recommendation_list": recommendation_list,
    "remaining_calories": remaining_calories,
    "emoji_dict": emoji_dict,
})

