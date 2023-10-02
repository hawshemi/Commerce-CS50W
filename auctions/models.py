from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length = 64)
    description = models.TextField()
    starting_bid = models.FloatField(validators = [MinValueValidator(1)])
    img_url = models.URLField(blank = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "owner")
    category = models.CharField(blank = True, max_length = 64)
    active = models.BooleanField(blank = False, default = True)
    winner = models.ForeignKey(User, blank = True, on_delete = models.CASCADE, related_name = "new_owner", null = True)
    
    def __str__(self):
        return (f"{self.title} - {self.description} \t Starting Bid = {self.starting_bid}")
    
class Bid(models.Model):
    value = models.FloatField(validators = [MinValueValidator(1)])
    listing = models.ForeignKey(Listing, verbose_name = "price", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    winner = models.BooleanField(default = False)
    
    def __str__(self):
        return (f"A bid of {self.value} made for the item - \n{self.listing}\n by user - {self.user}")
    
class Comment(models.Model):
    content = models.TextField()
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete = models.CASCADE)
    
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = False)
    listing = models.ForeignKey(Listing, on_delete = models.CASCADE, blank = False)