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
- ✅ Meal History View with Timestamped Logs
- ✅ PostgreSQL support for production
- 🔄 Fully Functional UI (Responsiveness in progress)

---

## ⚙️ Tech Stack

| Layer       | Tech Used                             |
|------------|-------------------------------------   |
| 💻 Frontend | HTML5, CSS3, JavaScript (vanilla)     |
| 🧠 Backend  | Python 3.12, Django 5.1.6             |
| 🗂️ Database | PostgreSQL(local), PostgreSQL (Render)|
| 🤖 AI APIs  | Open AI API                           |
| ☁️ Hosting  | Render                                |

```bash
# 1. Clone the Repo
git clone https://github.com/MohanraamS15/calTracker.git
cd calTracker

# 2. Create Virtual Environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Run Migrations
python manage.py migrate

# 5. Start the Development Server
python manage.py runserver
