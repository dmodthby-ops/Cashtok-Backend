import asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import *
from datetime import datetime

async def seed_testimonials(db: AsyncIOMotorDatabase):
    """Seed database with testimonials"""
    
    # Check if testimonials already exist
    existing_count = await db.testimonials.count_documents({})
    if existing_count > 0:
        print(f"Testimonials already seeded ({existing_count} testimonials)")
        return

    testimonials_data = [
        {
            "id": "1",
            "name": "Sophie Martinez",
            "image": "https://images.unsplash.com/photo-1657128344786-360c3f8e57e5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzh8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU2OTg1NTY3fDA&ixlib=rb-4.1.0&q=85",
            "text": "Grâce à CASHTOK, je génère maintenant 3 200€/mois avec mes vidéos TikTok. Les méthodes enseignées sont incroyables !",
            "platform": "TikTok",
            "revenue": "3 200€/mois",
            "rating": 5,
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "id": "2",
            "name": "Marc Dubois",
            "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzh8MHwxfHNlYXJjaHwyfHxwcm9mZXNzaW9uYWwlMjBoZWFkc2hvdHN8ZW58MHx8fHwxNzU2OTg1NTY3fDA&ixlib=rb-4.1.0&q=85",
            "text": "En 4 mois, mes revenus Instagram ont explosé ! De 0€ à 2 800€/mois. Le coaching personnalisé fait toute la différence.",
            "platform": "Instagram",
            "revenue": "2 800€/mois",
            "rating": 5,
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        # Add more testimonials data here... (truncated for brevity)
    ]
    
    # Insert all testimonials
    result = await db.testimonials.insert_many(testimonials_data)
    print(f"Seeded {len(result.inserted_ids)} testimonials")

async def seed_faqs(db: AsyncIOMotorDatabase):
    """Seed database with FAQs"""
    
    # Check if FAQs already exist
    existing_count = await db.faqs.count_documents({})
    if existing_count > 0:
        print(f"FAQs already seeded ({existing_count} FAQs)")
        return

    faqs_data = [
        {
            "id": "1",
            "question": "Cette formation est-elle adaptée aux débutants complets ?",
            "answer": "Absolument ! CASHTOK System est conçu pour tous les niveaux. Nos modules commencent par les bases et progressent étape par étape. Plus de 70% de nos membres étaient débutants et génèrent maintenant des revenus réguliers.",
            "order": 1,
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": "2", 
            "question": "Combien de temps faut-il pour voir les premiers résultats ?",
            "answer": "La plupart de nos membres voient leurs premiers gains dans les 30 à 60 jours. Certains ont généré leurs premiers 500€ en seulement 3 semaines en appliquant nos méthodes à la lettre.",
            "order": 2,
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": "3",
            "question": "Y a-t-il une garantie de remboursement ?",
            "answer": "Oui ! Nous offrons une garantie satisfait ou remboursé de 30 jours. Si vous n'êtes pas entièrement satisfait, nous vous remboursons intégralement, sans question.",
            "order": 3,
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": "4",
            "question": "Faut-il déjà avoir une audience sur les réseaux sociaux ?",
            "answer": "Pas du tout ! Nos méthodes fonctionnent même si vous partez de zéro follower. Nous vous enseignons comment créer et développer votre audience tout en monétisant dès le départ.",
            "order": 4,
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": "5",
            "question": "Le coaching est-il vraiment personnalisé ?",
            "answer": "Oui, avec l'offre Premium à 297€, vous bénéficiez de sessions de coaching individuelles avec nos experts, adaptées à votre situation et vos objectifs spécifiques.",
            "order": 5,
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": "6",
            "question": "Combien de temps ai-je accès à la formation ?",
            "answer": "L'accès à la formation est à vie ! Vous pourrez revoir les modules autant de fois que nécessaire et bénéficier de toutes les mises à jour gratuites.",
            "order": 6,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
    ]
    
    result = await db.faqs.insert_many(faqs_data)
    print(f"Seeded {len(result.inserted_ids)} FAQs")

async def init_database(db: AsyncIOMotorDatabase):
    """Initialize database with seed data"""
    print("Initializing database...")
    
    # Create indexes
    await db.testimonials.create_index("is_active")
    await db.testimonials.create_index("created_at")
    await db.faqs.create_index([("order", 1), ("is_active", 1)])
    await db.email_subscribers.create_index("email", unique=True)
    await db.email_subscribers.create_index("is_active")
    await db.analytics_events.create_index("timestamp")
    await db.analytics_events.create_index("session_id")
    await db.chat_messages.create_index("session_id")
    await db.chat_messages.create_index("timestamp")
    await db.leads.create_index("email")
    await db.leads.create_index("created_at")
    
    print("Database indexes created")
    
    # Seed data
    await seed_testimonials(db)
    await seed_faqs(db)
    
    print("Database initialization completed!")