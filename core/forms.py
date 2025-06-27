from django import forms
from django.db.models import Count
from .models import Zone, Event, Ticket, Review, Employer, Organizer
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ZoneForm(forms.ModelForm):
    create_contract = forms.BooleanField(label="Создать контракт", required=False)
    contract_conditions = forms.CharField(
        label="Условия контракта",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    contract_cost = forms.DecimalField(
        label="Стоимость контракта",
        required=False,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    contract_term = forms.DateField(
        label="Срок действия контракта",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    create_organizer = forms.BooleanField(label="Создать нового организатора", required=False)
    organizer_affiliation = forms.CharField(
        label="Название организации",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    organizer_fio = forms.CharField(
        label="ФИО организатора",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    create_event = forms.BooleanField(label="Создать мероприятие", required=False)
    event_format = forms.CharField(
        label="Формат мероприятия",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    event_date_time = forms.DateField(
        label="Дата мероприятия",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    event_exhibits = forms.CharField(
        label="Экспонаты (необязательно)",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Zone
        fields = ['contract', 'complex', 'zone_equipment', 'zone_square', 'zone_type']
        labels = {
            'contract': 'Контракт',
            'complex': 'Комплекс',
            'zone_equipment': 'Оборудование зоны',
            'zone_square': 'Площадь зоны',
            'zone_type': 'Тип зоны',
        }
        widgets = {
            'zone_equipment': forms.TextInput(attrs={'class': 'form-control'}),
            'zone_square': forms.NumberInput(attrs={'class': 'form-control'}),
            'zone_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['zone_type'].choices = [
            ('Выставка', 'Выставка'),
            ('Конференция', 'Конференция'),
            ('Семинар', 'Семинар'),
            ('Мастер-класс', 'Мастер-класс'),
            ('Кабинет управления', 'Кабинет Управление'),
        ]
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['event_date_time', 'event_format', 'event_exhibits', 'organizer', 'zone']
        labels = {
            'event_date_time': 'Дата мероприятия',
            'event_format': 'Формат мероприятия',
            'event_exhibits': 'Экспонаты (необязательно)',
            'organizer': 'Организатор',
            'zone': 'Зона',
        }
        widgets = {
            'event_date_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'event_format': forms.TextInput(attrs={'class': 'form-control'}),
            'event_exhibits': forms.TextInput(attrs={'class': 'form-control'}),
            'organizer': forms.Select(attrs={'class': 'form-control'}),
            'zone': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['zone'].queryset = Zone.objects.all()
        self.fields['organizer'].queryset = Organizer.objects.all()
        
class TicketForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        disabled=True,
        label="Пользователь"
    )
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(),
        label="Мероприятие"
    )

    class Meta:
        model = Ticket
        fields = ['user', 'event', 'ticket_cost']
        labels = {
            'ticket_cost': 'Стоимость билета',
        }
        widgets = {
            'ticket_cost': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['user'].initial = user
            self.fields['user'].queryset = User.objects.filter(id=user.id)

    def clean(self):
        cleaned_data = super().clean()
        event = cleaned_data.get('event')

        if not event:
            raise forms.ValidationError("Выберите мероприятие.")

        return cleaned_data

class ReviewForm(forms.ModelForm):
    event = forms.ModelChoiceField(queryset=Event.objects.all(), label="Мероприятие")
    created_at = forms.DateField(
        label="Дата отзыва",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = Review
        fields = ['event', 'review_text', 'rating', 'created_at']
        labels = {
            'review_text': 'Текст отзыва',
            'rating': 'Оценка (1-5)',
        }
        widgets = {
            'review_text': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5})
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not (1 <= rating <= 5):
            raise forms.ValidationError("Оценка должна быть от 1 до 5.")
        return rating
class StaffManagementForm(forms.Form):
    zone = forms.ModelChoiceField(queryset=Zone.objects.all(), label="Выберите зону")
    employer = forms.ModelChoiceField(
        queryset=Employer.objects.annotate(zone_count=Count('zones_employer')).filter(zone_count=0),
        label="Выберите сотрудника"
    )
class OrganizerRegistrationForm(UserCreationForm):
    affiliation = forms.CharField(max_length=100, label='Организация')
    fio = forms.CharField(max_length=100, label='ФИО')

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Organizer.objects.create(
                user=user,
                organizer_affiliation=self.cleaned_data['affiliation'],
                organizer_fio=self.cleaned_data['fio']
            )
        return user