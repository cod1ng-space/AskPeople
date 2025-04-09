from app.models import Tag, User
from django.core.cache import cache

# Глобальный контекст
def global_context(request):
    popular_tags = Tag.objects.popular()
    
    return {
        'popular_tags': popular_tags,
    }