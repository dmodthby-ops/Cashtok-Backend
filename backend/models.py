from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid

# Testimonial Models
class Testimonial(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    image: str
    text: str
    platform: str
    revenue: str
    rating: int = Field(ge=1, le=5)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class TestimonialCreate(BaseModel):
    name: str
    image: str
    text: str
    platform: str
    revenue: str
    rating: int = Field(ge=1, le=5)

# FAQ Models
class FAQ(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    answer: str
    order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FAQCreate(BaseModel):
    question: str
    answer: str
    order: int = 0

# Email Subscriber Models
class EmailSubscriber(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    source: str  # hero_section, offers, footer, etc.
    interests: List[str] = []
    subscribed_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    confirmed: bool = False

class EmailSubscriberCreate(BaseModel):
    email: EmailStr
    source: str = "unknown"
    interests: List[str] = []

# Analytics Models
class AnalyticsEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str  # page_view, cta_click, section_view, etc.
    page: str = "/"
    section: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    referrer: Optional[str] = None
    device_type: str = "unknown"  # mobile, desktop, tablet
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    additional_data: dict = {}

class AnalyticsEventCreate(BaseModel):
    event_type: str
    page: str = "/"
    section: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    device_type: str = "unknown"
    session_id: Optional[str] = None
    additional_data: dict = {}

class AnalyticsStats(BaseModel):
    total_visitors: int
    total_page_views: int
    conversion_rate: float
    average_time_on_site: str
    top_traffic_sources: List[str]
    device_breakdown: dict
    popular_sections: List[dict]

# Chat Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    user_name: str = "Visiteur"
    user_email: Optional[EmailStr] = None
    message: str
    is_admin: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str
    read: bool = False

class ChatMessageCreate(BaseModel):
    message: str
    user_name: str = "Visiteur"
    user_email: Optional[EmailStr] = None
    session_id: str

class ChatResponse(BaseModel):
    message: str
    session_id: str

# Lead Models
class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    interest_level: str = "low"  # low, medium, high
    source: str = "website"
    notes: str = ""
    status: str = "new"  # new, contacted, qualified, converted
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LeadCreate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    interest_level: str = "medium"
    source: str = "website"
    notes: str = ""

# Newsletter Campaign Models  
class NewsletterCampaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject: str
    content: str
    html_content: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    status: str = "draft"  # draft, scheduled, sending, sent
    recipients_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0