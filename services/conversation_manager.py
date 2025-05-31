# services/conversation_manager.py
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, asdict
from models.conversation import MessageRole, ConversationStatus

logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    role: str
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DealParameters:
    price: int
    deliverables: List[str]
    timeline: str
    usage_rights: str = "6 months"
    status: str = "negotiating"
    rush_premium: float = 0.0
    exclusivity_premium: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class NegotiationStrategy:
    opening_price: int
    max_budget: int
    flexibility_areas: List[str]
    key_selling_points: List[str]
    negotiation_approach: str
    data_points: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ConversationManager:
    def __init__(self):
        # In-memory storage (use Redis/Database in production)
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.message_history: Dict[str, List[ConversationMessage]] = {}
    
    def create_conversation(
        self, 
        campaign_brief: Dict[str, Any], 
        creator_profile: Dict[str, Any],
        initial_strategy: Dict[str, Any]
    ) -> str:
        """Create a new conversation with initial state"""
        
        conversation_id = str(uuid.uuid4())
        
        # Initialize deal parameters
        deal_params = DealParameters(
            price=initial_strategy["opening_price"],
            deliverables=campaign_brief["deliverables"],
            timeline=campaign_brief["timeline"],
            usage_rights="6 months",
            status="negotiating"
        )
        
        # Initialize negotiation strategy
        strategy = NegotiationStrategy(
            opening_price=initial_strategy["opening_price"],
            max_budget=initial_strategy["max_budget"],
            flexibility_areas=initial_strategy["flexibility_areas"],
            key_selling_points=initial_strategy["key_selling_points"],
            negotiation_approach=initial_strategy["negotiation_approach"],
            data_points=initial_strategy["data_points"]
        )
        
        # Create conversation state
        conversation_state = {
            "conversation_id": conversation_id,
            "status": ConversationStatus.INITIALIZING.value,
            "deal_params": deal_params.to_dict(),
            "creator_profile": creator_profile,
            "negotiation_strategy": strategy.to_dict(),
            "campaign_brief": campaign_brief,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "metadata": {
                "total_messages": 0,
                "negotiation_rounds": 0,
                "last_offer_price": initial_strategy["opening_price"],
                "price_changes": [],
                "key_discussion_points": []
            }
        }
        
        # Store conversation
        self.conversations[conversation_id] = conversation_state
        self.message_history[conversation_id] = []
        
        # Add initial system message
        self.add_message(
            conversation_id,
            MessageRole.SYSTEM,
            f"Conversation initiated for {creator_profile['name']} - {campaign_brief['campaign_type']} campaign"
        )
        
        logger.info(f"Created conversation {conversation_id} for creator {creator_profile['name']}")
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by ID"""
        return self.conversations.get(conversation_id)
    
    def add_message(
        self, 
        conversation_id: str, 
        role: MessageRole, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a message to the conversation"""
        
        if conversation_id not in self.conversations:
            logger.error(f"Conversation {conversation_id} not found")
            return False
        
        message = ConversationMessage(
            role=role.value,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.message_history[conversation_id].append(message)
        
        # Update conversation metadata
        conversation = self.conversations[conversation_id]
        conversation["metadata"]["total_messages"] += 1
        conversation["updated_at"] = datetime.now()
        
        # Track negotiation rounds
        if role in [MessageRole.AGENCY, MessageRole.CREATOR]:
            conversation["metadata"]["negotiation_rounds"] += 1
        
        return True
    
    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation"""
        messages = self.message_history.get(conversation_id, [])
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            }
            for msg in messages
        ]
    
    def update_deal_parameters(
        self, 
        conversation_id: str, 
        updates: Dict[str, Any],
        rationale: str = ""
    ) -> bool:
        """Update deal parameters and track changes"""
        
        if conversation_id not in self.conversations:
            return False
        
        conversation = self.conversations[conversation_id]
        old_params = conversation["deal_params"].copy()
        
        # Update parameters
        for key, value in updates.items():
            if key in conversation["deal_params"]:
                conversation["deal_params"][key] = value
        
        # Track price changes specifically
        if "price" in updates:
            old_price = old_params.get("price", 0)
            new_price = updates["price"]
            conversation["metadata"]["price_changes"].append({
                "from": old_price,
                "to": new_price,
                "timestamp": datetime.now().isoformat(),
                "rationale": rationale
            })
            conversation["metadata"]["last_offer_price"] = new_price
        
        conversation["updated_at"] = datetime.now()
        
        # Add system message about the change
        self.add_message(
            conversation_id,
            MessageRole.SYSTEM,
            f"Deal parameters updated: {', '.join(f'{k}={v}' for k, v in updates.items())}",
            {"rationale": rationale, "previous_params": old_params}
        )
        
        logger.info(f"Updated deal parameters for conversation {conversation_id}")
        return True
    
    def update_conversation_status(
        self, 
        conversation_id: str, 
        status: ConversationStatus,
        reason: str = ""
    ) -> bool:
        """Update conversation status"""
        
        if conversation_id not in self.conversations:
            return False
        
        conversation = self.conversations[conversation_id]
        old_status = conversation["status"]
        conversation["status"] = status.value
        conversation["updated_at"] = datetime.now()
        
        # Add system message
        self.add_message(
            conversation_id,
            MessageRole.SYSTEM,
            f"Status changed from {old_status} to {status.value}" + (f": {reason}" if reason else "")
        )
        
        logger.info(f"Conversation {conversation_id} status changed to {status.value}")
        return True
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of the conversation state"""
        
        if conversation_id not in self.conversations:
            return None
        
        conversation = self.conversations[conversation_id]
        messages = self.get_messages(conversation_id)
        
        # Calculate negotiation metrics
        price_changes = conversation["metadata"]["price_changes"]
        initial_price = conversation["negotiation_strategy"]["opening_price"]
        current_price = conversation["deal_params"]["price"]
        creator_rate = conversation["creator_profile"]["typical_rate"]
        
        return {
            "conversation_id": conversation_id,
            "status": conversation["status"],
            "creator_name": conversation["creator_profile"]["name"],
            "campaign_type": conversation["campaign_brief"]["campaign_type"],
            "deal_summary": {
                "initial_offer": initial_price,
                "current_offer": current_price,
                "creator_typical_rate": creator_rate,
                "negotiation_progress": round((current_price / creator_rate) * 100, 1),
                "total_price_changes": len(price_changes),
                "deliverables": conversation["deal_params"]["deliverables"],
                "timeline": conversation["deal_params"]["timeline"]
            },
            "conversation_metrics": {
                "total_messages": conversation["metadata"]["total_messages"],
                "negotiation_rounds": conversation["metadata"]["negotiation_rounds"],
                "duration_minutes": (datetime.now() - conversation["created_at"]).total_seconds() / 60,
                "last_updated": conversation["updated_at"].isoformat()
            },
            "recent_messages": messages[-5:] if len(messages) > 5 else messages
        }
    
    def get_negotiation_insights(self, conversation_id: str) -> Dict[str, Any]:
        """Get insights about the negotiation progress"""
        
        if conversation_id not in self.conversations:
            return {}
        
        conversation = self.conversations[conversation_id]
        creator = conversation["creator_profile"]
        deal_params = conversation["deal_params"]
        metadata = conversation["metadata"]
        
        # Calculate insights
        current_price = deal_params["price"]
        creator_rate = creator["typical_rate"]
        initial_offer = conversation["negotiation_strategy"]["opening_price"]
        
        price_vs_typical = (current_price / creator_rate) * 100
        movement_from_initial = current_price - initial_offer
        
        insights = {
            "pricing_analysis": {
                "current_vs_typical_rate": f"{price_vs_typical:.1f}%",
                "movement_from_initial": movement_from_initial,
                "total_price_changes": len(metadata["price_changes"]),
                "negotiation_direction": "increasing" if movement_from_initial > 0 else "decreasing" if movement_from_initial < 0 else "stable"
            },
            "creator_analysis": {
                "engagement_level": creator["engagement_rate"],
                "performance_score": creator["performance_metrics"]["avg_completion_rate"],
                "availability": creator["availability"],
                "collaboration_rating": creator["performance_metrics"].get("collaboration_rating", "N/A")
            },
            "negotiation_status": {
                "rounds_completed": metadata["negotiation_rounds"],
                "conversation_age_minutes": (datetime.now() - conversation["created_at"]).total_seconds() / 60,
                "current_status": conversation["status"]
            },
            "recommendations": self._generate_negotiation_recommendations(conversation)
        }
        
        return insights
    
    def _generate_negotiation_recommendations(self, conversation: Dict[str, Any]) -> List[str]:
        """Generate contextual negotiation recommendations"""
        
        recommendations = []
        current_price = conversation["deal_params"]["price"]
        creator_rate = conversation["creator_profile"]["typical_rate"]
        rounds = conversation["metadata"]["negotiation_rounds"]
        
        # Price-based recommendations
        if current_price < creator_rate * 0.8:
            recommendations.append("Consider increasing offer - current price is significantly below creator's typical rate")
        elif current_price > creator_rate * 1.2:
            recommendations.append("Offer is above market rate - good position for negotiation")
        
        # Round-based recommendations  
        if rounds > 5:
            recommendations.append("Extended negotiation - consider final offer or timeline adjustment")
        elif rounds < 2:
            recommendations.append("Early stage - room for exploration of terms")
        
        # Timeline recommendations
        timeline = conversation["deal_params"]["timeline"].lower()
        if any(word in timeline for word in ["friday", "urgent", "asap"]):
            recommendations.append("Rush timeline - justify premium pricing or offer scope reduction")
        
        return recommendations

# Create global instance
conversation_manager = ConversationManager()