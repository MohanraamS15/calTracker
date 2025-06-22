# 🍽️ CalTracker – AI-Powered Calorie & Meal Planner

An AI-driven calorie tracker and meal planner built with **Django**.  
Track your daily meals, monitor nutrition intake, and get **AI-powered** meal suggestions based on your fitness goals.

Live Demo 👉 [caltracker-yuau.onrender.com](https://caltracker-yuau.onrender.com/)

---

## 🔥 Features

- ✅ User Signup/Login
- ✅ TDEE-based Daily Calorie & Macro Goals
- ✅ Meal Logging with Real-time Nutrition Info
- ✅ AI-Powered Meal Recommendations using Google Gemini
- ✅ Meal Preferences (Veg, High-Protein, etc.)
- ✅ Food Exclusion Filters (e.g. No Eggs, No Sugar)
- ✅ Per-Meal Calorie Target System
- ✅ Full-Day Nutrition Summary (Calories, Protein, Carbs, Fats, Fiber)
- ✅ PostgreSQL support for production
- ✅ Fully Functional UI

---

## ⚙️ Tech Stack

| Layer       | Tech Used                            |
|------------|---------------------------------------|
| 💻 Frontend | HTML5, CSS3, JavaScript (vanilla)    |
| 🧠 Backend  | Python 3.12, Django 5.1.6             |
| 🗂️ Database | PostgreSQL (local & production)       |
| 🤖 AI APIs  | Perplexity API, Google Gemini API    |
| ☁️ Hosting  | Render                               |


```bash
# Clone the repository
git clone https://github.com/MohanraamS15/calTracker.git
cd calTracker

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up your local PostgreSQL DATABASE_URL in .env file
# Example .env content:
# DATABASE_URL=postgres://username:password@localhost:5432/dbname

# Export your environment variable (skip if using .env loader)
export DATABASE_URL=postgres://username:password@localhost:5432/dbname

# Run migrations and start the server
python manage.py migrate
python manage.py runserver

