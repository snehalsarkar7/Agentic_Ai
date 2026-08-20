from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
import requests
import os
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GET API KEYS FROM .ENV
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


# ============================================================
# CHECK API KEYS
# ============================================================

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing from .env"
    )

if not WEATHER_API_KEY:
    raise ValueError(
        "WEATHER_API_KEY is missing from .env"
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# TOOL 1 — ADD NUMBERS
# ============================================================

def add_numbers(a: float, b: float) -> dict:
    """
    Add two numbers together.

    Use this tool when the user wants:
    - addition
    - sum
    - adding two numbers
    """

    print("\n========================================")
    print("🔧 TOOL CALLED: add_numbers")
    print(f"   a = {a}")
    print(f"   b = {b}")
    print("========================================")

    result = a + b

    print(f"✅ TOOL RESULT: {result}")

    return {
        "operation": "addition",
        "a": a,
        "b": b,
        "result": result
    }


# ============================================================
# TOOL 2 — PRODUCT INFORMATION
# ============================================================

def product_info(product_name: str) -> dict:
    """
    Get information about a product.

    Use this tool when the user asks about:
    - product information
    - product price
    - smartphone price
    - laptop price
    - product category
    """

    print("\n========================================")
    print("🔧 TOOL CALLED: product_info")
    print(f"   Product = {product_name}")
    print("========================================")

    products = {

        "iphone 15": {
            "name": "iPhone 15",
            "category": "Smartphone",
            "price": 69999,
            "currency": "INR"
        },

        "samsung s24": {
            "name": "Samsung Galaxy S24",
            "category": "Smartphone",
            "price": 74999,
            "currency": "INR"
        },

        "macbook air": {
            "name": "MacBook Air",
            "category": "Laptop",
            "price": 99999,
            "currency": "INR"
        }

    }

    product = products.get(
        product_name.lower()
    )

    if product:

        print("✅ PRODUCT FOUND")
        print(product)

        return product

    print("❌ PRODUCT NOT FOUND")

    return {
        "error": f"Product '{product_name}' not found."
    }


# ============================================================
# TOOL 3 — WEATHER USING WEATHERAPI.COM
# ============================================================

def get_weather(city: str) -> dict:
    """
    Get current weather information for a city
    using WeatherAPI.com.

    Use this tool when the user asks about:
    - current weather
    - temperature
    - humidity
    - rain
    - wind
    - UV index
    - weather conditions
    """

    print("\n========================================")
    print("🌤️ TOOL CALLED: get_weather")
    print(f"   City = {city}")
    print("========================================")

    url = "https://api.weatherapi.com/v1/current.json"

    params = {
        "key": WEATHER_API_KEY,
        "q": city,
        "aqi": "no"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = response.json()

        # ----------------------------------------------------
        # WEATHER API ERROR
        # ----------------------------------------------------

        if response.status_code != 200:

            print("❌ WEATHER API ERROR")
            print(data)

            error_message = (
                data
                .get("error", {})
                .get(
                    "message",
                    "Unable to get weather information."
                )
            )

            return {
                "error": error_message
            }

        # ----------------------------------------------------
        # WEATHER RESULT
        # ----------------------------------------------------

        weather_result = {

            "city": data["location"]["name"],

            "region": data["location"]["region"],

            "country": data["location"]["country"],

            "local_time": data["location"]["localtime"],

            "temperature_celsius":
                data["current"]["temp_c"],

            "feels_like_celsius":
                data["current"]["feelslike_c"],

            "condition":
                data["current"]["condition"]["text"],

            "humidity_percent":
                data["current"]["humidity"],

            "wind_speed_kph":
                data["current"]["wind_kph"],

            "wind_direction":
                data["current"]["wind_dir"],

            "uv_index":
                data["current"]["uv"]

        }

        print("\n✅ WEATHER RESULT")
        print(weather_result)

        return weather_result

    except requests.exceptions.RequestException as e:

        print("\n❌ WEATHER REQUEST ERROR")
        print(e)

        return {
            "error": f"Weather API request failed: {str(e)}"
        }

    except Exception as e:

        print("\n❌ WEATHER TOOL ERROR")
        print(e)

        return {
            "error": str(e)
        }


# ============================================================
# REGISTER TOOLS
# ============================================================

tools = [

    add_numbers,

    product_info,

    get_weather

]


# ============================================================
# GEMINI CHAT SESSION
# ============================================================

chat = client.chats.create(

    model="gemini-3.6-flash",

    config=types.GenerateContentConfig(

        tools=tools,

        system_instruction="""

You are a helpful AI assistant with access to external tools.

You have the following tools:


============================================================
TOOL 1 — add_numbers
============================================================

Function:

add_numbers(a, b)

Use this tool whenever the user wants:

- addition
- sum of numbers
- adding two numbers
- basic addition calculations


Example:

User:
Add 25 and 75

Tool:
add_numbers(25, 75)


============================================================
TOOL 2 — product_info
============================================================

Function:

product_info(product_name)

Use this tool whenever the user asks about:

- product information
- product price
- smartphone price
- laptop price
- product category


Example:

User:
What is the price of iPhone 15?

Tool:
product_info("iPhone 15")


============================================================
TOOL 3 — get_weather
============================================================

Function:

get_weather(city)

Use this tool whenever the user asks about:

- current weather
- temperature
- humidity
- rain
- wind
- UV
- weather conditions
- weather of a particular city


Example:

User:
What is the weather in Jaipur?

Tool:
get_weather("Jaipur")


============================================================
IMPORTANT RULES
============================================================

1. Automatically select the appropriate tool.

2. Do NOT ask the user which tool to use.

3. When a tool can provide the requested information,
   use the tool.

4. For current weather information,
   ALWAYS use get_weather.

5. For product information,
   ALWAYS use product_info.

6. For addition calculations,
   ALWAYS use add_numbers.

7. Do not guess real-time information.

8. For questions that do not require a tool,
   answer normally.

9. After receiving a tool result, explain it clearly
   and naturally to the user.

10. Be concise and friendly.

"""

    )

)


# ============================================================
# HOME ROUTE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# CHAT ROUTE
# ============================================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat_api():

    try:

        # ----------------------------------------------------
        # GET USER MESSAGE
        # ----------------------------------------------------

        user_message = request.json.get(
            "message"
        )

        if not user_message:

            return jsonify({
                "reply": "Please enter a message."
            })

        # ----------------------------------------------------
        # PRINT USER MESSAGE
        # ----------------------------------------------------

        print("\n")
        print("============================================================")
        print("👤 USER MESSAGE")
        print("============================================================")
        print(user_message)
        print("============================================================")

        # ----------------------------------------------------
        # SEND TO GEMINI
        # ----------------------------------------------------

        response = chat.send_message(
            user_message
        )

        # ----------------------------------------------------
        # PRINT GEMINI RESPONSE
        # ----------------------------------------------------

        print("\n")
        print("============================================================")
        print("🤖 GEMINI RESPONSE")
        print("============================================================")
        print(response.text)
        print("============================================================")

        # ----------------------------------------------------
        # RETURN RESPONSE TO FRONTEND
        # ----------------------------------------------------

        return jsonify({

            "reply": response.text

        })

    except Exception as e:

        print("\n")
        print("============================================================")
        print("❌ ERROR")
        print("============================================================")
        print(str(e))
        print("============================================================")

        return jsonify({

            "reply": f"Error: {str(e)}"

        })


# ============================================================
# START APPLICATION
# ============================================================
if __name__ == "__main__":

    print("\n")
    print("============================================================")
    print("🚀 AGENTIC AI APPLICATION")
    print("============================================================")
    print("🤖 Model: Gemini 3.6 Flash")
    print("============================================================")
    print("🔧 AVAILABLE TOOLS")
    print("   1. add_numbers")
    print("   2. product_info")
    print("   3. get_weather")
    print("============================================================")
    print("🌐 SERVER")
    print("   http://0.0.0.0:5000")
    print("============================================================")
    print("\n")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )