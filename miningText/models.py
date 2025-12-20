from django.db import models

# Create your models here.
class Article(models.Model):
    titre = models.CharField(max_length=200)
    auteur = models.CharField(max_length=100)
    contenu = models.TextField()
    date_publication = models.DateTimeField(""" auto_now_add=True """)
    date_modification = models.DateTimeField(auto_now=True)

    discours = models.FileField(upload_to='discours/', null=True, blank=True)

    
    def __str__(self):
        return self.titre
    
    class Meta:
        ordering = ['-date_publication']
