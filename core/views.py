
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import ZoneForm, EventForm, TicketForm, ReviewForm, StaffManagementForm
from .models import Zone, Event, Ticket, Review, Organizer
from django.http import HttpResponseForbidden
from django.contrib import messages
from .decorators import admin_required
from .forms import OrganizerRegistrationForm
from django.db.models import Sum
from django.db.models import Count
from django.db import transaction
from .utils import generate_ticket_number, get_ticket_type, calculate_ticket_cost

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'user')
        
        if form_type == 'organizer':
            form = OrganizerRegistrationForm(request.POST)
        else:
            form = UserCreationForm(request.POST)
            
        if form.is_valid():
            form.save()
            messages.success(request, "Регистрация успешна! Теперь вы можете войти.")
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {
        'form': form,
        'organizer_form': OrganizerRegistrationForm()
    })

@login_required
@admin_required
def zone_list(request):
    zones = Zone.objects.all()
    return render(request, 'zones/list.html', {'zones': zones})

@admin_required
def zone_detail(request, pk):
    zone = Zone.objects.get(pk=pk)
    return render(request, 'zones/detail.html', {'zone': zone})
from django.db import transaction
from django.shortcuts import render, redirect
from .models import Zone, Contract, Organizer
from .forms import ZoneForm
from django.contrib import messages

@admin_required
@admin_required
def zone_create(request):
    if request.method == 'POST':
        form = ZoneForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Сохраняем зону
                    zone = form.save()

                    # Создаем контракт, если нужно
                    create_contract = form.cleaned_data.get('create_contract')
                    contract_conditions = form.cleaned_data.get('contract_conditions')
                    contract_cost = form.cleaned_data.get('contract_cost')
                    contract_term = form.cleaned_data.get('contract_term')

                    if create_contract and contract_conditions and contract_cost and contract_term:
                        contract = Contract.objects.create(
                            contract_conditions=contract_conditions,
                            contract_cost=contract_cost,
                            contract_term=contract_term
                        )
                        zone.contract = contract
                        zone.save()

                    # Создаем организатора, если нужно
                    create_organizer = form.cleaned_data.get('create_organizer')
                    organizer_affiliation = form.cleaned_data.get('organizer_affiliation')
                    organizer_fio = form.cleaned_data.get('organizer_fio')

                    if create_organizer and organizer_affiliation:
                        organizer = Organizer.objects.create(
                            organizer_affiliation=organizer_affiliation,
                            organizer_fio=organizer_fio
                        )
                        if create_contract:
                            contract.organizer = organizer
                            contract.save()

                    # Создаем мероприятие, если нужно
                    create_event = form.cleaned_data.get('create_event')
                    event_format = form.cleaned_data.get('event_format')
                    event_date_time = form.cleaned_data.get('event_date_time')
                    event_exhibits = form.cleaned_data.get('event_exhibits')

                    if create_event and event_format and event_date_time:
                        # Проверим, есть ли организатор у зоны или контракта
                        organizer = zone.contract.organizer if zone.contract else None
                        if not organizer:
                            raise forms.ValidationError("Для мероприятия нужен организатор.")

                        Event.objects.create(
                            zone=zone,
                            organizer=organizer,
                            event_date_time=event_date_time,
                            event_format=event_format,
                            event_exhibits=event_exhibits
                        )

                    messages.success(request, "Зона и, при необходимости, мероприятие созданы.")
                    return redirect('zone_list')
            except Exception as e:
                messages.error(request, f"Ошибка при сохранении: {e}")
        else:
            messages.error(request, "Форма заполнена некорректно.")
    else:
        form = ZoneForm()

    return render(request, 'zones/create.html', {'form': form})
def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/list.html', {'events': events})

@login_required
def event_create(request):
   
    is_organizer = hasattr(request.user, 'organizer_profile')
    if not request.user.is_staff and not is_organizer:
        messages.error(request, "У вас нет прав для создания мероприятий.")
        return redirect('event_list')

    if request.method == 'POST':
        form = EventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            if not request.user.is_staff and is_organizer:
                event.organizer = request.user.organizer_profile
            event.save()
            messages.success(request, "Мероприятие успешно создано!")
            return redirect('event_list')
    else:
        form = EventForm(user=request.user)

    return render(request, 'events/create.html', {
        'form': form,
        'is_organizer': is_organizer
    })

@admin_required
def event_edit(request, pk):
    event = Event.objects.get(pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Мероприятие обновлено.")
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'events/edit.html', {'form': form, 'event': event})

@login_required
def ticket_purchase(request):
    if request.user.is_staff:
        messages.error(request, "Администраторы не могут покупать билеты.")
        return redirect('event_list')

    if request.method == 'POST':
        form = TicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, "Билет успешно приобретён!")
            return redirect('event_list')
    else:
        form = TicketForm(user=request.user)

    return render(request, 'tickets/purchase.html', {'form': form})


def review_list(request):
    reviews = Review.objects.raw('SELECT * FROM review')
    return render(request, 'reviews/list.html', {'reviews': reviews})

@login_required
def review_create(request):
    if request.user.is_authenticated and request.user.is_staff:
        messages.error(request, "Администраторы не могут оставлять отзывы как обычные пользователи.")
        return redirect('home')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                review = form.save(commit=False)
                review.user = request.user  # Присваиваем текущего пользователя
                review.save()
                messages.success(request, "Отзыв успешно создан.")
                return redirect('review_list')
            except Exception as e:
                messages.error(request, f"Произошла ошибка при сохранении: {e}")
        else:
            messages.error(request, "Форма заполнена некорректно.")
    else:
        form = ReviewForm()

    return render(request, 'reviews/create.html', {'form': form})
@admin_required
def analytics_dashboard(request):
    event_count = Event.objects.count()
    total_revenue = Ticket.objects.aggregate(total=Sum('ticket_cost'))['total'] or 0
    return render(request, 'analytics/dashboard.html', {
        'event_count': event_count,
        'total_revenue': total_revenue
    })

@login_required
def profile(request):
    if request.user.is_staff:
        messages.error(request, "Администраторы не могут просматривать личный кабинет пользователя.")
        return redirect('analytics_dashboard')
    tickets = Ticket.objects.filter(user=request.user)
    has_tickets = tickets.exists()
    return render(request, 'profile.html', {'user': request.user, 'tickets': tickets, 'has_tickets': has_tickets})

@admin_required
def staff_management(request):
    if request.method == 'POST':
        form = StaffManagementForm(request.POST)
        if form.is_valid():
            zone = form.cleaned_data['zone']
            employer = form.cleaned_data['employer']
            zone.employer = employer
            zone.save()
            messages.success(request, f"{employer.employer_fio} назначен на зону {zone.zone_type}")
            return redirect('staff_management')
    else:
        form = StaffManagementForm()
    zones = Zone.objects.all()
    return render(request, 'zones/staff_management.html', {
        'form': form,
        'zones': zones
    })
def event_detail(request, event_id):
    event = Event.objects.get(event_id=event_id)
    return render(request, 'events/detail.html', {'event': event})

@admin_required
def remove_employer_from_zone(request, zone_id):
    zone = Zone.objects.get(zone_id=zone_id)
    zone.employer = None
    zone.save()
    messages.success(request, "Сотрудник удален с зоны")
    return redirect('staff_management')
@admin_required
def admin_event_create(request):
    if request.method == 'POST':
        event_format = request.POST.get('event_format')
        event_date_time = request.POST.get('event_date_time')
        event_exhibits = request.POST.get('event_exhibits')
        organizer_id = request.POST.get('organizer_id')
        zone_id = request.POST.get('zone_id')

        try:
            with transaction.atomic():
                event = Event.objects.create(
                    event_format=event_format,
                    event_date_time=event_date_time,
                    event_exhibits=event_exhibits,
                    organizer_id=organizer_id,
                    zone_id=zone_id
                )
                messages.success(request, "Мероприятие успешно создано")
                return redirect('event_list')
        except Exception as e:
            messages.error(request, f"Ошибка: {e}")

    organizers = Organizer.objects.all()
    zones = Zone.objects.all()

    return render(request, 'admin/event_create.html', {
        'zones': zones,
        'organizers': organizers
    })


