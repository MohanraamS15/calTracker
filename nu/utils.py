import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def fetch_nutrition_from_perplexity(food_query):
    try:
        client = OpenAI(
            api_key=os.getenv("PERPLEXITY_API_KEY"),
            base_url="https://api.perplexity.ai"  # Pro access URL stays same
        )

        response = client.chat.completions.create(
            model="sonar-pro",  # 🔥 Use your Pro model
            messages=[
                {"role": "system", "content": "You're a certified dietitian. Reply in clean bullet points."},
                {
                "role": "user",
                "content": f"Give only the nutritional values for {food_query}.If the quantity is not given take by default of 100g for it.If only the count  is given(like 1 idly),then take it for the medium sized of the food ,and disply it. Reply in this format: Name: /n Calories: ___ kcal, Protein: ___ g, Fat: ___ g, Carbs: ___ g, Fiber: ___ g. Do not include explanations or brackets. Keep it short."

}

            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Perplexity Error: {str(e)}"
