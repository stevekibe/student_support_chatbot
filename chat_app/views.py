from django.shortcuts import render

import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file (ensure this runs)
load_dotenv()

def home_view(request):
    return render(request, 'index.html') 

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file or environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-pro" # Or "gemini-1.5-flash" for potentially faster/cheaper responses

# --- Knowledge Base (Your FAQs) ---
KNOWLEDGE_BASE = """
## University Student Support FAQ Knowledge Base

**Admissions:**
- **Q:** How do I apply for admission?
  **A:** To apply, please visit our official admissions page: [https://www.university.edu/admissions](https://www.university.edu/admissions). You'll find application forms, deadlines, and requirements there.
- **Q:** What are the admission requirements for international students?
  **A:** International students must meet specific English proficiency requirements (e.g., TOEFL, IELTS), academic transcripts, and visa documentation. Detailed information is available on the international admissions section of our website.

**Financial Aid:**
- **Q:** How do I apply for financial aid?
  **A:** You can find comprehensive information about financial aid, scholarships, and FAFSA deadlines on the Financial Aid Office website: [https://www.university.edu/financialaid](https://www.university.edu/financialaid).
- **Q:** What scholarships are available?
  **A:** Information on available scholarships, eligibility criteria, and application procedures is on the Financial Aid Office website. We offer various merit-based, need-based, and departmental scholarships.

**Registration & Academics:**
- **Q:** How do I register for classes?
  **A:** Course registration typically opens a few weeks before the start of each semester. You can register via your student portal. Check the academic calendar for exact dates and deadlines.
- **Q:** Where can I find my academic advisor?
  **A:** Your academic advisor's contact information is usually available in your student portal under your 'Academic Profile' or 'Advising' section. If you can't find it, contact the Registrar's Office.
- **Q:** How do I view my grades?
  **A:** You can view your grades by logging into your student portal and accessing the 'Academic Records' or 'Grades' section.
- **Q:** How do I withdraw from a course?
  **A:** To withdraw from a course, please consult the academic calendar for withdrawal deadlines and follow the instructions on your student portal under 'Course Registration'. Be aware that withdrawing after certain dates may result in a 'W' grade or tuition implications.

**Campus Life & Services:**
- **Q:** Where is the Registrar's Office located?
  **A:** The Registrar's Office is located on the first floor of the Main Administration Building, Room 102.
- **Q:** What are the library hours?
  **A:** The library's operating hours vary by day and during holidays. Please check the official library website for the most current schedule: [https://www.university.edu/library](https://www.university.edu/library).
- **Q:** How do I get a student ID card?
  **A:** New student ID cards are issued at the Campus Services office. You'll need a valid government-issued ID. Replacements for lost cards can also be obtained there for a small fee.
- **Q:** Where can I find a campus map?
  **A:** A detailed campus map is available on the university's main website under 'Campus Life' or 'About Us'. You can also find it here: [https://www.university.edu/campusmap](https://www.university.edu/campusmap).
- **Q:** How can I contact student support?
  **A:** If you need further assistance, you can contact student support at support@university.edu or call us at (123) 456-7890 during business hours (Monday-Friday, 9 AM - 5 PM).
- **Q:** What career services are available?
  **A:** Our Career Services office offers resume reviews, interview preparation, job search assistance, and career counseling. Visit their website to book an appointment: [https://www.university.edu/careerservices](https://www.university.edu/careerservices).
"""

# Initialize the Gemini model
model = genai.GenerativeModel(MODEL_NAME)

@csrf_exempt # This decorator is important for allowing POST requests without CSRF token checking
def chat_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')

            if not user_message:
                return JsonResponse({"response": "Please enter a message."}, status=400)

            # Construct the prompt for the LLM
            prompt = (
                f"You are a helpful and polite university student support chatbot. "
                f"Your goal is to answer student questions based *only* on the provided knowledge base. "
                f"If the answer is not in the knowledge base, politely state that you don't have that information "
                f"and suggest contacting student support or visiting the relevant department's website. "
                f"Maintain a helpful and friendly tone.\n\n"
                f"**Knowledge Base:**\n{KNOWLEDGE_BASE}\n\n"
                f"**Student Query:** \"{user_message}\"\n\n"
                f"**Chatbot Response:**"
            )

            # Generate response using Gemini
            response = model.generate_content(prompt)
            bot_response = response.text

            return JsonResponse({"response": bot_response})

        except json.JSONDecodeError:
            return JsonResponse({"response": "Invalid JSON in request body."}, status=400)
        except Exception as e:
            print(f"Error processing chat: {e}")
            return JsonResponse({"response": "I'm sorry, an error occurred. Please try again later."}, status=500)
    else:
        return JsonResponse({"response": "Only POST requests are allowed."}, status=405)
