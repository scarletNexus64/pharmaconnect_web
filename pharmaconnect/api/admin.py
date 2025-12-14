from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Organization, Donor, HealthFacility, HealthFacilityDistributor, Project, MedicationCategory,
    Medication, StandardList, MedicationSubstitution, StockEntry,
    PrescriptionPhoto, Dispensation, DispensationItem, Inventory,
    InventoryItem, ConsumptionData, StockoutPeriod, Alert
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Administration personnalisée pour les utilisateurs"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'organization', 'access_level', 'is_active']
    list_filter = ['organization', 'access_level', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations PharmaConnect', {
            'fields': ('organization', 'health_facility', 'access_level', 'phone')
        }),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Administration pour les organisations"""
    list_display = ['name', 'code', 'type', 'country', 'created_at']
    list_filter = ['type', 'country', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    """Administration pour les bailleurs"""
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(HealthFacility)
class HealthFacilityAdmin(admin.ModelAdmin):
    """Administration pour les formations sanitaires"""
    list_display = ['name', 'code', 'type', 'level_of_care', 'location', 'has_coordinates', 'created_at']
    list_filter = ['type', 'level_of_care', 'created_at']
    search_fields = ['name', 'code', 'location', 'address']
    ordering = ['name']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'code', 'type', 'level_of_care', 'location', 'address')
        }),
        ('Géolocalisation', {
            'fields': ('latitude', 'longitude', 'coverage_radius_km'),
            'classes': ('collapse',)
        }),
        ('Zone de couverture', {
            'fields': ('coverage_polygon',),
            'classes': ('collapse',)
        }),
    )
    
    def has_coordinates(self, obj):
        return obj.latitude is not None and obj.longitude is not None
    has_coordinates.boolean = True
    has_coordinates.short_description = 'Coordonnées'


@admin.register(HealthFacilityDistributor)
class HealthFacilityDistributorAdmin(admin.ModelAdmin):
    """Administration pour les distributeurs de formations sanitaires"""
    list_display = ['user', 'health_facility', 'is_active', 'assigned_date', 'assigned_by']
    list_filter = ['is_active', 'assigned_date', 'health_facility__type', 'health_facility__level_of_care']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'health_facility__name']
    ordering = ['-assigned_date']
    
    fieldsets = (
        ('Assignation', {
            'fields': ('user', 'health_facility', 'is_active')
        }),
        ('Informations complémentaires', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('assigned_by', 'assigned_date'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('assigned_date',)
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une création
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Administration pour les projets"""
    list_display = ['name', 'code', 'organization', 'donor', 'health_facility', 'start_date', 'end_date']
    list_filter = ['organization', 'donor', 'start_date', 'end_date']
    search_fields = ['name', 'code']
    ordering = ['-start_date']


@admin.register(MedicationCategory)
class MedicationCategoryAdmin(admin.ModelAdmin):
    """Administration pour les catégories de médicaments"""
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    """Administration pour les médicaments"""
    list_display = ['code', 'name', 'dosage', 'form', 'category', 'unit_price', 'is_active']
    list_filter = ['category', 'therapeutic_class', 'is_active', 'created_at']
    search_fields = ['code', 'name', 'dosage', 'therapeutic_class']
    filter_horizontal = ['allowed_facilities']
    ordering = ['code']


@admin.register(StandardList)
class StandardListAdmin(admin.ModelAdmin):
    """Administration pour les listes standard"""
    list_display = ['organization', 'project', 'medication', 'is_included', 'custom_code', 'custom_name']
    list_filter = ['organization', 'project', 'is_included', 'created_at']
    search_fields = ['medication__name', 'medication__code', 'custom_name', 'custom_code']


@admin.register(MedicationSubstitution)
class MedicationSubstitutionAdmin(admin.ModelAdmin):
    """Administration pour les substitutions"""
    list_display = ['original_medication', 'substitute_medication', 'organization', 'created_at']
    list_filter = ['organization', 'created_at']
    search_fields = ['original_medication__name', 'substitute_medication__name']


@admin.register(StockEntry)
class StockEntryAdmin(admin.ModelAdmin):
    """Administration pour les entrées en stock"""
    list_display = ['medication', 'organization', 'project', 'quantity_delivered', 'delivery_date', 'expiry_date', 'reception_percentage']
    list_filter = ['organization', 'project', 'delivery_date', 'expiry_date']
    search_fields = ['medication__name', 'medication__code', 'supplier', 'batch_number']
    ordering = ['-delivery_date']


@admin.register(PrescriptionPhoto)
class PrescriptionPhotoAdmin(admin.ModelAdmin):
    """Administration pour les photos d'ordonnances"""
    list_display = ['id', 'user', 'uploaded_at']
    list_filter = ['uploaded_at', 'user']
    ordering = ['-uploaded_at']


class DispensationItemInline(admin.TabularInline):
    """Inline pour les articles dispensés"""
    model = DispensationItem
    extra = 0


@admin.register(Dispensation)
class DispensationAdmin(admin.ModelAdmin):
    """Administration pour les dispensations"""
    list_display = ['id', 'destination', 'patient_name', 'organization', 'project', 'status', 'dispensation_date']
    list_filter = ['destination', 'status', 'organization', 'project', 'dispensation_date']
    search_fields = ['patient_name', 'prescription_number', 'prescriber_name']
    inlines = [DispensationItemInline]
    ordering = ['-dispensation_date']


class InventoryItemInline(admin.TabularInline):
    """Inline pour les articles d'inventaire"""
    model = InventoryItem
    extra = 0


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    """Administration pour les inventaires"""
    list_display = ['organization', 'project', 'month', 'year', 'inventory_date', 'created_by']
    list_filter = ['organization', 'project', 'month', 'year', 'inventory_date']
    inlines = [InventoryItemInline]
    ordering = ['-inventory_date']


@admin.register(ConsumptionData)
class ConsumptionDataAdmin(admin.ModelAdmin):
    """Administration pour les données de consommation"""
    list_display = ['medication', 'organization', 'project', 'week_number', 'year', 'quantity_consumed', 'is_week_closed']
    list_filter = ['organization', 'project', 'week_number', 'year', 'is_week_closed']
    search_fields = ['medication__name', 'medication__code']
    ordering = ['-year', '-week_number']


@admin.register(StockoutPeriod)
class StockoutPeriodAdmin(admin.ModelAdmin):
    """Administration pour les périodes de rupture"""
    list_display = ['medication', 'organization', 'project', 'start_date', 'end_date', 'days_duration']
    list_filter = ['organization', 'project', 'start_date', 'end_date']
    search_fields = ['medication__name', 'medication__code']
    ordering = ['-start_date']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Administration pour les alertes"""
    list_display = ['title', 'alert_type', 'severity', 'organization', 'is_active', 'created_at']
    list_filter = ['alert_type', 'severity', 'organization', 'is_active', 'created_at']
    search_fields = ['title', 'message']
    ordering = ['-created_at']
    
    actions = ['mark_resolved']
    
    def mark_resolved(self, request, queryset):
        """Action pour marquer les alertes comme résolues"""
        from datetime import datetime
        queryset.update(is_active=False, resolved_at=datetime.now())
        self.message_user(request, f"{queryset.count()} alertes marquées comme résolues.")
    mark_resolved.short_description = "Marquer comme résolues"


# ========================================
# CONFIGURATION ADMIN JAZZMIN PERSONNALISÉE
# ========================================

# Personnalisation du titre de l'admin
admin.site.site_header = "PharmaConnect - Administration"
admin.site.site_title = "PharmaConnect Admin"
admin.site.index_title = "Tableau de bord PharmaConnect"

# Configuration simplifiée pour éviter les problèmes de récursion

# ========================================
# STATISTIQUES PERSONNALISÉES POUR LE TABLEAU DE BORD
# ========================================

from django.contrib.admin import AdminSite
from django.utils.timezone import now, timedelta

class PharmaConnectAdminSite(AdminSite):
    """AdminSite personnalisé avec statistiques en temps réel"""

    def index(self, request, extra_context=None):
        """Vue personnalisée pour le tableau de bord avec statistiques réelles"""
        extra_context = extra_context or {}

        # Calculer les statistiques
        extra_context.update({
            'medication_count': Medication.objects.filter(is_active=True).count(),
            'organization_count': Organization.objects.count(),
            'health_facility_count': HealthFacility.objects.count(),
            'active_project_count': Project.objects.filter(
                start_date__lte=now(),
                end_date__gte=now()
            ).count(),
            'dispensation_count': Dispensation.objects.filter(
                dispensation_date__gte=now() - timedelta(days=30)
            ).count(),
            'inventory_count': Inventory.objects.filter(
                inventory_date__gte=now() - timedelta(days=30)
            ).count(),
            'active_user_count': User.objects.filter(is_active=True).count(),
            'active_alert_count': Alert.objects.filter(is_active=True).count(),
        })

        return super().index(request, extra_context)

# Créer une instance du site admin personnalisé
# pharma_admin_site = PharmaConnectAdminSite(name='pharma_admin')

# Note: Pour utiliser le site personnalisé, décommentez la ligne ci-dessus
# et enregistrez vos modèles avec pharma_admin_site.register() au lieu de admin.site.register()
# Pour le moment, on injecte juste les statistiques via un contexte processor

from django.template import RequestContext

def admin_statistics(request):
    """Context processor pour injecter les statistiques dans le template admin"""
    if not request.path.startswith('/admin'):
        return {}

    return {
        'medication_count': Medication.objects.filter(is_active=True).count(),
        'organization_count': Organization.objects.count(),
        'health_facility_count': HealthFacility.objects.count(),
        'active_project_count': Project.objects.filter(
            start_date__lte=now(),
            end_date__gte=now()
        ).count(),
        'dispensation_count': Dispensation.objects.filter(
            dispensation_date__gte=now() - timedelta(days=30)
        ).count(),
        'inventory_count': Inventory.objects.filter(
            inventory_date__gte=now() - timedelta(days=30)
        ).count(),
        'active_user_count': User.objects.filter(is_active=True).count(),
        'active_alert_count': Alert.objects.filter(is_active=True).count(),
    }
