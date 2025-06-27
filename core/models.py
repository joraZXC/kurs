from django.db import models
from django.contrib.auth.models import User

class Complex(models.Model):
    complex_id = models.AutoField(primary_key=True)
    complex_rigging = models.CharField(max_length=100, null=True, blank=True)
    complex_address = models.CharField(max_length=100)

    class Meta:
        db_table = 'complex'
        verbose_name = 'Комплекс'
        verbose_name_plural = 'Комплексы'
        indexes = [
            models.Index(fields=['complex_id'], name='complex_pk'),
        ]

    def __str__(self):
        return self.complex_address or f"Комплекс {self.complex_id}"

class Organizer(models.Model):
    organizer_id = models.AutoField(primary_key=True)
    organizer_affiliation = models.CharField(max_length=100)
    organizer_fio = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'organizer'
        verbose_name = 'Организатор'
        verbose_name_plural = 'Организаторы'
        indexes = [
            models.Index(fields=['organizer_id'], name='organizer_pk'),
        ]

    def __str__(self):
        return self.organizer_fio or self.organizer_affiliation or "Без названия"

class Contract(models.Model):
    contract_id = models.AutoField(primary_key=True)
    organizer = models.ForeignKey(
        Organizer,
        on_delete=models.RESTRICT,
        null=True,
        blank=True
    )
    contract_conditions = models.CharField(max_length=100)
    contract_cost = models.DecimalField(max_digits=10, decimal_places=2)
    contract_term = models.DateField()

    class Meta:
        db_table = 'contract'
        verbose_name = 'Контракт'
        verbose_name_plural = 'Контракты'
        indexes = [
            models.Index(fields=['contract_id'], name='contract_pk'),
            models.Index(fields=['organizer_id'], name='slave_fk'),
        ]

    def __str__(self):
        return f"Контракт {self.contract_id}"

class Employer(models.Model):
    employer_id = models.AutoField(primary_key=True)
    employer_post = models.CharField(max_length=100)
    employer_fio = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'employer'
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        indexes = [
            models.Index(fields=['employer_id'], name='employer_pk'),
        ]
    def __str__(self):
        return self.employer_fio or self.employer_post or "Без имени"

class Zone(models.Model):
    ZONE_TYPE_CHOICES = (
        ('Выставка', 'Выставка'),
        ('Конференция', 'Конференция'),
        ('Семинар', 'Семинар'),
        ('Мастер-класс', 'Мастер-класс'),
        ('Кабинт управления', 'Кабинет Управление'),
    )

    zone_id = models.AutoField(primary_key=True)
    employer = models.ForeignKey(
        Employer,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name='zones_employer'
    )
    contract = models.ForeignKey(Contract, on_delete=models.RESTRICT, null=True, blank=True)
    complex = models.ForeignKey(Complex, on_delete=models.RESTRICT)
    zone_equipment = models.CharField(max_length=100, null=True, blank=True)
    event = models.ForeignKey('Event', on_delete=models.RESTRICT, null=True, blank=True, related_name='zones')
    zone_square = models.SmallIntegerField(null=True, blank=True)
    zone_type = models.CharField(
        max_length=100,
        choices=ZONE_TYPE_CHOICES,
        default='other',
        verbose_name='Тип зоны'
    )

    class Meta:
        db_table = 'zone'
        verbose_name = 'Зона'
        verbose_name_plural = 'Зоны'
        indexes = [
            models.Index(fields=['zone_id'], name='zone_pk'),
            models.Index(fields=['employer_id'], name='work_fk'),
            models.Index(fields=['contract_id'], name='give_fk'),
            models.Index(fields=['complex_id'], name='consists_fk'),
            models.Index(fields=['event_id'], name='zone_event_fk'),
        ]

    def __str__(self):
        return f"{self.zone_type} ({self.zone_id})"

class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    zone = models.ForeignKey(Zone, on_delete=models.RESTRICT, related_name='events')
    organizer = models.ForeignKey(Organizer, on_delete=models.RESTRICT)
    event_date_time = models.DateField()
    event_format = models.CharField(max_length=100)
    event_exhibits = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True, verbose_name='Описание мероприятия')


    class Meta:
        db_table = 'event'
        db_table = 'event'
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        indexes = [
            models.Index(fields=['event_id'], name='event_pk'),
            models.Index(fields=['organizer_id'], name='plan_fk'),
            models.Index(fields=['zone_id'], name='depends_fk'),
        ]

    def __str__(self):
        return f"{self.event_format} ({self.event_date_time})"

class Man(models.Model):
    man_id = models.AutoField(primary_key=True)
    man_fio = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=20, default='visitor')

    class Meta:
        db_table = 'man'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        indexes = [
            models.Index(fields=['man_id'], name='man_pk'),
        ]

    def __str__(self):
        return self.man_fio or f"Пользователь {self.man_id}"

class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    ticket_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'ticket'
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'
        indexes = [
            models.Index(fields=['ticket_id'], name='ticket_pk'),
            models.Index(fields=['user_id'], name='buy_fk'),
            models.Index(fields=['event_id'], name='based_fk'),  
        ]

    def __str__(self):
        return f"Билет #{self.ticket_id} ({self.event.event_format})"

class Control(models.Model):
    event = models.ForeignKey(Event, on_delete=models.RESTRICT)
    employer = models.ForeignKey(Employer, on_delete=models.RESTRICT)

    class Meta:
        db_table = 'control'
        verbose_name = 'Контроль'
        verbose_name_plural = 'Контроли'
        unique_together = (('event', 'employer'),)
        indexes = [
            models.Index(fields=['event_id', 'employer_id'], name='control_pk'),
        ]

    def __str__(self):
        return f"Контроль: {self.event} - {self.employer}"

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    event = models.ForeignKey('Event', on_delete=models.RESTRICT)
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    review_text = models.TextField()
    rating = models.SmallIntegerField(null=True)
    created_at = models.DateField()

    class Meta:
        db_table = 'review'
        managed = False  # или True, если хотите управлять через миграции

    def __str__(self):
        return f"Отзыв {self.review_id}"