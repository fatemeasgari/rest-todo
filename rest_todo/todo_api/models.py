from django.db import models

class Task(models.Model):
    title = models.CharField ('Title' , max_length= 200)
    done = models.BooleanField ('Done!')

    def __str__ (self):
        return self.title    


