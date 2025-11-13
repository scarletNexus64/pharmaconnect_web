#!/usr/bin/env python
"""
Script pour créer des utilisateurs supplémentaires de test
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmaconnect.settings')
django.setup()

from api.models import User, Organization, HealthFacility
from django.contrib.auth.hashers import make_password

def create_additional_users():
    """Créer des utilisateurs supplémentaires pour tester la gestion des distributeurs"""
    
    # Récupérer l'organisation existante
    try:
        org = Organization.objects.get(code='ORG001')
        print(f"✅ Organisation trouvée: {org.name}")
    except Organization.DoesNotExist:
        print("❌ Organisation ORG001 non trouvée. Veuillez d'abord exécuter create_test_user.py")
        return
    
    # Récupérer la formation sanitaire existante
    try:
        facility = HealthFacility.objects.get(code='CS001')
        print(f"✅ Formation sanitaire trouvée: {facility.name}")
    except HealthFacility.DoesNotExist:
        print("❌ Formation sanitaire CS001 non trouvée. Veuillez d'abord exécuter create_test_user.py")
        return
    
    # Utilisateurs à créer
    users_data = [
        {
            'username': 'marie.dubois',
            'email': 'marie.dubois@pharmaconnect.org',
            'first_name': 'Marie',
            'last_name': 'Dubois',
            'access_level': 'FACILITY',
            'phone': '+237 600 111 111'
        },
        {
            'username': 'jean.martin',
            'email': 'jean.martin@pharmaconnect.org',
            'first_name': 'Jean',
            'last_name': 'Martin',
            'access_level': 'PROJECT',
            'phone': '+237 600 222 222'
        },
        {
            'username': 'sophie.bernard',
            'email': 'sophie.bernard@pharmaconnect.org',
            'first_name': 'Sophie',
            'last_name': 'Bernard',
            'access_level': 'FACILITY',
            'phone': '+237 600 333 333'
        },
        {
            'username': 'paul.garcia',
            'email': 'paul.garcia@pharmaconnect.org',
            'first_name': 'Paul',
            'last_name': 'Garcia',
            'access_level': 'PROJECT',
            'phone': '+237 600 444 444'
        },
        {
            'username': 'anna.lopez',
            'email': 'anna.lopez@pharmaconnect.org',
            'first_name': 'Anna',
            'last_name': 'Lopez',
            'access_level': 'COORDINATION',
            'phone': '+237 600 555 555'
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'organization': org,
                'health_facility': facility if user_data['access_level'] == 'FACILITY' else None,
                'access_level': user_data['access_level'],
                'phone': user_data['phone'],
                'is_active': True
            }
        )
        
        # Définir le mot de passe
        user.set_password('TestPassword123!')
        user.save()
        
        created_users.append(user)
        status = "créé" if created else "existant"
        print(f"✅ Utilisateur {status}: {user.first_name} {user.last_name} ({user.username})")
    
    print(f"\n📊 Total des utilisateurs dans l'organisation {org.name}:")
    all_users = User.objects.filter(organization=org)
    for user in all_users:
        print(f"   - {user.first_name} {user.last_name} ({user.email}) - {user.access_level}")
    
    return created_users

if __name__ == '__main__':
    try:
        users = create_additional_users()
        print(f"\n✅ {len(users)} utilisateurs traités avec succès!")
        print("\n📝 Tous les utilisateurs ont le mot de passe: TestPassword123!")
        print("\n🔧 Vous pouvez maintenant tester la gestion des distributeurs avec plusieurs utilisateurs.")
    except Exception as e:
        print(f"\n❌ Erreur lors de la création des utilisateurs: {e}")
        sys.exit(1)