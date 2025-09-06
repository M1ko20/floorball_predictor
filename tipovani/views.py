# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from .models import UserProfile, Match, MatchTip, Team, TeamRanking, TeamRankingItem
from .forms import (CustomLoginForm, MatchTipForm, TeamRankingForm, 
                   MatchForm, MatchResultForm, TeamCorrectRankingForm)

def custom_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = CustomLoginForm()
    
    return render(request, 'tipovani/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Získat všechny tipy uživatele
    tips = MatchTip.objects.filter(user=request.user).select_related('match')
    
    # Získat pořadí týmů pokud existuje
    try:
        team_ranking = TeamRanking.objects.get(user=request.user)
        ranking_items = TeamRankingItem.objects.filter(ranking=team_ranking).select_related('team').order_by('position')
    except TeamRanking.DoesNotExist:
        team_ranking = None
        ranking_items = []
    
    context = {
        'profile': profile,
        'tips': tips,
        'team_ranking': team_ranking,
        'ranking_items': ranking_items,
    }
    
    return render(request, 'tipovani/dashboard.html', context)

@login_required
def zapasy(request):
    matches = Match.objects.all().order_by('datetime')
    
    # Získat všechny tipy uživatele a vytvořit dictionary {match_id: tip}
    user_tips_list = MatchTip.objects.filter(user=request.user)
    user_tips_dict = {tip.match_id: tip for tip in user_tips_list}
    
    # Přidat tip k každému zápasu
    for match in matches:
        match.user_tip = user_tips_dict.get(match.id)
    
    if request.method == 'POST':
        match_id = request.POST.get('match_id')
        match = get_object_or_404(Match, id=match_id)
        
        if match.is_locked():
            messages.error(request, 'Tip je již uzamčen!')
            return redirect('zapasy')
        
        form = MatchTipForm(request.POST)
        if form.is_valid():
            tip, created = MatchTip.objects.get_or_create(
                user=request.user,
                match=match,
                defaults={
                    'home_score_tip': form.cleaned_data['home_score_tip'],
                    'away_score_tip': form.cleaned_data['away_score_tip']
                }
            )
            
            if not created:
                tip.home_score_tip = form.cleaned_data['home_score_tip']
                tip.away_score_tip = form.cleaned_data['away_score_tip']
                tip.save()
            
            messages.success(request, 'Tip byl uložen!')
            return redirect('zapasy')
    
    context = {
        'matches': matches,
        'tip_form': MatchTipForm(),
        'now': timezone.now(),
    }
    
    return render(request, 'tipovani/zapasy.html', context)

@login_required
def poradi_tymu(request):
    try:
        team_ranking = TeamRanking.objects.get(user=request.user)
        if team_ranking.is_submitted:
            ranking_items = TeamRankingItem.objects.filter(ranking=team_ranking).select_related('team').order_by('position')
            return render(request, 'tipovani/poradi_tymu.html', {
                'submitted': True,
                'ranking_items': ranking_items
            })
    except TeamRanking.DoesNotExist:
        team_ranking = None
    
    if request.method == 'POST':
        form = TeamRankingForm(request.POST)
        if form.is_valid():
            # Zkontrolovat, že každá pozice je použita právě jednou
            positions = []
            teams = Team.objects.all()
            
            for team in teams:
                position = form.cleaned_data[f'team_{team.id}']
                if position in positions:
                    messages.error(request, 'Každá pozice musí být použita právě jednou!')
                    return render(request, 'tipovani/poradi_tymu.html', {'form': form})
                positions.append(position)
            
            # Uložit pořadí
            with transaction.atomic():
                ranking, created = TeamRanking.objects.get_or_create(
                    user=request.user,
                    defaults={'is_submitted': True, 'submitted_at': timezone.now()}
                )
                
                if not created and ranking.is_submitted:
                    messages.error(request, 'Pořadí již bylo odevzdáno!')
                    return redirect('poradi_tymu')
                
                ranking.is_submitted = True
                ranking.submitted_at = timezone.now()
                ranking.save()
                
                # Smazat staré položky a vytvořit nové
                TeamRankingItem.objects.filter(ranking=ranking).delete()
                
                for team in teams:
                    position = form.cleaned_data[f'team_{team.id}']
                    TeamRankingItem.objects.create(
                        ranking=ranking,
                        team=team,
                        position=position
                    )
            
            messages.success(request, 'Pořadí týmů bylo úspěšně odevzdáno!')
            return redirect('poradi_tymu')
    else:
        form = TeamRankingForm()
    
    return render(request, 'tipovani/poradi_tymu.html', {'form': form})

@login_required
def leaderboard(request):
    profiles = UserProfile.objects.select_related('user').order_by('-points')
    return render(request, 'tipovani/leaderboard.html', {'profiles': profiles})

# Admin views
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Nemáte oprávnění pro přístup do admin sekce!')
        return redirect('dashboard')
    
    matches = Match.objects.all().order_by('-datetime')[:10]
    return render(request, 'tipovani/admin/admin_dashboard.html', {'matches': matches})

@login_required
def pridat_zapas(request):
    if not request.user.is_staff:
        messages.error(request, 'Nemáte oprávnění pro přístup do admin sekce!')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zápas byl úspěšně přidán!')
            return redirect('admin_dashboard')
    else:
        form = MatchForm()
    
    return render(request, 'tipovani/admin/pridat_zapas.html', {'form': form})

@login_required
def zadat_vysledek(request, match_id):
    if not request.user.is_staff:
        messages.error(request, 'Nemáte oprávnění pro přístup do admin sekce!')
        return redirect('dashboard')
    
    match = get_object_or_404(Match, id=match_id)
    
    if request.method == 'POST':
        form = MatchResultForm(request.POST, instance=match)
        if form.is_valid():
            match = form.save()
            match.is_finished = True
            match.save()
            
            # Přepočítat body pro všechny tipy
            tips = MatchTip.objects.filter(match=match)
            for tip in tips:
                tip.points_earned = tip.calculate_points()
                tip.save()
                
                # Aktualizovat celkové body uživatele
                profile, created = UserProfile.objects.get_or_create(user=tip.user)
                total_points = sum(t.points_earned for t in MatchTip.objects.filter(user=tip.user))
                profile.points = total_points
                profile.save()
            
            messages.success(request, 'Výsledek byl úspěšně zadán a body přepočítány!')
            return redirect('admin_dashboard')
    else:
        form = MatchResultForm(instance=match)
    
    return render(request, 'tipovani/admin/zadat_vysledek.html', {
        'form': form,
        'match': match
    })

@login_required
def vyhodnotit_poradi(request):
    if not request.user.is_staff:
        messages.error(request, 'Nemáte oprávnění pro přístup do admin sekce!')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TeamCorrectRankingForm(request.POST)
        if form.is_valid():
            # Zkontrolovat unikátnost pozic
            positions = []
            teams = Team.objects.all()
            
            for team in teams:
                position = form.cleaned_data[f'team_{team.id}']
                if position in positions:
                    messages.error(request, 'Každá pozice musí být použita právě jednou!')
                    return render(request, 'tipovani/admin/vyhodnotit_poradi.html', {'form': form})
                positions.append(position)
            
            # Uložit správné pořadí
            with transaction.atomic():
                for team in teams:
                    position = form.cleaned_data[f'team_{team.id}']
                    team.position = position
                    team.save()
                
                # Vyhodnotit všechna odevzdaná pořadí
                submitted_rankings = TeamRanking.objects.filter(is_submitted=True)
                
                for ranking in submitted_rankings:
                    points = 0
                    ranking_items = TeamRankingItem.objects.filter(ranking=ranking)
                    
                    for item in ranking_items:
                        if item.team.position == item.position:
                            points += 3
                    
                    # Přidat body k uživatelovu profilu
                    profile, created = UserProfile.objects.get_or_create(user=ranking.user)
                    profile.points += points
                    profile.save()
            
            messages.success(request, f'Pořadí bylo vyhodnoceno! Bylo uděleno celkem bodů všem uživatelům.')
            return redirect('admin_dashboard')
    else:
        form = TeamCorrectRankingForm()
    
    return render(request, 'tipovani/admin/vyhodnotit_poradi.html', {'form': form})