from django.db import models

# Create your models here.


class ScrapperOutput_withNumbers(models.Model):
    userid= models.CharField(max_length=50)
    links= models.TextField()
    Name= models.TextField()
    Price= models.CharField(max_length=100)
    Kilometers= models.CharField(max_length=100)
    Date= models.TextField()
    Power= models.TextField()
    Image= models.TextField()
    Number= models.TextField()
    def __str__(self):
        return self.Name

class ScrapperOutput_withoutNumbers(models.Model):
    userid= models.CharField(max_length=50)
    links= models.TextField()
    Name= models.TextField()
    Price= models.TextField()
    Kilometers= models.TextField()
    Date= models.TextField()
    Power= models.TextField()
    Image= models.TextField()
    def __str__(self):
        return self.Name
