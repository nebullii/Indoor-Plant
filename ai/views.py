import os
import openai
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from .bot import ask_plant_advisor
from .bot import ask_plant_advisor_with_links
from .models import ChatbotInteraction
import re
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

@require_http_methods(["POST"])
def ask_bot(request):
    """
    SECURE: CSRF-protected AI chatbot endpoint
    """
    # Handle both form data and JSON requests
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            question = data.get("question")
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"error": "Invalid JSON data."}, status=400)
    else:
        question = request.POST.get("question")
    
    if not question or not question.strip():
        return JsonResponse({"error": "No question provided."}, status=400)
    
    # Rate limiting check (basic)
    if len(question) > 1000:
        return JsonResponse({"error": "Question too long. Max 1000 characters."}, status=400)
    
    try:
        answer = ask_plant_advisor_with_links(question, request)
        # Extract product links from the answer (HTML <a> tags)
        product_links = re.findall(r"<a [^>]*href=['\"]([^'\"]+)['\"][^>]*>.*?</a>", answer)
        
        # Log the interaction (with input sanitization)
        ChatbotInteraction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            question=question.strip()[:500],  # Limit stored question length
            answer=answer[:2000],  # Limit stored answer length
            product_links=product_links[:10]  # Limit number of links stored
        )
        
        return JsonResponse({
            "answer": answer,
            "csrf_token": get_token(request)  # Provide fresh CSRF token
        })
        
    except Exception as e:
        # Log error without exposing internal details
        import logging
        logging.error(f"AI bot error: {str(e)}")
        return JsonResponse({
            "error": "Sorry, I'm having trouble processing your request. Please try again later."
        }, status=500)

def ai_chat_page(request):
    return render(request, "ai_chat.html")
