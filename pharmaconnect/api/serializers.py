from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    User, Organization, Donor, HealthFacility, HealthFacilityDistributor, Project, MedicationCategory,
    Medication, StandardList, MedicationSubstitution, StockEntry,
    PrescriptionPhoto, Dispensation, DispensationItem, Inventory,
    InventoryItem, ConsumptionData, StockoutPeriod, Alert
)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = '__all__'
        read_only_fields = ['created_at']


class HealthFacilitySerializer(serializers.ModelSerializer):
    distributors_count = serializers.SerializerMethodField()
    
    class Meta:
        model = HealthFacility
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_distributors_count(self, obj):
        """Retourne le nombre de distributeurs actifs pour cette formation sanitaire"""
        return obj.distributors.filter(is_active=True).count()


class HealthFacilityDistributorSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    health_facility_name = serializers.CharField(source='health_facility.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    
    class Meta:
        model = HealthFacilityDistributor
        fields = '__all__'
        read_only_fields = ['assigned_date', 'assigned_by']


class ProjectSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    donor_name = serializers.CharField(source='donor.name', read_only=True)
    health_facility_name = serializers.CharField(source='health_facility.name', read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_at']


class UserSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    health_facility_name = serializers.CharField(source='health_facility.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone',
                 'organization', 'organization_name', 'health_facility', 
                 'health_facility_name', 'access_level', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 
                 'last_name', 'phone', 'organization', 'health_facility', 'access_level']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Identifiants invalides')
            if not user.is_active:
                raise serializers.ValidationError('Compte désactivé')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Nom d\'utilisateur et mot de passe requis')


class MedicationCategorySerializer(serializers.ModelSerializer):
    medications_count = serializers.SerializerMethodField()

    class Meta:
        model = MedicationCategory
        fields = '__all__'
        read_only_fields = ['created_at']

    def get_medications_count(self, obj):
        return obj.medications.count()


class MedicationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    allowed_facilities_names = serializers.StringRelatedField(
        source='allowed_facilities', many=True, read_only=True
    )

    class Meta:
        model = Medication
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class MedicationSearchSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour la recherche"""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Medication
        fields = ['id', 'code', 'name', 'dosage', 'form', 'packaging', 
                 'unit_price', 'category_name', 'therapeutic_class']


class StandardListSerializer(serializers.ModelSerializer):
    medication_details = MedicationSerializer(source='medication', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = StandardList
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class MedicationSubstitutionSerializer(serializers.ModelSerializer):
    original_medication_name = serializers.CharField(source='original_medication.name', read_only=True)
    substitute_medication_name = serializers.CharField(source='substitute_medication.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = MedicationSubstitution
        fields = '__all__'
        read_only_fields = ['created_at']


class StockEntrySerializer(serializers.ModelSerializer):
    medication_details = MedicationSerializer(source='medication', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    reception_percentage = serializers.ReadOnlyField()
    expiry_risk_months = serializers.ReadOnlyField()
    is_expiry_risk = serializers.ReadOnlyField()

    class Meta:
        model = StockEntry
        fields = '__all__'
        read_only_fields = ['created_at']
        extra_kwargs = {
            'organization': {'required': False}  # Le backend l'assignera automatiquement
        }


class PrescriptionPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionPhoto
        fields = '__all__'
        read_only_fields = ['uploaded_at', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DispensationItemSerializer(serializers.ModelSerializer):
    medication_details = MedicationSerializer(source='medication', read_only=True)

    class Meta:
        model = DispensationItem
        fields = '__all__'


class DispensationSerializer(serializers.ModelSerializer):
    items = DispensationItemSerializer(many=True, read_only=True)
    prescription_photo_url = serializers.CharField(source='prescription_photo.photo.url', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Dispensation
        fields = '__all__'
        read_only_fields = ['dispensation_date', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class InventoryItemSerializer(serializers.ModelSerializer):
    medication_details = MedicationSerializer(source='medication', read_only=True)
    variance = serializers.ReadOnlyField()
    variance_percentage = serializers.ReadOnlyField()

    class Meta:
        model = InventoryItem
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    items = InventoryItemSerializer(many=True, read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Inventory
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ConsumptionDataSerializer(serializers.ModelSerializer):
    medication_details = MedicationSerializer(source='medication', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = ConsumptionData
        fields = '__all__'
        read_only_fields = ['created_at']


class StockoutPeriodSerializer(serializers.ModelSerializer):
    medication_details = MedicationSerializer(source='medication', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = StockoutPeriod
        fields = '__all__'


class AlertSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    medication_name = serializers.CharField(source='medication.name', read_only=True)

    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ['created_at']


# Serializers pour les statistiques et analyses
class StockSummarySerializer(serializers.Serializer):
    """Serializer pour le résumé des stocks"""
    total_medications = serializers.IntegerField()
    total_stock_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    expired_items = serializers.IntegerField()
    expiry_risk_items = serializers.IntegerField()
    stockout_items = serializers.IntegerField()
    pre_stockout_items = serializers.IntegerField()


class ConsumptionAnalysisSerializer(serializers.Serializer):
    """Serializer pour l'analyse de consommation"""
    medication = MedicationSerializer()
    weekly_average = serializers.DecimalField(max_digits=10, decimal_places=2)
    monthly_average = serializers.DecimalField(max_digits=10, decimal_places=2)
    current_stock = serializers.IntegerField()
    stock_days_remaining = serializers.IntegerField()
    status = serializers.CharField()


class ReceptionReportSerializer(serializers.Serializer):
    """Serializer pour le rapport de réception"""
    total_orders = serializers.IntegerField()
    total_deliveries = serializers.IntegerField()
    average_reception_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    items = StockEntrySerializer(many=True)


class PharmacoepidemioAnalysisSerializer(serializers.Serializer):
    """Serializer pour les analyses pharmacoépidémiologiques"""
    total_prescriptions = serializers.IntegerField()
    antibiotic_prescriptions = serializers.IntegerField()
    antibiotic_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    multitherapy_prescriptions = serializers.IntegerField()
    malaria_prescriptions = serializers.IntegerField()
    malaria_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    pregnant_women_prescriptions = serializers.IntegerField()
    children_under_5_prescriptions = serializers.IntegerField()