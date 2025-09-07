import asyncio
import uuid
from typing import List, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
import json
from collections import defaultdict, Counter

class TestimonialService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.testimonials

    async def get_all_active(self) -> List[dict]:
        """Get all active testimonials"""
        testimonials = await self.collection.find(
            {"is_active": True}
        ).sort("created_at", -1).to_list(100)
        return testimonials

    async def create(self, testimonial_data: dict) -> dict:
        """Create new testimonial"""
        result = await self.collection.insert_one(testimonial_data)
        return await self.collection.find_one({"_id": result.inserted_id})

class FAQService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.faqs

    async def get_all_active(self) -> List[dict]:
        """Get all active FAQs ordered by order field"""
        faqs = await self.collection.find(
            {"is_active": True}
        ).sort("order", 1).to_list(100)
        return faqs

    async def create(self, faq_data: dict) -> dict:
        """Create new FAQ"""
        result = await self.collection.insert_one(faq_data)
        return await self.collection.find_one({"_id": result.inserted_id})

class EmailService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.email_subscribers

    async def subscribe(self, subscriber_data: dict) -> dict:
        """Subscribe user to newsletter"""
        # Check if email already exists
        existing = await self.collection.find_one({"email": subscriber_data["email"]})
        
        if existing:
            # Update existing subscription
            await self.collection.update_one(
                {"email": subscriber_data["email"]},
                {
                    "$set": {
                        "is_active": True,
                        "subscribed_at": datetime.utcnow(),
                        "source": subscriber_data.get("source", "unknown"),
                        "interests": subscriber_data.get("interests", [])
                    }
                }
            )
            return await self.collection.find_one({"email": subscriber_data["email"]})
        else:
            # Create new subscription
            result = await self.collection.insert_one(subscriber_data)
            return await self.collection.find_one({"_id": result.inserted_id})

    async def get_all_active(self) -> List[dict]:
        """Get all active subscribers"""
        subscribers = await self.collection.find(
            {"is_active": True}
        ).sort("subscribed_at", -1).to_list(10000)
        return subscribers

    async def get_stats(self) -> dict:
        """Get email subscription stats"""
        total_subscribers = await self.collection.count_documents({"is_active": True})
        
        # Group by source
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {"_id": "$source", "count": {"$sum": 1}}}
        ]
        sources = await self.collection.aggregate(pipeline).to_list(100)
        
        return {
            "total_subscribers": total_subscribers,
            "sources": {item["_id"]: item["count"] for item in sources}
        }

class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.analytics_events

    async def track_event(self, event_data: dict) -> dict:
        """Track an analytics event"""
        result = await self.collection.insert_one(event_data)
        return await self.collection.find_one({"_id": result.inserted_id})

    async def get_stats(self, days: int = 30) -> dict:
        """Get analytics statistics for last N days"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Total visitors (unique sessions)
        unique_sessions = await self.collection.distinct(
            "session_id", 
            {"timestamp": {"$gte": since_date}}
        )
        total_visitors = len(unique_sessions)
        
        # Total page views
        total_page_views = await self.collection.count_documents({
            "event_type": "page_view",
            "timestamp": {"$gte": since_date}
        })
        
        # Device breakdown
        device_pipeline = [
            {"$match": {"timestamp": {"$gte": since_date}}},
            {"$group": {"_id": "$device_type", "count": {"$sum": 1}}}
        ]
        device_data = await self.collection.aggregate(device_pipeline).to_list(100)
        device_breakdown = {item["_id"]: item["count"] for item in device_data}
        
        # Top traffic sources (referrers)
        referrer_pipeline = [
            {"$match": {"timestamp": {"$gte": since_date}, "referrer": {"$ne": None}}},
            {"$group": {"_id": "$referrer", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        referrer_data = await self.collection.aggregate(referrer_pipeline).to_list(5)
        top_referrers = [item["_id"] for item in referrer_data]
        
        # Popular sections
        section_pipeline = [
            {"$match": {"timestamp": {"$gte": since_date}, "section": {"$ne": None}}},
            {"$group": {"_id": "$section", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        section_data = await self.collection.aggregate(section_pipeline).to_list(100)
        popular_sections = [{"section": item["_id"], "views": item["count"]} for item in section_data]
        
        # Mock conversion rate (would be calculated based on actual conversions)
        conversion_rate = 4.8  # Mock value
        
        # Mock average time on site
        average_time_on_site = "3:42"  # Mock value
        
        return {
            "total_visitors": total_visitors,
            "total_page_views": total_page_views,
            "conversion_rate": conversion_rate,
            "average_time_on_site": average_time_on_site,
            "top_traffic_sources": top_referrers if top_referrers else ["Direct", "Google", "Facebook"],
            "device_breakdown": device_breakdown,
            "popular_sections": popular_sections
        }

class ChatService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.chat_messages

    async def save_message(self, message_data: dict) -> dict:
        """Save chat message to database"""
        result = await self.collection.insert_one(message_data)
        return await self.collection.find_one({"_id": result.inserted_id})

    async def get_session_messages(self, session_id: str) -> List[dict]:
        """Get all messages for a session"""
        messages = await self.collection.find(
            {"session_id": session_id}
        ).sort("timestamp", 1).to_list(1000)
        return messages

    async def get_unread_messages(self) -> List[dict]:
        """Get all unread messages for admin"""
        messages = await self.collection.find(
            {"read": False, "is_admin": False}
        ).sort("timestamp", -1).to_list(1000)
        return messages

    async def mark_as_read(self, message_ids: List[str]) -> int:
        """Mark messages as read"""
        result = await self.collection.update_many(
            {"id": {"$in": message_ids}},
            {"$set": {"read": True}}
        )
        return result.modified_count

    async def auto_respond(self, session_id: str) -> dict:
        """Generate auto-response for common questions"""
        auto_responses = [
            "Merci pour votre message ! Un membre de notre équipe vous répondra dans les plus brefs délais.",
            "Bonjour ! Comment puis-je vous aider concernant la formation CASHTOK ?",
            "Excellente question ! Notre équipe support va vous répondre très rapidement.",
        ]
        
        # Simple auto-response logic (can be enhanced with AI)
        response_message = {
            "id": str(uuid.uuid4()),
            "user_id": "system",
            "user_name": "Support CASHTOK",
            "message": auto_responses[0],
            "is_admin": True,
            "timestamp": datetime.utcnow(),
            "session_id": session_id,
            "read": True
        }
        
        return await self.save_message(response_message)

class LeadService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.leads

    async def create_lead(self, lead_data: dict) -> dict:
        """Create new lead"""
        # Check if lead already exists by email
        if lead_data.get("email"):
            existing = await self.collection.find_one({"email": lead_data["email"]})
            if existing:
                # Update existing lead
                await self.collection.update_one(
                    {"email": lead_data["email"]},
                    {
                        "$set": {
                            **lead_data,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                return await self.collection.find_one({"email": lead_data["email"]})
        
        # Create new lead
        result = await self.collection.insert_one(lead_data)
        return await self.collection.find_one({"_id": result.inserted_id})

    async def get_all_leads(self) -> List[dict]:
        """Get all leads"""
        leads = await self.collection.find({}).sort("created_at", -1).to_list(10000)
        return leads

    async def get_stats(self) -> dict:
        """Get lead statistics"""
        total_leads = await self.collection.count_documents({})
        
        # Group by status
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        status_data = await self.collection.aggregate(status_pipeline).to_list(100)
        status_breakdown = {item["_id"]: item["count"] for item in status_data}
        
        # Group by source
        source_pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}}
        ]
        source_data = await self.collection.aggregate(source_pipeline).to_list(100)
        source_breakdown = {item["_id"]: item["count"] for item in source_data}
        
        return {
            "total_leads": total_leads,
            "status_breakdown": status_breakdown,
            "source_breakdown": source_breakdown
        }