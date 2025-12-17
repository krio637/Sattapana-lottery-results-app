from django.db import models

class LotteryResult(models.Model):
    date = models.DateField()
    state = models.CharField(max_length=100, help_text="e.g., Gali, Disawar, Faridabad, Ghaziabad")
    winning_number = models.CharField(max_length=10, blank=True, default='')
    result_time = models.CharField(max_length=20, blank=True, default='', help_text="Result announcement time (e.g., 05:00 AM)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'state']
        verbose_name = 'Lottery Result'
        verbose_name_plural = 'Lottery Results'
        unique_together = ['date', 'state']

    def __str__(self):
        return f"{self.state} - {self.date} - {self.winning_number}"

class Advertisement(models.Model):
    title = models.CharField(max_length=200, help_text="Advertisement title")
    image = models.ImageField(upload_to='ads/', blank=True, null=True, help_text="Upload advertisement image")
    text = models.TextField(help_text="Advertisement text/description")
    is_active = models.BooleanField(default=True, help_text="Show this advertisement")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Advertisement'
        verbose_name_plural = 'Advertisements'

    def __str__(self):
        return self.title
