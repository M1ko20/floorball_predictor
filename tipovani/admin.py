# DJANGO_ADMIN
from django.contrib import admin
from .models import UserProfile, Team, Match, MatchTip, TeamRanking, TeamRankingItem

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'points']
    list_filter = ['points']
    search_fields = ['user__username']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'position']
    list_editable = ['position']
    ordering = ['position', 'name']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['home_team', 'opponent', 'datetime', 'location', 'is_finished']
    list_filter = ['is_finished', 'datetime']
    search_fields = ['opponent', 'location']
    ordering = ['-datetime']

@admin.register(MatchTip)
class MatchTipAdmin(admin.ModelAdmin):
    list_display = ['user', 'match', 'home_score_tip', 'away_score_tip', 'points_earned']
    list_filter = ['match', 'points_earned']
    search_fields = ['user__username']

@admin.register(TeamRanking)
class TeamRankingAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_submitted', 'submitted_at']
    list_filter = ['is_submitted']

@admin.register(TeamRankingItem)
class TeamRankingItemAdmin(admin.ModelAdmin):
    list_display = ['ranking', 'team', 'position']
    list_filter = ['team']