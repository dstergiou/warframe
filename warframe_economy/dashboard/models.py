from django.db import models

   
class PrimeItem(models.Model):
    name = models.CharField(max_length=200, unique=True)
    url_name = models.CharField(max_length=200, unique=True, blank=True)
    ducats = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1)
    primeset_name = models.CharField(max_length=200)
    primeset_url = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.url_name:
            self.url_name = self.name.lower().replace(' ', '_')
        if not self.primeset_url:
            self.primeset_url = self.primeset_name.lower().replace(' ', '_')
        super(PrimeItem, self).save(*args, **kwargs)
    


# class Collection(models.Model):
#     name = models.CharField(max_length=200, unique=True)
#     url_name = models.CharField(max_length=200, unique=True, blank=True)
#     quantity = models.PositiveIntegerField(default=1)
#     prime_set = models.ForeignKey(PrimeSet, on_delete=models.CASCADE)
