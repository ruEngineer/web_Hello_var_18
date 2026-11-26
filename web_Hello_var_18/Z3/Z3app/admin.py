from django.contrib import admin

from .models import Bus, BusPassport, Passenger, Ticket, Trip


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'email', 'birth_date')
    search_fields = ('full_name', 'phone', 'email')


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'plate_number', 'seats')
    search_fields = ('model_name', 'plate_number')


@admin.register(BusPassport)
class BusPassportAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'bus', 'issue_date', 'valid_until', 'registered')
    list_filter = ('registered',)
    search_fields = ('serial_number', 'bus__model_name', 'bus__plate_number')


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        'bus', 'from_city', 'to_city', 'price',
        'departure_date', 'departure_time', 'travel_time',
    )
    list_filter = ('departure_date', 'bus')
    search_fields = ('from_city', 'to_city', 'bus__plate_number')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'passenger', 'trip', 'seat', 'status',
        'baggage', 'total', 'paid_at', 'refunded_at', 'created_at',
    )
    list_filter = ('status', 'baggage')
    search_fields = ('passenger__full_name', 'passenger__phone')
    readonly_fields = ('total', 'paid_at', 'refunded_at', 'refund_amount', 'created_at')
