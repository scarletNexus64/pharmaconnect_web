#!/usr/bin/env python
"""
Script pour créer un utilisateur de test avec les données nécessaires
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmaconnect.settings')
django.setup()

from api.models import User, Organization, HealthFacility
from django.contrib.auth.hashers import make_password

def create_test_data():
    """Créer les données de test nécessaires"""
    
    # Créer une organisation
    org, created = Organization.objects.get_or_create(
        code='ORG001',
        defaults={
            'name': 'Organisation Test PharmaConnect',
            'type': 'NGO',
            'country': 'Cameroun'
        }
    )
    print(f"Organisation {'créée' if created else 'existante'}: {org.name}")
    
    # Créer une formation sanitaire
    facility, created = HealthFacility.objects.get_or_create(
        code='CS001',
        defaults={
            'name': 'Centre de Santé Test',
            'type': 'CSI',
            'level_of_care': 'PRIMARY',
            'location': 'Yaoundé, Cameroun'
        }
    )
    print(f"Formation sanitaire {'créée' if created else 'existante'}: {facility.name}")
    
    # Créer ou mettre à jour l'utilisateur de test
    user, created = User.objects.get_or_create(
        username='claudeUserTest',
        defaults={
            'email': 'claude.test@pharmaconnect.org',
            'first_name': 'Claude',
            'last_name': 'Test User',
            'organization': org,
            'health_facility': facility,
            'access_level': 'COORDINATION',
            'phone': '+237 600 000 000',
            'is_active': True
        }
    )
    
    # Définir le mot de passe
    user.set_password('TestPassword123!')
    user.save()
    
    print(f"\nUtilisateur {'créé' if created else 'mis à jour'}: {user.username}")
    print(f"Email: {user.email}")
    print(f"Organisation: {user.organization.name}")
    print(f"Formation sanitaire: {user.health_facility.name}")
    print(f"Niveau d'accès: {user.access_level}")
    print(f"Mot de passe: TestPassword123!")
    
    return user, org, facility

if __name__ == '__main__':
    try:
        user, org, facility = create_test_data()
        print("\n✅ Données de test créées avec succès!")
        print("\n📝 Informations de connexion:")
        print(f"   Username: claudeUserTest")
        print(f"   Password: TestPassword123!")
        print(f"   Organisation: {org.name}")
        print(f"   Access Level: COORDINATION")
    except Exception as e:
        print(f"\n❌ Erreur lors de la création des données: {e}")
        sys.exit(1)