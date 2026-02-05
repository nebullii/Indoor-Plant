from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatbotInteraction(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    question = models.TextField()
    answer = models.TextField()
    product_links = models.JSONField(null=True, blank=True)  # List of product URLs or slugs
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatbotInteraction({self.user}, {self.created_at})"
