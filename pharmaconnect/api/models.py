from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from datetime import datetime, timedelta


class Organization(models.Model):
    """Modèle pour les organisations (ONG, programmes étatiques)"""
    
    class Meta:
        verbose_name = "Organisation"
        verbose_name_plural = "Organisations"
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=50, choices=[
        ('NGO', 'ONG'),
        ('GOVERNMENT', 'Programme étatique'),
        ('INTERNATIONAL', 'Organisation internationale')
    ])
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Donor(models.Model):
    """Modèle pour les bailleurs de fonds"""
    
    class Meta:
        verbose_name = "Bailleur de fonds"
        verbose_name_plural = "Bailleurs de fonds"
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class HealthFacility(models.Model):
    """Modèle pour les formations sanitaires"""
    
    class Meta:
        verbose_name = "Formation sanitaire"
        verbose_name_plural = "Formations sanitaires"
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=50, choices=[
        ('CSI', 'Centre de Santé Intégré'),
        ('CS', 'Centre de Santé'),
        ('HOSPITAL', 'Hôpital'),
        ('MOBILE_CLINIC', 'Clinique mobile'),
        ('ASC', 'Agent de Santé Communautaire')
    ])
    level_of_care = models.CharField(max_length=50, choices=[
        ('PRIMARY', 'Soins de santé primaire'),
        ('SECONDARY', 'Soins de santé secondaire'),
        ('HIV', 'Programme VIH'),
        ('MALARIA', 'Programme Paludisme'),
        ('TB', 'Programme Tuberculose'),
        ('NUTRITION', 'Programme Nutrition'),
        ('LABORATORY', 'Programme Laboratoire')
    ])
    location = models.CharField(max_length=255)
    
    # Géolocalisation et zones de couverture
    address = models.TextField(blank=True, help_text="Adresse complète de la formation sanitaire")
    latitude = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True,
        help_text="Latitude de la formation sanitaire"
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True,
        help_text="Longitude de la formation sanitaire"
    )
    coverage_polygon = models.JSONField(
        null=True, blank=True,
        help_text="Coordonnées du polygone définissant la zone de couverture (format GeoJSON)"
    )
    coverage_radius_km = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        help_text="Rayon de couverture en kilomètres (alternatif au polygone)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class HealthFacilityDistributor(models.Model):
    """Modèle pour gérer les distributeurs assignés aux formations sanitaires"""
    
    class Meta:
        verbose_name = "Distributeur de formation sanitaire"
        verbose_name_plural = "Distributeurs de formations sanitaires"
        unique_together = ['user', 'health_facility']  # Un utilisateur ne peut être qu'une fois par formation
    
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='health_facility_assignments')
    health_facility = models.ForeignKey(HealthFacility, on_delete=models.CASCADE, related_name='distributors')
    assigned_date = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='distributor_assignments_made',
        help_text="Utilisateur qui a effectué l'assignation"
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text="Notes sur l'assignation du distributeur")
    
    def __str__(self):
        status = "Actif" if self.is_active else "Inactif"
        return f"{self.user.get_full_name()} - {self.health_facility.name} ({status})"


class Project(models.Model):
    """Modèle pour les projets"""
    
    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='projects')
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='projects')
    health_facility = models.ForeignKey(HealthFacility, on_delete=models.CASCADE, related_name='projects')
    start_date = models.DateField()
    end_date = models.DateField()
    order_frequency_months = models.IntegerField(default=3)  # Périodicité des commandes
    delivery_delay_months = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)  # Délai de livraison
    buffer_stock_months = models.DecimalField(max_digits=4, decimal_places=2, default=0.5)  # Stock tampon
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.organization.name}/{self.donor.code}"


class User(AbstractUser):
    """Utilisateur étendu"""
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    health_facility = models.ForeignKey(HealthFacility, on_delete=models.CASCADE, null=True, blank=True)
    access_level = models.CharField(max_length=20, choices=[
        ('COORDINATION', 'Coordination'),
        ('PROJECT', 'Projet'),
        ('FACILITY', 'Formation sanitaire')
    ])
    phone = models.CharField(max_length=20, blank=True)


class MedicationCategory(models.Model):
    """Catégories de médicaments"""
    
    class Meta:
        verbose_name = "Catégorie de médicaments"
        verbose_name_plural = "Catégories de médicaments"
        unique_together = ['organization', 'code']  # Code unique par organisation
    
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='medication_categories', null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Medication(models.Model):
    """Modèle pour les médicaments conforme au cahier des charges"""
    
    class Meta:
        verbose_name = "Médicament"
        verbose_name_plural = "Médicaments"
        unique_together = ['organization', 'code']  # Code unique par organisation
    
    # Champs principaux selon cahier des charges
    code = models.CharField(max_length=20)  # Ex: MA0103
    name = models.CharField(max_length=255)  # Libellé du médicament
    designation = models.CharField(max_length=500, blank=True)  # Désignation complète (nom + dosage + forme)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='medications', null=True, blank=True)
    
    # Présentation et conditionnement
    dosage = models.CharField(max_length=100, blank=True)  # Ex: 500mg
    form = models.CharField(max_length=100)  # Forme galénique (Comprimé, Sirop, Injectable, etc.)
    packaging = models.CharField(max_length=100)  # Conditionnement (Boîte de 20 comprimés, Flacon de 100ml, etc.)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # PU - Prix unitaire
    
    # Classification
    category = models.ForeignKey(MedicationCategory, on_delete=models.CASCADE, related_name='medications')
    therapeutic_class = models.CharField(max_length=100, blank=True)  # Classe thérapeutique
    pharmacotherapeutic = models.CharField(max_length=200, blank=True)  # Action pharmacothérapeutique
    
    # Posologie et administration
    administration_route = models.CharField(max_length=50, blank=True, choices=[
        ('ORAL', 'Voie orale'),
        ('IV', 'Intraveineuse'),
        ('IM', 'Intramusculaire'),
        ('SC', 'Sous-cutanée'),
        ('TOPIQUE', 'Application locale'),
        ('INHALATION', 'Inhalation'),
        ('RECTALE', 'Voie rectale'),
        ('VAGINALE', 'Voie vaginale'),
        ('OCULAIRE', 'Voie oculaire'),
        ('NASALE', 'Voie nasale'),
        ('AUTRE', 'Autre')
    ])
    posology = models.TextField(blank=True)  # Posologie détaillée
    posology_unit = models.CharField(max_length=100, blank=True)  # Unité posologique (cp/jour, ml/kg, etc.)
    dosage_instructions = models.TextField(blank=True)  # Instructions de dosage
    
    # Indications et pathologies
    pathology = models.CharField(max_length=200, blank=True)  # Pathologie principale
    indications = models.TextField(blank=True)  # Indications thérapeutiques
    
    # Niveaux de soins et structures autorisées
    care_level = models.CharField(max_length=50, blank=True, choices=[
        ('SSP', 'Soins de santé primaire'),
        ('SSS', 'Soins de santé secondaire'),
        ('TERTIAIRE', 'Soins tertiaires'),
        ('TOUS', 'Tous niveaux')
    ])
    structure_types = models.CharField(max_length=200, blank=True)  # CSI, CS, Hôpital, Clinique mobile, ASC (séparés par virgules)
    allowed_facilities = models.ManyToManyField(HealthFacility, blank=True)
    
    # Protocole et justification
    protocol = models.TextField(blank=True)  # Protocole de traitement
    protocol_justification = models.TextField(blank=True)  # Justification du protocole
    
    # Contre-indications et précautions
    contraindications = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)  # Effets secondaires
    interactions = models.TextField(blank=True)  # Interactions médicamenteuses
    precautions = models.TextField(blank=True)  # Précautions d'emploi
    storage_conditions = models.CharField(max_length=200, blank=True)  # Conditions de conservation
    
    # Codes et tracking
    barcode_gs1 = models.CharField(max_length=50, blank=True)
    
    # Statut
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class StandardList(models.Model):
    """Liste standard générée automatiquement"""
    
    class Meta:
        verbose_name = "Liste standard"
        verbose_name_plural = "Listes standard"
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    is_included = models.BooleanField(default=True)
    custom_code = models.CharField(max_length=20, blank=True)  # Code personnalisé par l'ONG
    custom_name = models.CharField(max_length=255, blank=True)  # Nom personnalisé par l'ONG
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['organization', 'project', 'medication']

    def __str__(self):
        return f"{self.organization.name} - {self.medication.name}"


class MedicationSubstitution(models.Model):
    """Substitutions de médicaments"""
    
    class Meta:
        verbose_name = "Substitution de médicament"
        verbose_name_plural = "Substitutions de médicaments"
    original_medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='substitutions')
    substitute_medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='substitute_for')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['original_medication', 'substitute_medication', 'organization']


class StockEntry(models.Model):
    """Entrées en stock"""
    
    class Meta:
        verbose_name = "Entrée en stock"
        verbose_name_plural = "Entrées en stock"
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    delivery_date = models.DateField()
    quantity_ordered = models.PositiveIntegerField(default=0)
    quantity_delivered = models.PositiveIntegerField()
    expiry_date = models.DateField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.CharField(max_length=255, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def reception_percentage(self):
        if self.quantity_ordered > 0:
            return (self.quantity_delivered / self.quantity_ordered) * 100
        return 0

    @property
    def expiry_risk_months(self):
        """Calcule le risque de péremption en mois"""
        today = datetime.now().date()
        if self.expiry_date <= today:
            return 0
        diff = self.expiry_date - today
        return diff.days / 30.44  # Nombre moyen de jours par mois

    @property
    def is_expiry_risk(self):
        """Retourne True si le produit expire dans moins de 2 mois"""
        return self.expiry_risk_months < 2

    def __str__(self):
        return f"{self.medication.name} - {self.quantity_delivered} - {self.delivery_date}"


class PrescriptionPhoto(models.Model):
    """Photos d'ordonnances"""
    
    class Meta:
        verbose_name = "Photo d'ordonnance"
        verbose_name_plural = "Photos d'ordonnances"
    photo = models.ImageField(upload_to='prescriptions/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Prescription {self.id} - {self.uploaded_at}"


class Dispensation(models.Model):
    """Dispensation de médicaments"""
    
    class Meta:
        verbose_name = "Dispensation"
        verbose_name_plural = "Dispensations"
    DESTINATION_CHOICES = [
        ('PATIENT', 'Patient'),
        ('SERVICE', 'Service hôpital'),
        ('EXPIRED', 'Périmés/détériorés'),
        ('RETURN', 'Retour pharmacie')
    ]
    
    STATUS_CHOICES = [
        ('DELIVERED', 'Délivrée'),
        ('PENDING', 'En attente'),
        ('PARTIAL', 'Livraison partielle')
    ]

    # Informations générales
    prescription_photo = models.ForeignKey(PrescriptionPhoto, on_delete=models.CASCADE)
    destination = models.CharField(max_length=20, choices=DESTINATION_CHOICES)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    dispensation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Informations patient (si destination = PATIENT)
    patient_name = models.CharField(max_length=255, blank=True)
    patient_age = models.PositiveIntegerField(null=True, blank=True)
    patient_sex = models.CharField(max_length=10, choices=[('M', 'Masculin'), ('F', 'Féminin')], blank=True)
    prescription_number = models.CharField(max_length=100, blank=True)
    prescriber_name = models.CharField(max_length=255, blank=True)
    patient_phone = models.CharField(max_length=20, blank=True)
    patient_service = models.CharField(max_length=100, blank=True)
    
    # Informations service (si destination = SERVICE)
    service_name = models.CharField(max_length=255, blank=True)
    
    # Patient unique pour programmes chroniques
    patient_unique_id = models.CharField(max_length=100, blank=True)
    care_type = models.CharField(max_length=50, choices=[
        ('CURATIVE', 'Curative'),
        ('PREVENTIVE', 'Préventive'),
        ('FOLLOW_UP', 'Suivi')
    ], blank=True)
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        if self.destination == 'PATIENT':
            return f"Dispensation {self.id} - {self.patient_name}"
        return f"Dispensation {self.id} - {self.destination}"


class DispensationItem(models.Model):
    """Articles dispensés"""
    
    class Meta:
        verbose_name = "Article dispensé"
        verbose_name_plural = "Articles dispensés"
    dispensation = models.ForeignKey(Dispensation, on_delete=models.CASCADE, related_name='items')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    stock_entry = models.ForeignKey(StockEntry, on_delete=models.CASCADE)
    quantity_dispensed = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.medication.name} - {self.quantity_dispensed}"


class Inventory(models.Model):
    """Inventaires mensuels"""
    
    class Meta:
        verbose_name = "Inventaire"
        verbose_name_plural = "Inventaires"
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    inventory_date = models.DateField()
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['organization', 'project', 'month', 'year']

    def __str__(self):
        return f"Inventaire {self.month}/{self.year} - {self.organization.name}"


class InventoryItem(models.Model):
    """Articles d'inventaire"""
    
    class Meta:
        verbose_name = "Article d'inventaire"
        verbose_name_plural = "Articles d'inventaire"
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='items')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    stock_entry = models.ForeignKey(StockEntry, on_delete=models.CASCADE, null=True, blank=True)
    theoretical_stock = models.PositiveIntegerField()  # Stock théorique
    physical_stock = models.PositiveIntegerField()     # Stock physique compté
    expiry_date = models.DateField(null=True, blank=True)

    @property
    def variance(self):
        """Écart = Stock théorique - Stock physique"""
        return self.theoretical_stock - self.physical_stock

    @property
    def variance_percentage(self):
        """Pourcentage d'écart"""
        if self.physical_stock > 0:
            return (self.variance / self.physical_stock) * 100
        return 0

    def __str__(self):
        return f"{self.medication.name} - Inventaire {self.inventory.month}/{self.inventory.year}"


class ConsumptionData(models.Model):
    """Données de consommation pour calculs CMM"""
    
    class Meta:
        verbose_name = "Données de consommation"
        verbose_name_plural = "Données de consommation"
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    week_number = models.PositiveIntegerField()  # Semaine épidémiologique S1-S52
    year = models.PositiveIntegerField()
    quantity_consumed = models.PositiveIntegerField()
    is_week_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['organization', 'project', 'medication', 'week_number', 'year']

    def __str__(self):
        return f"{self.medication.name} - S{self.week_number}/{self.year}"


class StockoutPeriod(models.Model):
    """Périodes de rupture"""
    
    class Meta:
        verbose_name = "Période de rupture"
        verbose_name_plural = "Périodes de rupture"
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    days_duration = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.end_date and self.start_date:
            self.days_duration = (self.end_date - self.start_date).days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Rupture {self.medication.name} - {self.start_date}"


class Alert(models.Model):
    """Système d'alertes"""
    
    class Meta:
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"
    ALERT_TYPES = [
        ('EXPIRY_RISK', 'Risque de péremption'),
        ('STOCKOUT', 'Rupture'),
        ('PRE_STOCKOUT', 'Pré-rupture'),
        ('OVERSTOCK', 'Surstock'),
        ('ANTIBIOTIC_OVERUSE', 'Surutilisation antibiotiques'),
        ('MALARIA_EPIDEMIC', 'Alerte épidémique paludisme'),
        ('SERVICE_OVERCONSUMPTION', 'Surconsommation service'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyenne'),
        ('HIGH', 'Élevée'),
        ('CRITICAL', 'Critique')
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, null=True, blank=True)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.severity}"
