# diary/forms.py
from django import forms
from .models import QuestionSet, Question, QuestionSetStyle


# forms.py
class QuestionSetCreateForm(forms.ModelForm):
    class Meta:
        model = QuestionSet
        fields = ['title', 'description', 'style']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter styles based on user plan
        if user and user.userprofile.plan == 'free':
            self.fields['style'].queryset = QuestionSetStyle.objects.all()
            self.fields['style'].widget.choices = [
                (style.pk, f"{style.name} (Premium)" if style.is_premium else style.name)
                for style in QuestionSetStyle.objects.all()
            ]


class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter your question here'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']