from django.db import models

class Space(models.Model):
    
    # Best way to create admin(s) ? -> read how to implement roles
    # & normal members ? 
    
    # you could use related_name in serializer query (try) 

    class Meta:
        verbose_name = 'Space'
        verbose_name_plural = 'Spaces'

    