from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
import asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import *
from services import *
import os
from datetime import datetime
import uuid

def get_database():
    from index import db
    return db

# Create router
router = APIRouter(prefix="/api")

# Testimonials Routes
@router.get("/testimonials", response_model=List[Testimonial])
async def get_testimonials(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get all active testimonials"""
    service = TestimonialService(db)
    testimonials = await service.get_all_active()
    return testimonials

@router.post("/testimonials", response_model=Testimonial)
async def create_testimonial(
    testimonial: TestimonialCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create new testimonial (admin only)"""
    service = TestimonialService(db)
    testimonial_dict = Testimonial(**testimonial.dict()).dict()
    result = await service.create(testimonial_dict)
    return result

# FAQ Routes
@router.get("/faqs", response_model=List[FAQ])
async def get_faqs(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get all active FAQs"""
    service = FAQService(db)
    faqs = await service.get_all_active()
    return faqs

@router.post("/faqs", response_model=FAQ)
async def create_faq(
    faq: FAQCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create new FAQ (admin only)"""
    service = FAQService(db)
    faq_dict = FAQ(**faq.dict()).dict()
    result = await service.create(faq_dict)
    return result

# Email Subscription Routes
@router.post("/emails/subscribe", response_model=EmailSubscriber)
async def subscribe_email(
    subscriber: EmailSubscriberCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Subscribe to newsletter"""
    service = EmailService(db)
    
    # Add IP tracking
    subscriber_dict = EmailSubscriber(**subscriber.dict()).dict()
    subscriber_dict["ip_address"] = request.client.host
    
    result = await service.subscribe(subscriber_dict)
    
    # Track analytics event
    analytics_service = AnalyticsService(db)
    await analytics_service.track_event({
        "id": str(uuid.uuid4()),
        "event_type": "email_subscribe",
        "page": "/",
        "section": subscriber.source,
        "ip_address": request.client.host,
        "timestamp": datetime.utcnow(),
        "additional_data": {"email": subscriber.email}
    })
    
    return result

@router.get("/emails", response_model=List[EmailSubscriber])
async def get_email_subscribers(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get all email subscribers (admin only)"""
    service = EmailService(db)
    subscribers = await service.get_all_active()
    return subscribers

@router.get("/emails/stats")
async def get_email_stats(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get email subscription statistics"""
    service = EmailService(db)
    stats = await service.get_stats()
    return stats

# Confirmer l'email du subscriber
@router.get("/emails/confirm/{token}", response_model=EmailSubscriber)
async def confirm_email(token: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Confirme l'inscription à la newsletter via token.
    """
    email_service = EmailService(db)
    subscriber = await email_service.confirm_subscriber(token)
    
    if not subscriber:
        raise HTTPException(status_code=404, detail="Token invalide ou expiré")
    
    # Optionnel : track analytics confirmation
    analytics_service = AnalyticsService(db)
    await analytics_service.track_event({
        "id": str(uuid.uuid4()),
        "event_type": "email_confirmed",
        "page": "/emails/confirm",
        "ip_address": "server",  # ou récupérer IP si besoin
        "timestamp": datetime.utcnow(),
        "additional_data": {
            "email": subscriber.email,
            "source": subscriber.source,
            "interests": subscriber.interests
        }
    })

    return subscriber

# Analytics Routes
@router.post("/analytics/track", response_model=AnalyticsEvent)
async def track_event(
    event: AnalyticsEventCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Track analytics event"""
    service = AnalyticsService(db)
    
    # Add IP and user agent
    event_dict = AnalyticsEvent(**event.dict()).dict()
    event_dict["ip_address"] = request.client.host
    event_dict["user_agent"] = request.headers.get("user-agent", "")
    
    result = await service.track_event(event_dict)
    return result

@router.get("/analytics/stats", response_model=AnalyticsStats)
async def get_analytics_stats(
    days: int = 30,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get analytics statistics"""
    service = AnalyticsService(db)
    stats = await service.get_stats(days)
    return stats

# Chat Routes
@router.post("/chat/message", response_model=ChatMessage)
async def send_chat_message(
    message: ChatMessageCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Send chat message"""
    service = ChatService(db)
    
    # Create message
    message_dict = ChatMessage(**message.dict()).dict()
    message_dict["ip_address"] = request.client.host
    
    result = await service.save_message(message_dict)
    
    # Auto-respond for first message in session
    existing_messages = await service.get_session_messages(message.session_id)
    if len(existing_messages) <= 1:  # First message
        await service.auto_respond(message.session_id)
    
    # Track analytics
    analytics_service = AnalyticsService(db)
    await analytics_service.track_event({
        "id": str(uuid.uuid4()),
        "event_type": "chat_message",
        "page": "/",
        "section": "chat",
        "ip_address": request.client.host,
        "timestamp": datetime.utcnow(),
        "session_id": message.session_id,
        "additional_data": {"message_length": len(message.message)}
    })
    
    return result

@router.get("/chat/messages/{session_id}", response_model=List[ChatMessage])
async def get_chat_messages(
    session_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get chat messages for session"""
    service = ChatService(db)
    messages = await service.get_session_messages(session_id)
    return messages

@router.get("/chat/unread", response_model=List[ChatMessage])
async def get_unread_messages(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get unread messages (admin only)"""
    service = ChatService(db)
    messages = await service.get_unread_messages()
    return messages

@router.post("/chat/mark-read")
async def mark_messages_read(
    message_ids: List[str],
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Mark messages as read (admin only)"""
    service = ChatService(db)
    count = await service.mark_as_read(message_ids)
    return {"marked_count": count}

# Leads Routes
@router.post("/leads", response_model=Lead)
async def create_lead(
    lead: LeadCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create new lead AND subscribe to newsletter"""
    lead_service = LeadService(db)
    email_service = EmailService(db)
    analytics_service = AnalyticsService(db)



    # Lead → DB
    lead_dict = Lead(**lead.dict()).dict()
    lead_dict["ip_address"] = request.client.host
    new_lead = await lead_service.create_lead(lead_dict)


    # Newsletter → DB (2 en 1)
    if lead.email:
        subscriber_dict = {
            "email": lead.email,
            "source": lead.source,
            "interests": lead.interests,
            "ip_address": request.client.host
        }
        try:
            await email_service.subscribe(subscriber_dict)
        except Exception as e:
            print(f"Newsletter subscription failed for {lead.email}: {e}")


    # Analytics → DB
    await analytics_service.track_event({
        "id": str(uuid.uuid4()),
        "event_type": "lead_created",
        "page": "/",
        "ip_address": request.client.host,
        "timestamp": datetime.utcnow(),
        "additional_data": {
            "lead_source": lead.source,
            "interest_level": lead.interest_level,
            "email": lead.email
        }
    })

    return new_lead

@router.get("/emails/confirm/{token}", response_model=EmailSubscriber)
async def confirm_email(token: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Confirme l'inscription à la newsletter via token."""
    email_service = EmailService(db)
    subscriber = await email_service.confirm_subscriber(token)


    if not subscriber:
        raise HTTPException(status_code=404, detail="Token invalide ou expiré")


    # Analytics
    analytics_service = AnalyticsService(db)
    await analytics_service.track_event({
        "id": str(uuid.uuid4()),
        "event_type": "email_confirmed",
        "page": "/emails/confirm",
        "ip_address": "server",
        "timestamp": datetime.utcnow(),
        "additional_data": {
            "email": subscriber["email"],
            "source": subscriber["source"],
            "interests": subscriber.get("interests", [])
        }
    })

    return subscriber


@router.get("/leads", response_model=List[Lead])
async def get_leads(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get all leads (admin only)"""
    service = LeadService(db)
    leads = await service.get_all_leads()
    return leads

@router.get("/leads/stats")
async def get_lead_stats(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get lead statistics"""
    service = LeadService(db)
    stats = await service.get_stats()
    return stats

# Utility Routes
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CASHTOK System API",
        "version": "1.0.0",
        "endpoints": {
            "testimonials": "/api/testimonials",
            "faqs": "/api/faqs", 
            "email_subscribe": "/api/emails/subscribe",
            "analytics_track": "/api/analytics/track",
            "chat": "/api/chat/message",
            "leads": "/api/leads"
        }
    }