from django.db import models


class Proxy(models.Model):
    ip = models.CharField(max_length=15)
    port = models.PositiveSmallIntegerField()
    user = models.CharField(max_length=32)
    password = models.CharField(max_length=32)

    class Meta:
        verbose_name = "Прокси"
        verbose_name_plural = "Прокси"
        
    def __str__(self):
        return f"http://{self.user}:{self.password}@{self.ip}:{self.port}"
