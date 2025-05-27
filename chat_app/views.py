# chat_app/views.py

from django.shortcuts import render

import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file (ensure this runs)
load_dotenv()

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file or environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "models/gemini-1.5-flash-latest" # Or "gemini-1.5-flash" for potentially faster/cheaper responses

# --- TEMPORARY DEBUGGING CODE: List Available Gemini Models ---
# This section will print models that support 'generateContent' to your terminal
# when the Django server starts. Use this to confirm 'gemini-pro' is available
# and to get its exact name (e.g., 'models/gemini-pro').
print("\n--- Available Gemini Models (for debugging) ---")
found_gemini_pro_for_content = False
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- Found model: {m.name} (Supports generateContent)")
            if m.name == 'gemini-pro' or m.name == 'models/gemini-pro':
                found_gemini_pro_for_content = True
except Exception as e:
    print(f"Error listing models: {e}")
print("---------------------------------------------")

if not found_gemini_pro_for_content:
    print("\nWARNING: 'gemini-pro' or 'models/gemini-pro' not found with 'generateContent' support.")
    print("This often indicates an issue with your API key, billing, or regional availability.")
    print("Please verify your GEMINI_API_KEY and Google Cloud project settings.")
# --- END TEMPORARY DEBUGGING CODE ---


# Initialize the Gemini model
# This line will use the MODEL_NAME defined above.
# If 'gemini-pro' isn't found or accessible, this is where the 404 error occurs.
model = genai.GenerativeModel(MODEL_NAME)

# --- Knowledge Base Path Definition ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, 'knowledge_base.json')

# --- Function to load and format the knowledge base ---
def load_and_format_knowledge_base(json_path):
    formatted_kb = []
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            category = item.get("category", "General")
            questions = item.get("question_phrasings", [])
            answer = item.get("answer", "No answer provided.")

            formatted_kb.append(f"Category: {category}")
            if questions:
                formatted_kb.append(f"Common Questions: {', '.join(questions)}")
            formatted_kb.append(f"Answer: {answer}\n---")

    except FileNotFoundError:
        print(f"ERROR: knowledge_base.json NOT FOUND at expected path: {json_path}")
        return "Knowledge base not loaded."
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON syntax in {json_path}. Please check its format.")
        return "Knowledge base failed to parse."
    except Exception as e:
        print(f"ERROR: An unexpected error occurred loading knowledge base: {e}")
        return "Knowledge base loading error."

    return "\n\n".join(formatted_kb)

KNOWLEDGE_BASE_STRING = load_and_format_knowledge_base(KNOWLEDGE_BASE_PATH)

if "Knowledge base not loaded." in KNOWLEDGE_BASE_STRING or \
   "Knowledge base failed to parse." in KNOWLEDGE_BASE_STRING:
    print("FATAL ERROR: Knowledge base could not be loaded. Chatbot may not function correctly.")

# --- Chat Endpoint ---
@csrf_exempt
def chat_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')

            if not user_message:
                return JsonResponse({"response": "Please enter a message."}, status=400)

            prompt = (
                f"You are a helpful and polite university student support chatbot. "
                f"Your goal is to answer student questions based *only* on the provided knowledge base. "
                f"If the answer is not in the knowledge base, politely state that you don't have that information "
                f"and suggest contacting student support or visiting the relevant department's website. "
                f"Maintain a helpful and friendly tone.\n\n"
                f"**Knowledge Base:**\n{KNOWLEDGE_BASE_STRING}\n\n"
                f"**Student Query:** \"{user_message}\"\n\n"
                f"**Chatbot Response:**"
            )

            response = model.generate_content(prompt)
            bot_response = response.text

            return JsonResponse({"response": bot_response})

        except json.JSONDecodeError:
            return JsonResponse({"response": "Invalid JSON in request body."}, status=400)
        except Exception as e:
            # This 'e' should now contain the Google API 404 error if it's still happening
            print(f"Error processing chat: {e}")
            return JsonResponse({"response": "I'm sorry, an error occurred. Please try again later."}, status=500)
    else:
        return JsonResponse({"response": "Only POST requests are allowed."}, status=405)

# --- Home View (for serving your index.html) ---
def home_view(request):
    return render(request, 'index.html')

# --- Knowledge Base Test View ---
def knowledge_base_test_view(request):
    return JsonResponse({"knowledge_base_content": KNOWLEDGE_BASE_STRING})