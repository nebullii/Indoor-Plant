import os
import openai
from products.models import Product
from django.urls import reverse
import re

PROMPT_PATH = os.path.join(os.path.dirname(__file__), 'prompts', 'plant_qa.txt')

# Load the system prompt template
with open(PROMPT_PATH, 'r') as f:
    SYSTEM_PROMPT = f.read().strip()

openai.api_key = os.getenv('OPENAI_API_KEY')

def ask_plant_advisor(question):
    """
    Sends a plant-related question to the OpenAI API and returns the answer.
    """
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]   
    )
    answer = response.choices[0].message.content.strip()
    return answer

def ask_plant_advisor_with_links(question, request):
    answer = ask_plant_advisor(question)
    
    # First, replace markdown links [Plant Name](PRODUCT_LINK)
    markdown_link_pattern = re.compile(r'\[(.*?)\]\(PRODUCT_LINK\)')
    matches = markdown_link_pattern.findall(answer)
    already_linked = set()
    
    for plant_name in matches:
        try:
            # Try exact match first
            product = Product.objects.filter(name__iexact=plant_name).first()
            
            # If no exact match, try partial matches
            if not product:
                # Try matching against name that contains the plant name
                product = Product.objects.filter(name__icontains=plant_name.split('(')[0].strip()).first()
            
            # If still no match, try matching common plant names
            if not product:
                # Handle common variations
                plant_variations = {
                    'Snake Plant': 'Snake Plant (Sansevieria)',
                    'Pothos': 'Pothos (Epipremnum aureum)', 
                    'Peace Lily': 'Peace Lily (Spathiphyllum)',
                    'ZZ Plant': 'ZZ Plant (Zamioculcas zamiifolia)',
                    'Aloe Vera': 'Aloe Vera (Aloe barbadensis)',
                    'Sansevieria': 'Snake Plant (Sansevieria)'
                }
                
                for variation, full_name in plant_variations.items():
                    if variation.lower() in plant_name.lower():
                        product = Product.objects.filter(name__icontains=variation).first()
                        break
            
            if product:
                url = request.build_absolute_uri(reverse('products:product_detail', args=[product.slug]))
                answer = re.sub(rf'\[{re.escape(plant_name)}\]\(PRODUCT_LINK\)', 
                              f"<a href='{url}' target='_blank' style='color: #28a745; text-decoration: none; font-weight: bold;'>{plant_name}</a>", 
                              answer, count=1)
                already_linked.add(plant_name.lower())
                already_linked.add(product.name.lower())
            else:
                # Remove the link format but keep the plant name
                answer = re.sub(rf'\[{re.escape(plant_name)}\]\(PRODUCT_LINK\)', plant_name, answer, count=1)
                
        except Exception as e:
            # Remove the link format but keep the plant name
            answer = re.sub(rf'\[{re.escape(plant_name)}\]\(PRODUCT_LINK\)', plant_name, answer, count=1)
    
    # Then, linkify any plain plant names not already linked (more conservative approach)
    for product in Product.objects.all():
        # Split product name to get just the common name
        common_name = product.name.split('(')[0].strip()
        
        if product.name.lower() not in already_linked and common_name.lower() not in already_linked:
            url = request.build_absolute_uri(reverse('products:product_detail', args=[product.slug]))
            
            # Only replace standalone mentions, not parts of other words
            pattern = re.compile(rf'\b({re.escape(common_name)})\b(?![^<]*</a>)', re.IGNORECASE)
            answer = pattern.sub(f"<a href='{url}' target='_blank' style='color: #28a745; text-decoration: none; font-weight: bold;'>{common_name}</a>", answer, count=1)
    
    return answer

def find_plant_links(text):
    links = []
    text = text.lower()
    # Remove punctuation for better matching
    text = re.sub(r'[^\w\s]', '', text)
    for product in Product.objects.all():
        product_name = product.name.lower()
        product_name_clean = re.sub(r'[^\w\s]', '', product_name)
        if product_name in text or product_name_clean in text:
            url = reverse('products:product_detail', args=[product.slug])
            links.append((url, product.name))
    return links 