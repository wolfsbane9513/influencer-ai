"""SQLAlchemy database models"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
import enum

class CampaignStatusEnum(enum.Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    COMPLETED = "completed"
    PAUSED = "paused"

class NegotiationStatusEnum(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"

class ContractStatusEnum(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    SIGNED = "signed"
    EXECUTED = "executed"
    CANCELLED = "cancelled"

class Campaign(Base):
    """Campaign database model"""
    __tablename__ = "campaigns"
    
    id = Column(String, primary_key=True)
    product_name = Column(String, nullable=False)
    brand_name = Column(String, nullable=False)
    product_description = Column(Text)
    target_audience = Column(Text)
    campaign_goal = Column(Text)
    product_niche = Column(String)
    total_budget = Column(Float, nullable=False)
    status = Column(Enum(CampaignStatusEnum), default=CampaignStatusEnum.ACTIVE)
    influencer_count = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Additional fields
    ai_strategy = Column(JSON)
    campaign_code = Column(String)
    
    # Relationships
    negotiations = relationship("Negotiation", back_populates="campaign", cascade="all, delete-orphan")
    contracts = relationship("Contract", back_populates="campaign", cascade="all, delete-orphan")
    outreach_logs = relationship("OutreachLog", back_populates="campaign", cascade="all, delete-orphan")

class Creator(Base):
    """Creator database model"""
    __tablename__ = "creators"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    followers = Column(Integer, nullable=False)
    niche = Column(String)
    typical_rate = Column(Float)
    engagement_rate = Column(Float)
    average_views = Column(Integer)
    availability = Column(String)
    location = Column(String)
    phone_number = Column(String)
    languages = Column(JSON)
    specialties = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_campaign_date = Column(DateTime(timezone=True))
    
    # Relationships
    negotiations = relationship("Negotiation", back_populates="creator")
    contracts = relationship("Contract", back_populates="creator")

class Negotiation(Base):
    """Negotiation database model"""
    __tablename__ = "negotiations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    creator_id = Column(String, ForeignKey("creators.id"), nullable=False)
    
    # Negotiation details
    status = Column(Enum(NegotiationStatusEnum), default=NegotiationStatusEnum.PENDING)
    initial_rate = Column(Float)
    final_rate = Column(Float)
    negotiated_terms = Column(JSON)
    
    # Communication details
    call_status = Column(String)
    email_status = Column(String)
    call_duration_seconds = Column(Integer, default=0)
    call_recording_url = Column(Text)
    call_transcript = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_contact_date = Column(DateTime(timezone=True))
    
    # Relationships
    campaign = relationship("Campaign", back_populates="negotiations")
    creator = relationship("Creator", back_populates="negotiations")

class Contract(Base):
    """Contract database model"""
    __tablename__ = "contracts"
    
    id = Column(String, primary_key=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    creator_id = Column(String, ForeignKey("creators.id"), nullable=False)
    
    # Contract details
    compensation_amount = Column(Float, nullable=False)
    deliverables = Column(JSON)
    timeline = Column(JSON)
    usage_rights = Column(JSON)
    status = Column(Enum(ContractStatusEnum), default=ContractStatusEnum.DRAFT)
    
    # Contract content
    contract_text = Column(Text)
    legal_review_status = Column(String, default="pending")
    amendments = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    signed_at = Column(DateTime(timezone=True))
    
    # Relationships
    campaign = relationship("Campaign", back_populates="contracts")
    creator = relationship("Creator", back_populates="contracts")
    payments = relationship("Payment", back_populates="contract", cascade="all, delete-orphan")

class Payment(Base):
    """Payment database model"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(String, ForeignKey("contracts.id"), nullable=False)
    
    # Payment details
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, completed, failed
    payment_method = Column(String, default="bank_transfer")
    due_date = Column(DateTime(timezone=True))
    paid_date = Column(DateTime(timezone=True))
    
    # Additional info
    transaction_id = Column(String)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    contract = relationship("Contract", back_populates="payments")

class OutreachLog(Base):
    """Outreach log database model"""
    __tablename__ = "outreach_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    creator_id = Column(String, nullable=False)
    
    # Outreach details
    contact_type = Column(String)  # call, email, message
    status = Column(String)
    duration_minutes = Column(Integer)
    recording_url = Column(Text)
    transcript = Column(Text)
    sentiment = Column(String)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="outreach_logs")