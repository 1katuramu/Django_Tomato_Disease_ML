from django.db import models

class TomatoImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    prediction = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"Tomato Image {self.id} - {self.prediction}"
