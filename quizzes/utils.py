import os
import json
import time
import re
from groq import Groq
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

# API Key retrieval from Django settings or Environment
API_KEY = getattr(settings, "GROQ_API_KEY", None) or os.getenv("GROQ_API_KEY")

if API_KEY:
    client = Groq(api_key=API_KEY)
else:
    client = None

def generate_ai_questions(subcategory_name, difficulty, num_questions=5):
    """
    Generates MCQs and explanations in a single atomic API call.
    Includes robust JSON cleaning to handle Groq's markdown output.
    """
    if not client:
        print("Error: Groq API client not initialized.")
        return None

    prompt = f"""
    Generate {num_questions} multiple-choice questions about {subcategory_name} at {difficulty} level.
    
    The output MUST be a JSON object with this exact key: "questions".
    Each question must have:
    - "text": The question string.
    - "choices": An array of exactly 4 strings.
    - "correct_answer": The string matching one of the choices.
    - "explanation": A 2-sentence educational explanation of why the answer is correct.

    Example format:
    {{
      "questions": [
        {{
          "text": "Question?",
          "choices": ["A", "B", "C", "D"],
          "correct_answer": "A",
          "explanation": "..."
        }}
      ]
    }}
    Return ONLY JSON. No introductory text.
    """

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            chat_completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a quiz engine that outputs raw JSON only. Do not use markdown blocks like ```json."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                response_format={"type": "json_object"},
                timeout=30.0  # Increased timeout for complex generation
            )
            
            content = chat_completion.choices[0].message.content.strip()
            
            # --- ROBUST JSON CLEANING ---
            # Remove Markdown code blocks if present
            if content.startswith("```"):
                content = re.sub(r'^```json\s*|```\s*$', '', content, flags=re.MULTILINE)
            
            # Remove any trailing commas or hidden characters that break JSON
            content = content.strip()
            
            data = json.loads(content)
            questions = data.get('questions', [])
            
            if questions and len(questions) > 0:
                return questions
                
        except (json.JSONDecodeError, Exception) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries:
                time.sleep(1.5) # Wait a bit longer before retrying
            else:
                return None
    return None

def get_ai_explanation(question_text, correct_answer):
    """
    Used for Standard Mode quizzes when a database explanation is missing.
    """
    if not client:
        return "Explanation currently unavailable."

    prompt = (
        f"Question: {question_text}\n"
        f"Correct Answer: {correct_answer}\n"
        f"Task: Provide a 2-sentence explanation of why this is the correct answer. "
        f"Keep it professional and academic."
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating explanation: {e}")
        return "Check your study materials for more details."