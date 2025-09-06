# DJANGO_MODELS
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.points} bodů"

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    position = models.IntegerField(null=True, blank=True)  # Pro správné pořadí od admina
    
    def __str__(self):
        return self.name

class TeamRanking(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Pořadí týmů - {self.user.username}"

class TeamRankingItem(models.Model):
    ranking = models.ForeignKey(TeamRanking, on_delete=models.CASCADE, related_name='items')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    position = models.IntegerField()
    
    class Meta:
        unique_together = ['ranking', 'team']
        unique_together = ['ranking', 'position']
    
    def __str__(self):
        return f"{self.ranking.user.username} - {self.team.name} na pozici {self.position}"

class Match(models.Model):
    home_team = models.CharField(max_length=100, default="FBC ČPP Bystroň Group OSTRAVA")
    opponent = models.CharField(max_length=100)
    datetime = models.DateTimeField()
    location = models.CharField(max_length=200)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    is_finished = models.BooleanField(default=False)
    
    def is_locked(self):
        return timezone.now() >= (self.datetime - timedelta(hours=1))
    
    def __str__(self):
        return f"{self.home_team} vs {self.opponent} - {self.datetime.strftime('%d.%m.%Y %H:%M')}"

class MatchTip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_score_tip = models.IntegerField()
    away_score_tip = models.IntegerField()
    points_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'match']
    
    def calculate_points(self):
        if not self.match.is_finished:
            return 0
        
        points = 0
        
        # Správný vítěz
        home_wins_tip = self.home_score_tip > self.away_score_tip
        away_wins_tip = self.home_score_tip < self.away_score_tip
        draw_tip = self.home_score_tip == self.away_score_tip
        
        home_wins_actual = self.match.home_score > self.match.away_score
        away_wins_actual = self.match.home_score < self.match.away_score
        draw_actual = self.match.home_score == self.match.away_score
        
        if (home_wins_tip and home_wins_actual) or (away_wins_tip and away_wins_actual) or (draw_tip and draw_actual):
            points += 2
        
        # Přesný počet gólů domácích
        if self.home_score_tip == self.match.home_score:
            points += 2
        
        # Přesný počet gólů hostů
        if self.away_score_tip == self.match.away_score:
            points += 2
        
        # Bonus za perfektní tip
        if (self.home_score_tip == self.match.home_score and 
            self.away_score_tip == self.match.away_score):
            points += 2  # Celkem 8 bodů (2+2+2+2)
        
        return points
    
    def __str__(self):
        return f"{self.user.username} - {self.match} - {self.home_score_tip}:{self.away_score_tip}"
