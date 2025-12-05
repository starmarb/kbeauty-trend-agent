from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, 
    DateTime, ForeignKey, JSON, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()


class Content(Base):
    """Raw content collected from platforms."""
    __tablename__ = "content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(String(50), nullable=False)  # reddit, tiktok, youtube
    source_url = Column(Text, unique=True, nullable=False)
    content_text = Column(Text)
    author_id = Column(String(200))
    published_at = Column(DateTime)
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    # Filtering
    authenticity_score = Column(Float)
    is_organic = Column(Boolean, default=True)
    
    # Language
    language = Column(String(10))
    inferred_region = Column(String(10))
    
    # Engagement
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
    
    # Raw data
    raw_metadata = Column(JSON)
    
    # Relationships
    entities = relationship("ContentEntity", back_populates="content")
    
    __table_args__ = (
        Index("ix_content_platform_published", "platform", "published_at"),
        Index("ix_content_collected_at", "collected_at"),
    )


class ContentEntity(Base):
    """Entities extracted from content (brands, ingredients, etc.)."""
    __tablename__ = "content_entities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id"), nullable=False)
    entity_type = Column(String(50), nullable=False)  # brand, ingredient, aesthetic
    entity_id = Column(String(200), nullable=False)  # normalized identifier
    entity_value = Column(String(200))  # original matched text
    confidence = Column(Float, default=1.0)
    
    # Relationships
    content = relationship("Content", back_populates="entities")
    
    __table_args__ = (
        Index("ix_content_entity_type_id", "entity_type", "entity_id"),
        UniqueConstraint("content_id", "entity_type", "entity_id", name="uq_content_entity"),
    )


class Trend(Base):
    """Trend entities (topics being tracked over time)."""
    __tablename__ = "trends"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    name_ko = Column(String(200))  # Korean name
    category = Column(String(50))  # aesthetic, formulation, general
    
    # Lifecycle
    first_detected_at = Column(DateTime, default=datetime.utcnow)
    current_stage = Column(String(50))  # emerging, growing, peak, declining
    
    # Clustering
    parent_trend_id = Column(UUID(as_uuid=True), ForeignKey("trends.id"))
    cluster_keywords = Column(ARRAY(String))
    
    # Relationships
    parent_trend = relationship("Trend", remote_side=[id])
    relationships_as_source = relationship(
        "TrendRelationship",
        foreign_keys="TrendRelationship.source_trend_id",
        back_populates="source_trend"
    )
    metrics = relationship("TrendMetrics", back_populates="trend")


class TrendRelationship(Base):
    """Relationships between trends (parent-child, evolution, etc.)."""
    __tablename__ = "trend_relationships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_trend_id = Column(UUID(as_uuid=True), ForeignKey("trends.id"), nullable=False)
    target_trend_id = Column(UUID(as_uuid=True), ForeignKey("trends.id"), nullable=False)
    relationship_type = Column(String(50), nullable=False)  # parent_child, evolution, aesthetic_link
    confidence = Column(Float, default=1.0)
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    source_trend = relationship("Trend", foreign_keys=[source_trend_id])
    target_trend = relationship("Trend", foreign_keys=[target_trend_id])
    
    __table_args__ = (
        UniqueConstraint("source_trend_id", "target_trend_id", "relationship_type", name="uq_trend_rel"),
    )


class TrendMetrics(Base):
    """Daily metrics per trend per region."""
    __tablename__ = "trend_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trend_id = Column(UUID(as_uuid=True), ForeignKey("trends.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    region = Column(String(10), default="global")
    
    # Volume
    mention_count = Column(Integer, default=0)
    unique_authors = Column(Integer, default=0)
    total_engagement = Column(Integer, default=0)
    
    # Velocity
    wow_change = Column(Float)  # week-over-week % change
    
    # Sentiment
    avg_sentiment = Column(Float)
    avg_purchase_intent = Column(Float)
    
    # Platform breakdown
    platform_breakdown = Column(JSON)  # {"reddit": 100, "tiktok": 200}
    
    # Relationships
    trend = relationship("Trend", back_populates="metrics")
    
    __table_args__ = (
        UniqueConstraint("trend_id", "date", "region", name="uq_trend_metrics"),
        Index("ix_trend_metrics_date", "date"),
    )


class BrandTopicShare(Base):
    """Brand share of voice within a topic."""
    __tablename__ = "brand_topic_share"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trend_id = Column(UUID(as_uuid=True), ForeignKey("trends.id"), nullable=False)
    brand = Column(String(100), nullable=False)
    is_amorepacific = Column(Boolean, default=False)
    date = Column(DateTime, nullable=False)
    region = Column(String(10), default="global")
    
    mention_count = Column(Integer, default=0)
    share_of_voice = Column(Float)
    avg_sentiment = Column(Float)
    top_products = Column(JSON)
    
    __table_args__ = (
        UniqueConstraint("trend_id", "brand", "date", "region", name="uq_brand_topic"),
        Index("ix_brand_topic_brand", "brand"),
    )


class Alert(Base):
    """Generated alerts for stakeholders."""
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trend_id = Column(UUID(as_uuid=True), ForeignKey("trends.id"))
    alert_type = Column(String(50), nullable=False)  # new_trend, sentiment_shift, etc.
    triggered_at = Column(DateTime, default=datetime.utcnow)
    
    # Content
    title = Column(String(500))
    title_ko = Column(String(500))
    payload = Column(JSON)
    
    # Status
    status = Column(String(20), default="pending")  # pending, sent, acknowledged
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)


class DailyReport(Base):
    """Generated daily reports."""
    __tablename__ = "daily_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_date = Column(DateTime, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Content
    report_content_ko = Column(Text)  # Korean report
    report_content_en = Column(Text)  # English report (optional)
    
    # Metadata
    topics_covered = Column(ARRAY(UUID(as_uuid=True)))
    insights_summary = Column(JSON)
    
    __table_args__ = (
        UniqueConstraint("report_date", name="uq_daily_report_date"),
    )