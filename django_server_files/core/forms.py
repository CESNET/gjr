from django import forms

class PlayHistory(forms.Form):
    history_moment = forms.IntegerField(widget=forms.NumberInput(attrs={'type':'range', 'step': '1', 'min': '0', 'max': '100'}), required=False)
