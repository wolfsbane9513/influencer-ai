# services/openai_service.py
import openai
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import os
from decouple import config

logger = logging.getLogger(__name__)

class OpenAINegotiationService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=config('OPENAI_API_KEY')
        )
        self.model = "gpt-4-1106-preview"
    
    def generate_negotiation_response(
        self, 
        conversation_context: Dict[str, Any], 
        user_message: str, 
        speaker: str
    ) -> Dict[str, Any]:
        """Generate AI negotiation response based on context and user input"""
        
        try:
            # Build system prompt for professional consultant persona
            system_prompt = self._build_system_prompt(conversation_context)
            
            # Build conversation history
            messages = self._build_conversation_history(conversation_context, user_message, speaker)
            
            # Get AI response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                temperature=0.7,
                max_tokens=400,
                functions=[
                    {
                        "name": "update_deal_parameters",
                        "description": "Update deal parameters during negotiation",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "price": {"type": "integer", "description": "Updated price offer"},
                                "deliverables": {
                                    "type": "array", 
                                    "items": {"type": "string"},
                                    "description": "Updated list of deliverables"
                                },
                                "timeline": {"type": "string", "description": "Updated timeline"},
                                "usage_rights": {"type": "string", "description": "Updated usage rights"},
                                "rationale": {"type": "string", "description": "Explanation for the changes"}
                            },
                            "required": ["rationale"]
                        }
                    }
                ],
                function_call="auto"
            )
            
            # Process response
            message = response.choices[0].message
            
            result = {
                "message": message.content or "",
                "insights": self._extract_insights(conversation_context, user_message),
                "strategy_notes": self._generate_strategy_notes(conversation_context, user_message)
            }
            
            # Handle function calls (deal parameter updates)
            if message.function_call:
                function_result = self._handle_function_call(message.function_call, conversation_context)
                result.update(function_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return {
                "message": "I apologize, but I'm experiencing technical difficulties. Let me try a different approach to this negotiation.",
                "insights": [],
                "strategy_notes": "System error occurred during response generation."
            }
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build comprehensive system prompt for negotiation AI"""
        
        creator = context["creator_profile"]
        deal_params = context["deal_params"]
        strategy = context["negotiation_strategy"]
        
        return f"""You are an expert AI negotiation consultant helping an agency negotiate with influencer creators. Your role is to be a professional, data-driven advisor who helps secure favorable deals while maintaining positive relationships.

CREATOR PROFILE:
- Name: {creator["name"]}
- Platform: {creator["platform"]} ({creator["followers"]:,} followers)
- Niche: {creator["niche"]}
- Typical Rate: ${creator["typical_rate"]:,}
- Engagement Rate: {creator["engagement_rate"]}%
- Average Views: {creator["average_views"]:,}
- Last Campaign: {creator["last_campaign_date"]}
- Performance: {creator["performance_metrics"]["avg_completion_rate"]}% completion rate

CURRENT DEAL STATUS:
- Current Offer: ${deal_params["price"]:,}
- Deliverables: {', '.join(deal_params["deliverables"])}
- Timeline: {deal_params["timeline"]}
- Usage Rights: {deal_params.get("usage_rights", "Standard")}

NEGOTIATION STRATEGY:
- Opening Price: ${strategy["opening_price"]:,}
- Max Budget: ${strategy["max_budget"]:,}
- Flexibility Areas: {', '.join(strategy["flexibility_areas"])}
- Key Selling Points: {'; '.join(strategy["key_selling_points"])}

YOUR PERSONALITY & APPROACH:
- Professional consultant tone - confident but respectful
- Always back up suggestions with specific data and metrics
- Use performance metrics and market comparisons in your reasoning
- Suggest creative solutions that benefit both parties
- Show expertise in influencer marketing industry standards
- Be persuasive but not pushy
- Focus on value creation, not just cost reduction

DATA-DRIVEN INSIGHTS TO USE:
- Cost per view: ${strategy["data_points"]["cost_per_view"]:.4f}
- Engagement value: ${strategy["data_points"]["engagement_value"]:.2f} per engaged user
- Market position: Compare to industry standards for {creator["niche"]} creators
- ROI projections: Calculate expected campaign performance

NEGOTIATION GUIDELINES:
1. If creator asks for higher rates, counter with value-based reasoning
2. If creator has timeline concerns, explore flexible solutions
3. If creator wants more deliverables, calculate fair additional compensation
4. If creator seems hesitant, emphasize their strengths and campaign potential
5. Always maintain professional relationship - this could lead to future collaborations

When the creator makes a counter-offer or raises concerns, respond professionally with data-backed suggestions. Use the update_deal_parameters function when you want to propose specific changes to the deal terms.

Remember: Your goal is to help the agency secure a fair deal while making the creator feel valued and excited about the collaboration."""

    def _build_conversation_history(
        self, 
        context: Dict[str, Any], 
        user_message: str, 
        speaker: str
    ) -> List[Dict[str, str]]:
        """Build conversation history for context"""
        
        messages = []
        
        # Add previous conversation messages
        for msg in context.get("messages", []):
            role = "assistant" if msg["role"] == "ai_agent" else "user"
            messages.append({
                "role": role,
                "content": f"[{msg['role'].upper()}]: {msg['content']}"
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": f"[{speaker.upper()}]: {user_message}"
        })
        
        return messages
    
    def _extract_insights(self, context: Dict[str, Any], user_message: str) -> List[str]:
        """Extract relevant insights based on conversation context"""
        
        creator = context["creator_profile"]
        deal_params = context["deal_params"]
        strategy = context["negotiation_strategy"]
        
        insights = []
        
        # Performance insights
        if creator["engagement_rate"] > 5.0:
            insights.append(f"High engagement rate ({creator['engagement_rate']}%) suggests quality audience")
        
        # Pricing insights
        current_rate_percentage = (deal_params["price"] / creator["typical_rate"]) * 100
        insights.append(f"Current offer is {current_rate_percentage:.0f}% of creator's typical rate")
        
        # Market positioning
        cost_per_view = deal_params["price"] / creator["average_views"]
        insights.append(f"Cost per view: ${cost_per_view:.4f} - {self._evaluate_cost_efficiency(cost_per_view, creator['niche'])}")
        
        # Timeline considerations
        if "friday" in deal_params["timeline"].lower() or "urgent" in user_message.lower():
            insights.append("Rush timeline may justify premium pricing (+15-25%)")
        
        return insights
    
    def _evaluate_cost_efficiency(self, cost_per_view: float, niche: str) -> str:
        """Evaluate cost efficiency based on niche benchmarks"""
        benchmarks = {
            "tech": {"excellent": 0.015, "good": 0.025, "average": 0.035},
            "beauty": {"excellent": 0.012, "good": 0.020, "average": 0.030},
            "fitness": {"excellent": 0.018, "good": 0.028, "average": 0.040},
            "gaming": {"excellent": 0.020, "good": 0.030, "average": 0.045}
        }
        
        niche_benchmarks = benchmarks.get(niche, benchmarks["tech"])
        
        if cost_per_view <= niche_benchmarks["excellent"]:
            return "excellent value"
        elif cost_per_view <= niche_benchmarks["good"]:
            return "good value"
        elif cost_per_view <= niche_benchmarks["average"]:
            return "market average"
        else:
            return "above market rate"
    
    def _generate_strategy_notes(self, context: Dict[str, Any], user_message: str) -> str:
        """Generate strategy notes for the negotiation"""
        
        # Analyze user message for negotiation cues
        if any(word in user_message.lower() for word in ["expensive", "budget", "cost", "price"]):
            return "Creator is price-sensitive. Focus on value proposition and ROI data."
        elif any(word in user_message.lower() for word in ["timeline", "time", "rush", "deadline"]):
            return "Timeline is key concern. Consider extended deadline for better rate."
        elif any(word in user_message.lower() for word in ["deliverables", "content", "posts", "videos"]):
            return "Creator wants clarity on scope. Define deliverables precisely."
        else:
            return "Maintain professional tone and use data to support negotiations."
    
    def _handle_function_call(self, function_call, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle function calls for updating deal parameters"""
        
        try:
            if function_call.name == "update_deal_parameters":
                # Parse function arguments
                args = json.loads(function_call.arguments)
                
                # Build updated deal parameters
                updated_deal = {}
                for key, value in args.items():
                    if key != "rationale" and value is not None:
                        updated_deal[key] = value
                
                return {
                    "updated_deal": updated_deal,
                    "rationale": args.get("rationale", "Deal parameters updated based on negotiation progress"),
                    "function_used": True
                }
        except Exception as e:
            logger.error(f"Error handling function call: {str(e)}")
        
        return {"function_used": False}

    def generate_initial_strategy(self, campaign_brief: Dict[str, Any], creator_profile: Dict[str, Any]) -> str:
        """Generate initial negotiation strategy message"""
        
        try:
            prompt = f"""As an expert negotiation consultant, provide a strategic briefing for negotiating with this creator:

CREATOR: {creator_profile['name']}
- Platform: {creator_profile['platform']} ({creator_profile['followers']:,} followers)
- Niche: {creator_profile['niche']}
- Typical Rate: ${creator_profile['typical_rate']:,}
- Engagement: {creator_profile['engagement_rate']}%
- Avg Views: {creator_profile['average_views']:,}

CAMPAIGN REQUEST:
- Budget: ${campaign_brief['budget']:,}
- Deliverables: {', '.join(campaign_brief['deliverables'])}
- Timeline: {campaign_brief['timeline']}
- Type: {campaign_brief['campaign_type']}

Provide a concise strategy briefing (2-3 sentences) with:
1. Recommended opening offer with rationale
2. Key negotiation points to emphasize
3. Creator's likely concerns and how to address them"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating initial strategy: {str(e)}")
            return f"Based on {creator_profile['name']}'s profile, I recommend starting at ${int(creator_profile['typical_rate'] * 0.85):,} and emphasizing their strong engagement metrics."