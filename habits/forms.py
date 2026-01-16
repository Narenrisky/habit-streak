from django import forms
from .models import Habit

class HabitForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Habit
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        if not name:
            raise forms.ValidationError("Habit name cannot be empty.")

        if self.user:
            exists = Habit.objects.filter(
                user=self.user,
                name__iexact=name
            ).exists()
        else:
            exists = Habit.objects.filter(
                user__isnull=True,
                name__iexact=name
            ).exists()

        if exists:
            raise forms.ValidationError(
                "You already have a habit with this name."
            )
        return name
