# DJANGO_FORMS
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Match, MatchTip, Team, TeamRankingItem

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Uživatelské jméno'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Heslo'
        })
    )

class MatchTipForm(forms.ModelForm):
    class Meta:
        model = MatchTip
        fields = ['home_score_tip', 'away_score_tip', 'question_answer']
        widgets = {
            'home_score_tip': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 80px; display: inline-block;'}),
            'away_score_tip': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 80px; display: inline-block;'}),
            'question_answer': forms.Select(choices=[(True, 'Ano'), (False, 'Ne')], attrs={'class': 'form-control', 'style': 'width: 120px; display: inline-block;'})
        }



class TeamRankingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        teams = Team.objects.all().order_by('name')
        
        for i, team in enumerate(teams, 1):
            self.fields[f'team_{team.id}'] = forms.IntegerField(
                label=team.name,
                min_value=1,
                max_value=14,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control',
                    'style': 'width: 80px;'
                })
            )

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['opponent', 'datetime', 'location', 'question']
        widgets = {
            'opponent': forms.TextInput(attrs={'class': 'form-control'}),
            'datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'question': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MatchResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['home_score', 'away_score', 'correct_answer']
        widgets = {
            'home_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'away_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'correct_answer': forms.Select(choices=[(True, 'Ano'), (False, 'Ne')], attrs={'class': 'form-control'}),
        }

class TeamCorrectRankingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        teams = Team.objects.all().order_by('name')
        
        for team in teams:
            self.fields[f'team_{team.id}'] = forms.IntegerField(
                label=team.name,
                min_value=1,
                max_value=14,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control',
                    'style': 'width: 80px;'
                })
            )