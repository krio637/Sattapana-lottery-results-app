from django import forms
from .models import LotteryResult, Advertisement

class LotteryResultForm(forms.ModelForm):
    class Meta:
        model = LotteryResult
        fields = ['date', 'state', 'winning_number', 'result_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter state name'}),
            'winning_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter winning number', 'maxlength': '10'}),
            'result_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 05:00 AM', 'maxlength': '20'}),
        }

class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['title', 'image', 'text', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter advertisement title'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter advertisement text', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
