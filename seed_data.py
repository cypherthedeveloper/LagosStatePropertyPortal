import os
import django
import random
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# Import models after Django setup
from django.contrib.auth import get_user_model
from properties.models import Property, PropertyImage, PropertyDocument, Amenity, Location
from leads.models import Lead, Message
from favorites.models import Favorite

User = get_user_model()


@transaction.atomic
def create_users():
    """Create sample users with different roles."""
    print("Creating users...")
    
    # Admin user
    admin, created = User.objects.get_or_create(
        email='admin@example.com',
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'role': User.ADMIN,
            'is_staff': True,
            'is_superuser': True,
            'is_verified': True,
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"Created admin user: {admin.email}")
    
    # Government agency user
    govt, created = User.objects.get_or_create(
        email='government@example.com',
        defaults={
            'first_name': 'Government',
            'last_name': 'Agency',
            'role': User.GOVERNMENT,
            'is_verified': True,
        }
    )
    if created:
        govt.set_password('govt123')
        govt.save()
        print(f"Created government user: {govt.email}")
    
    # Real estate firm user
    firm, created = User.objects.get_or_create(
        email='firm@example.com',
        defaults={
            'first_name': 'Real Estate',
            'last_name': 'Firm',
            'role': User.REAL_ESTATE_FIRM,
            'is_verified': True,
            'business_name': 'Lagos Properties Ltd',
            'business_registration_number': 'RC123456',
        }
    )
    if created:
        firm.set_password('firm123')
        firm.save()
        print(f"Created real estate firm user: {firm.email}")
    
    # Property owner user
    owner, created = User.objects.get_or_create(
        email='owner@example.com',
        defaults={
            'first_name': 'Property',
            'last_name': 'Owner',
            'role': User.PROPERTY_OWNER,
            'is_verified': True,
        }
    )
    if created:
        owner.set_password('owner123')
        owner.save()
        print(f"Created property owner user: {owner.email}")
    
    # Buyer/renter user
    buyer, created = User.objects.get_or_create(
        email='buyer@example.com',
        defaults={
            'first_name': 'Buyer',
            'last_name': 'Renter',
            'role': User.BUYER_RENTER,
            'is_verified': True,
        }
    )
    if created:
        buyer.set_password('buyer123')
        buyer.save()
        print(f"Created buyer/renter user: {buyer.email}")
    
    return admin, govt, firm, owner, buyer


@transaction.atomic
def create_amenities():
    """Create sample amenities."""
    print("Creating amenities...")
    
    amenities_data = [
        {'name': 'Swimming Pool', 'icon': 'pool'},
        {'name': 'Gym', 'icon': 'fitness_center'},
        {'name': 'Security', 'icon': 'security'},
        {'name': 'Parking', 'icon': 'local_parking'},
        {'name': 'Air Conditioning', 'icon': 'ac_unit'},
        {'name': 'Furnished', 'icon': 'weekend'},
        {'name': 'Internet', 'icon': 'wifi'},
        {'name': 'Balcony', 'icon': 'balcony'},
        {'name': 'Garden', 'icon': 'grass'},
        {'name': '24/7 Electricity', 'icon': 'power'},
    ]
    
    amenities = []
    for data in amenities_data:
        amenity, created = Amenity.objects.get_or_create(name=data['name'], defaults={'icon': data['icon']})
        amenities.append(amenity)
        if created:
            print(f"Created amenity: {amenity.name}")
    
    return amenities


@transaction.atomic
def create_locations():
    """Create sample locations in Lagos."""
    print("Creating locations...")
    
    locations_data = [
        {'name': 'Lekki', 'latitude': 6.4698, 'longitude': 3.5852},
        {'name': 'Victoria Island', 'latitude': 6.4281, 'longitude': 3.4219},
        {'name': 'Ikoyi', 'latitude': 6.4500, 'longitude': 3.4333},
        {'name': 'Ajah', 'latitude': 6.4698, 'longitude': 3.5852},
        {'name': 'Ikeja', 'latitude': 6.6018, 'longitude': 3.3515},
        {'name': 'Yaba', 'latitude': 6.5144, 'longitude': 3.3792},
        {'name': 'Surulere', 'latitude': 6.5059, 'longitude': 3.3509},
        {'name': 'Gbagada', 'latitude': 6.5555, 'longitude': 3.3887},
    ]
    
    locations = []
    for data in locations_data:
        location, created = Location.objects.get_or_create(
            name=data['name'],
            defaults={
                'city': 'Lagos',
                'state': 'Lagos',
                'country': 'Nigeria',
                'latitude': data['latitude'],
                'longitude': data['longitude'],
            }
        )
        locations.append(location)
        if created:
            print(f"Created location: {location.name}")
    
    return locations


@transaction.atomic
def create_properties(firm, owner, locations, amenities):
    """Create sample properties."""
    print("Creating properties...")
    
    property_types = [Property.APARTMENT, Property.HOUSE, Property.LAND, Property.COMMERCIAL, Property.OFFICE]
    listing_types = [Property.FOR_SALE, Property.FOR_RENT]
    verification_statuses = [Property.PENDING, Property.VERIFIED, Property.REJECTED]
    
    properties = []
    
    # Create properties for the real estate firm
    for i in range(5):
        property_type = random.choice(property_types)
        listing_type = random.choice(listing_types)
        location = random.choice(locations)
        
        property_instance, created = Property.objects.get_or_create(
            title=f"Firm Property {i+1} in {location.name}",
            defaults={
                'description': f"A beautiful {property_type} for {listing_type.replace('_', ' ')} in {location.name}.",
                'price': Decimal(str(random.randint(5000000, 50000000))),
                'property_type': property_type,
                'listing_type': listing_type,
                'location': location,
                'address': f"{random.randint(1, 100)} {location.name} Road, Lagos",
                'bedrooms': random.randint(1, 5) if property_type != Property.LAND else None,
                'bathrooms': random.randint(1, 5) if property_type != Property.LAND else None,
                'size': Decimal(str(random.randint(50, 500))),
                'owner': firm,
                'verification_status': random.choice(verification_statuses),
                'is_featured': random.choice([True, False]),
                'is_active': True,
            }
        )
        
        if created:
            # Add random amenities
            num_amenities = random.randint(2, 6)
            selected_amenities = random.sample(list(amenities), num_amenities)
            property_instance.amenities.set(selected_amenities)
            
            # Set verification details for verified properties
            if property_instance.verification_status == Property.VERIFIED:
                property_instance.verified_at = timezone.now()
                property_instance.save()
            
            properties.append(property_instance)
            print(f"Created property: {property_instance.title}")
    
    # Create properties for the individual property owner
    for i in range(3):
        property_type = random.choice(property_types)
        listing_type = random.choice(listing_types)
        location = random.choice(locations)
        
        property_instance, created = Property.objects.get_or_create(
            title=f"Owner Property {i+1} in {location.name}",
            defaults={
                'description': f"A cozy {property_type} for {listing_type.replace('_', ' ')} in {location.name}.",
                'price': Decimal(str(random.randint(2000000, 30000000))),
                'property_type': property_type,
                'listing_type': listing_type,
                'location': location,
                'address': f"{random.randint(1, 100)} {location.name} Avenue, Lagos",
                'bedrooms': random.randint(1, 4) if property_type != Property.LAND else None,
                'bathrooms': random.randint(1, 3) if property_type != Property.LAND else None,
                'size': Decimal(str(random.randint(50, 300))),
                'owner': owner,
                'verification_status': random.choice(verification_statuses),
                'is_featured': random.choice([True, False]),
                'is_active': True,
            }
        )
        
        if created:
            # Add random amenities
            num_amenities = random.randint(2, 5)
            selected_amenities = random.sample(list(amenities), num_amenities)
            property_instance.amenities.set(selected_amenities)
            
            # Set verification details for verified properties
            if property_instance.verification_status == Property.VERIFIED:
                property_instance.verified_at = timezone.now()
                property_instance.save()
            
            properties.append(property_instance)
            print(f"Created property: {property_instance.title}")
    
    return properties


@transaction.atomic
def create_leads_and_messages(buyer, properties):
    """Create sample leads and messages."""
    print("Creating leads and messages...")
    
    leads = []
    verified_properties = [p for p in properties if p.verification_status == Property.VERIFIED]
    
    for i, property_instance in enumerate(verified_properties[:3]):
        lead, created = Lead.objects.get_or_create(
            user=buyer,
            property=property_instance,
            defaults={
                'status': Lead.NEW,
                'message': f"I am interested in this {property_instance.property_type}. Please contact me for more information.",
            }
        )
        
        if created:
            leads.append(lead)
            print(f"Created lead for property: {property_instance.title}")
            
            # Create initial message from buyer to property owner
            Message.objects.create(
                lead=lead,
                sender=buyer,
                receiver=property_instance.owner,
                content=f"Hello, I'm interested in your property at {property_instance.address}. Is it still available?",
                is_read=False,
            )
            
            # Create reply from property owner
            Message.objects.create(
                lead=lead,
                sender=property_instance.owner,
                receiver=buyer,
                content=f"Yes, it's still available. Would you like to schedule a viewing?",
                is_read=False,
            )
            
            print(f"Created messages for lead on property: {property_instance.title}")
    
    return leads


@transaction.atomic
def create_favorites(buyer, properties):
    """Create sample favorites."""
    print("Creating favorites...")
    
    favorites = []
    verified_properties = [p for p in properties if p.verification_status == Property.VERIFIED]
    
    for property_instance in random.sample(verified_properties, min(3, len(verified_properties))):
        favorite, created = Favorite.objects.get_or_create(
            user=buyer,
            property=property_instance,
        )
        
        if created:
            favorites.append(favorite)
            print(f"Created favorite for property: {property_instance.title}")
    
    return favorites


def run_seed():
    """Run all seed functions."""
    print("Starting seed data creation...")
    
    admin, govt, firm, owner, buyer = create_users()
    amenities = create_amenities()
    locations = create_locations()
    properties = create_properties(firm, owner, locations, amenities)
    leads = create_leads_and_messages(buyer, properties)
    favorites = create_favorites(buyer, properties)
    
    print("\nSeed data creation completed!")
    print(f"Created {User.objects.count()} users")
    print(f"Created {Amenity.objects.count()} amenities")
    print(f"Created {Location.objects.count()} locations")
    print(f"Created {Property.objects.count()} properties")
    print(f"Created {Lead.objects.count()} leads")
    print(f"Created {Message.objects.count()} messages")
    print(f"Created {Favorite.objects.count()} favorites")
    
    print("\nYou can now log in with the following credentials:")
    print("Admin: admin@example.com / admin123")
    print("Government Agency: government@example.com / govt123")
    print("Real Estate Firm: firm@example.com / firm123")
    print("Property Owner: owner@example.com / owner123")
    print("Buyer/Renter: buyer@example.com / buyer123")


if __name__ == "__main__":
    run_seed()