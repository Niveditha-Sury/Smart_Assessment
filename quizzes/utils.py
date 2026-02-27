import os
import json
import time
from groq import Groq
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

API_KEY = getattr(settings, "GROQ_API_KEY", None) or os.getenv("GROQ_API_KEY")

if API_KEY:
    client = Groq(api_key=API_KEY)
else:
    client = None


def get_ai_explanation(question_text, correct_answer):
    """
    Generates a brief explanation for why a specific answer is correct.
    """
    if not client:  # Ensure your Groq/OpenAI client is initialized
        return "Explanation currently unavailable."

    prompt = (
        f"Question: {question_text}\n"
        f"Correct Answer: {correct_answer}\n"
        f"Task: Provide a 2-sentence explanation of why this is the correct answer. "
        f"Keep it encouraging and educational."
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Or your preferred model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating explanation: {e}")
        return "Check your study materials for more details on this topic."

def generate_ai_questions(subcategory_name, difficulty, num_questions=5):
    if not client:
        print("Error: Groq API client not initialized.")
        return None

    # Refined prompt for better consistency
    prompt = f"""
    Generate {num_questions} multiple-choice questions about {subcategory_name} at {difficulty} level.
    
    The output MUST be a JSON object with this exact key: "questions".
    Each question must have:
    - "text": The question string.
    - "choices": An array of exactly 4 strings.
    - "correct_answer": The string matching one of the choices.

    Example format:
    {{
      "questions": [
        {{
          "text": "...",
          "choices": ["...", "...", "...", "..."],
          "correct_answer": "..."
        }}
      ]
    }}
    Return ONLY JSON.
    """

    # Retry logic to handle temporary network issues or model hiccups
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            chat_completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a quiz engine that outputs raw JSON only. Do not include conversational text."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                response_format={"type": "json_object"},
                timeout=25.0 # Set explicit timeout to prevent hanging
            )
            
            content = chat_completion.choices[0].message.content
            data = json.loads(content)
            questions = data.get('questions', [])
            
            if questions:
                return questions
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries:
                time.sleep(1) # Wait before retrying
            else:
                return None
    return None