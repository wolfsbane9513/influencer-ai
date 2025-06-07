# agents/campaign_data_collector.py
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import pandas as pd
from pydantic import BaseModel
from enum import Enum

from models.campaign import CampaignData
from services.enhanced_voice import EnhancedVoiceService

logger = logging.getLogger(__name__)

class DataCollectionMethod(str, Enum):
    MANUAL = "manual"
    FILE_UPLOAD = "file_upload"
    CONVERSATIONAL = "conversational"
    API_INTEGRATION = "api_integration"

class CampaignDataCollectionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATION_REQUIRED = "validation_required"
    COMPLETED = "completed"
    FAILED = "failed"

class DataCollectionSession(BaseModel):
    """Track data collection progress in real-time"""
    session_id: str
    method: DataCollectionMethod
    status: CampaignDataCollectionStatus
    progress_percentage: float = 0.0
    collected_fields: Dict[str, Any] = {}
    missing_fields: List[str] = []
    validation_errors: List[str] = []
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    def get_completion_percentage(self) -> float:
        """Calculate completion based on required fields"""
        required_fields = [
            "product_name", "brand_name", "product_description", 
            "target_audience", "campaign_goal", "total_budget", "product_niche"
        ]
        
        completed = sum(1 for field in required_fields if field in self.collected_fields and self.collected_fields[field])
        return (completed / len(required_fields)) * 100.0

class EnhancedCampaignDataCollector:
    """
    🎯 ENHANCED CAMPAIGN DATA COLLECTOR
    
    Supports multiple data collection methods:
    1. Manual input (existing)
    2. File upload with auto-processing
    3. Conversational AI data gathering
    4. API integrations
    """
    
    def __init__(self):
        self.voice_service = EnhancedVoiceService()
        self.active_sessions: Dict[str, DataCollectionSession] = {}
        
        # File processors for different formats
        self.supported_formats = ['.csv', '.xlsx', '.json', '.txt', '.pdf']
        
        # Conversational AI prompts
        self.conversation_prompts = self._load_conversation_prompts()
    
    async def start_data_collection(
        self, 
        method: DataCollectionMethod,
        initial_data: Optional[Dict[str, Any]] = None,
        file_path: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> DataCollectionSession:
        """🚀 Start data collection process"""
        
        if not session_id:
            session_id = f"campaign_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = DataCollectionSession(
            session_id=session_id,
            method=method,
            status=CampaignDataCollectionStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        if initial_data:
            session.collected_fields.update(initial_data)
        
        self.active_sessions[session_id] = session
        
        logger.info(f"🎯 Started data collection: {method.value} (session: {session_id})")
        
        # Route to appropriate collection method
        if method == DataCollectionMethod.MANUAL:
            await self._process_manual_input(session)
        elif method == DataCollectionMethod.FILE_UPLOAD:
            await self._process_file_upload(session, file_path)
        elif method == DataCollectionMethod.CONVERSATIONAL:
            await self._process_conversational_input(session)
        elif method == DataCollectionMethod.API_INTEGRATION:
            await self._process_api_integration(session)
        
        return session
    
    async def _process_manual_input(self, session: DataCollectionSession):
        """📝 Process manual input (existing method)"""
        
        session.status = CampaignDataCollectionStatus.VALIDATION_REQUIRED
        session.progress_percentage = session.get_completion_percentage()
        
        logger.info(f"📝 Manual input session ready for validation")
    
    async def _process_file_upload(self, session: DataCollectionSession, file_path: Optional[str]):
        """📄 Process uploaded file and extract campaign data"""
        
        if not file_path or not Path(file_path).exists():
            session.status = CampaignDataCollectionStatus.FAILED
            session.validation_errors.append("File not found")
            return
        
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.csv':
                extracted_data = await self._process_csv_file(file_path)
            elif file_ext == '.xlsx':
                extracted_data = await self._process_excel_file(file_path)
            elif file_ext == '.json':
                extracted_data = await self._process_json_file(file_path)
            elif file_ext == '.txt':
                extracted_data = await self._process_text_file(file_path)
            elif file_ext == '.pdf':
                extracted_data = await self._process_pdf_file(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Update session with extracted data
            session.collected_fields.update(extracted_data)
            session.progress_percentage = session.get_completion_percentage()
            
            # Validate completeness
            await self._validate_collected_data(session)
            
            logger.info(f"📄 File processed: {len(extracted_data)} fields extracted")
            
        except Exception as e:
            session.status = CampaignDataCollectionStatus.FAILED
            session.validation_errors.append(f"File processing error: {str(e)}")
            logger.error(f"❌ File processing failed: {e}")
    
    async def _process_csv_file(self, file_path: str) -> Dict[str, Any]:
        """Process CSV campaign brief"""
        
        df = pd.read_csv(file_path)
        extracted_data = {}
        
        # Look for campaign data in various CSV formats
        if 'campaign_name' in df.columns or 'product_name' in df.columns:
            # Direct mapping CSV
            for _, row in df.iterrows():
                for col in df.columns:
                    if col.lower() in ['product_name', 'brand_name', 'description', 'budget']:
                        extracted_data[col.lower()] = row[col]
        else:
            # Key-value pair CSV
            for _, row in df.iterrows():
                if len(df.columns) >= 2:
                    key = str(row.iloc[0]).lower().replace(' ', '_')
                    value = row.iloc[1]
                    
                    # Map common variations
                    key_mapping = {
                        'product': 'product_name',
                        'brand': 'brand_name',
                        'description': 'product_description',
                        'audience': 'target_audience',
                        'goal': 'campaign_goal',
                        'budget': 'total_budget',
                        'niche': 'product_niche'
                    }
                    
                    mapped_key = key_mapping.get(key, key)
                    extracted_data[mapped_key] = value
        
        return extracted_data
    
    async def _process_excel_file(self, file_path: str) -> Dict[str, Any]:
        """Process Excel campaign brief"""
        
        # Try different sheet names
        sheet_names = ['Campaign', 'Brief', 'Data', 0]
        
        for sheet in sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet)
                return await self._extract_from_dataframe(df)
            except:
                continue
        
        # Fallback to first sheet
        df = pd.read_excel(file_path)
        return await self._extract_from_dataframe(df)
    
    async def _extract_from_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract campaign data from any DataFrame"""
        
        extracted_data = {}
        
        # Method 1: Column-based extraction
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['product', 'brand', 'budget', 'audience']):
                if not df[col].isna().all():
                    value = df[col].iloc[0] if not pd.isna(df[col].iloc[0]) else df[col].dropna().iloc[0]
                    extracted_data[col_lower.replace(' ', '_')] = value
        
        # Method 2: Key-value pair extraction
        if len(df.columns) == 2:
            for _, row in df.iterrows():
                if not pd.isna(row.iloc[0]) and not pd.isna(row.iloc[1]):
                    key = str(row.iloc[0]).lower().replace(' ', '_')
                    value = row.iloc[1]
                    extracted_data[key] = value
        
        return extracted_data
    
    async def _process_json_file(self, file_path: str) -> Dict[str, Any]:
        """Process JSON campaign brief"""
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Handle nested JSON structures
        extracted_data = {}
        
        def flatten_json(obj, prefix=''):
            for key, value in obj.items():
                if isinstance(value, dict):
                    flatten_json(value, f"{prefix}{key}_")
                else:
                    final_key = f"{prefix}{key}".lower()
                    extracted_data[final_key] = value
        
        if isinstance(data, dict):
            flatten_json(data)
        elif isinstance(data, list) and len(data) > 0:
            flatten_json(data[0])  # Take first item
        
        return extracted_data
    
    async def _process_text_file(self, file_path: str) -> Dict[str, Any]:
        """Process text file using AI extraction"""
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Use AI to extract structured data from unstructured text
        extracted_data = await self._ai_extract_from_text(content)
        return extracted_data
    
    async def _process_pdf_file(self, file_path: str) -> Dict[str, Any]:
        """Process PDF file (requires additional PDF processing)"""
        
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                content = ""
                for page in reader.pages:
                    content += page.extract_text()
            
            return await self._ai_extract_from_text(content)
            
        except ImportError:
            logger.warning("PyPDF2 not available, PDF processing disabled")
            return {}
    
    async def _ai_extract_from_text(self, text_content: str) -> Dict[str, Any]:
        """Use AI to extract campaign data from unstructured text"""
        
        # This would use a language model to extract structured data
        # For now, using simple keyword matching
        
        extracted_data = {}
        lines = text_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                # Map common patterns
                if any(keyword in key for keyword in ['product', 'name']):
                    extracted_data['product_name'] = value
                elif 'brand' in key:
                    extracted_data['brand_name'] = value
                elif any(keyword in key for keyword in ['description', 'desc']):
                    extracted_data['product_description'] = value
                elif 'audience' in key or 'target' in key:
                    extracted_data['target_audience'] = value
                elif 'budget' in key:
                    # Extract numeric value
                    import re
                    numbers = re.findall(r'\d+', value)
                    if numbers:
                        extracted_data['total_budget'] = float(numbers[0])
                elif 'goal' in key:
                    extracted_data['campaign_goal'] = value
                elif 'niche' in key or 'category' in key:
                    extracted_data['product_niche'] = value
        
        return extracted_data
    
    async def _process_conversational_input(self, session: DataCollectionSession):
        """🗣️ Use conversational AI to gather campaign data"""
        
        logger.info("🗣️ Starting conversational data collection")
        
        # Implement conversational flow using ElevenLabs or similar
        conversation_flow = [
            "Let's gather your campaign information. What's the name of your product?",
            "Great! What's your brand name?",
            "Tell me about your product. What does it do?",
            "Who is your target audience?",
            "What's the main goal of this campaign?",
            "What's your total budget for this campaign?",
            "What category or niche does your product fit into?"
        ]
        
        # This would integrate with voice/chat interface
        # For now, setting up the framework
        
        session.status = CampaignDataCollectionStatus.VALIDATION_REQUIRED
        session.progress_percentage = 50.0  # Partial completion
        
        logger.info("🗣️ Conversational collection in progress...")
    
    async def _process_api_integration(self, session: DataCollectionSession):
        """🔌 Process data from API integrations"""
        
        # This would connect to various APIs (Shopify, WooCommerce, etc.)
        session.status = CampaignDataCollectionStatus.VALIDATION_REQUIRED
        session.progress_percentage = 75.0
        
        logger.info("🔌 API integration collection in progress...")
    
    async def _validate_collected_data(self, session: DataCollectionSession):
        """✅ Validate collected campaign data"""
        
        required_fields = {
            'product_name': str,
            'brand_name': str,
            'product_description': str,
            'target_audience': str,
            'campaign_goal': str,
            'total_budget': (int, float),
            'product_niche': str
        }
        
        session.missing_fields = []
        session.validation_errors = []
        
        for field, field_type in required_fields.items():
            if field not in session.collected_fields:
                session.missing_fields.append(field)
            elif not isinstance(session.collected_fields[field], field_type):
                session.validation_errors.append(f"{field} must be of type {field_type.__name__}")
        
        # Additional validation rules
        if 'total_budget' in session.collected_fields:
            budget = session.collected_fields['total_budget']
            if budget < 500:
                session.validation_errors.append("Budget must be at least $500")
        
        # Set status based on validation
        if not session.missing_fields and not session.validation_errors:
            session.status = CampaignDataCollectionStatus.COMPLETED
            session.completed_at = datetime.now()
        else:
            session.status = CampaignDataCollectionStatus.VALIDATION_REQUIRED
        
        session.progress_percentage = session.get_completion_percentage()
    
    def get_session_status(self, session_id: str) -> Optional[DataCollectionSession]:
        """📊 Get real-time status of data collection"""
        return self.active_sessions.get(session_id)
    
    def get_all_active_sessions(self) -> List[DataCollectionSession]:
        """📋 Get all active collection sessions"""
        return list(self.active_sessions.values())
    
    async def finalize_campaign_data(self, session_id: str) -> Optional[CampaignData]:
        """🏁 Convert collected data to CampaignData model"""
        
        session = self.active_sessions.get(session_id)
        if not session or session.status != CampaignDataCollectionStatus.COMPLETED:
            return None
        
        try:
            campaign_data = CampaignData(
                id=f"campaign_{session_id}",
                **session.collected_fields
            )
            
            logger.info(f"🏁 Campaign data finalized: {campaign_data.id}")
            return campaign_data
            
        except Exception as e:
            logger.error(f"❌ Failed to create campaign data: {e}")
            return None
    
    def _load_conversation_prompts(self) -> Dict[str, str]:
        """Load conversational AI prompts"""
        return {
            "welcome": "Hi! I'm here to help you set up your influencer marketing campaign. Let's gather some information about your product and goals.",
            "product_name": "What's the name of the product you'd like to promote?",
            "brand_name": "What's your brand or company name?",
            "description": "Can you describe your product? What makes it special?",
            "audience": "Who is your target audience? Be as specific as possible.",
            "goal": "What's the main goal of this campaign? (e.g., brand awareness, sales, product launch)",
            "budget": "What's your total budget for this influencer campaign?",
            "niche": "What category or niche does your product fit into? (e.g., fitness, tech, beauty)",
            "completion": "Perfect! I have all the information needed. Let me create your campaign."
        }

# Usage example for the enhanced data collector
class CampaignDataCollectionAPI:
    """API endpoints for enhanced data collection"""
    
    def __init__(self):
        self.collector = EnhancedCampaignDataCollector()
    
    async def upload_campaign_file(self, file_path: str, method: str = "file_upload"):
        """Handle file upload for campaign data"""
        
        session = await self.collector.start_data_collection(
            method=DataCollectionMethod.FILE_UPLOAD,
            file_path=file_path
        )
        
        return {
            "session_id": session.session_id,
            "status": session.status,
            "progress": session.progress_percentage,
            "collected_fields": list(session.collected_fields.keys()),
            "missing_fields": session.missing_fields
        }
    
    async def start_conversational_collection(self, initial_data: Optional[Dict] = None):
        """Start conversational data collection"""
        
        session = await self.collector.start_data_collection(
            method=DataCollectionMethod.CONVERSATIONAL,
            initial_data=initial_data
        )
        
        return {
            "session_id": session.session_id,
            "status": "ready_for_conversation",
            "next_prompt": self.collector.conversation_prompts["welcome"]
        }