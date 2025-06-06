# services/document_processor.py
import asyncio
import logging
import json
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import tempfile
import os
from pathlib import Path

# PDF processing
try:
    import PyPDF2
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Word document processing  
try:
    import mammoth
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# AI processing
from groq import Groq
from config.settings import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    📄 DOCUMENT PROCESSOR - AI-Powered Brief Parser
    
    Features:
    - PDF, DOCX, TXT campaign brief parsing
    - Intelligent data extraction using AI
    - Campaign parameter detection
    - Creator requirements analysis
    - Budget and timeline extraction
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        
        # Document processing capabilities
        self.supported_formats = {
            "application/pdf": "PDF",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
            "text/plain": "TXT",
            "text/markdown": "MD"
        }
        
        # AI extraction templates
        self.extraction_templates = {
            "campaign_brief": {
                "fields": [
                    "brand_name", "product_name", "product_description", 
                    "target_audience", "campaign_goal", "product_niche",
                    "total_budget", "timeline", "deliverables", "usage_rights",
                    "creator_requirements", "content_guidelines"
                ],
                "prompt_template": """
                Extract campaign details from this document. Return JSON only.
                
                Document content: "{content}"
                
                Extract these fields if present:
                {{
                    "brand_name": "string",
                    "product_name": "string", 
                    "product_description": "string",
                    "target_audience": "string",
                    "campaign_goal": "string",
                    "product_niche": "fitness|tech|beauty|gaming|food|lifestyle|other",
                    "total_budget": number,
                    "budget_currency": "USD|EUR|INR",
                    "timeline": "string",
                    "campaign_start_date": "YYYY-MM-DD",
                    "campaign_end_date": "YYYY-MM-DD",
                    "deliverables": ["array", "of", "deliverables"],
                    "usage_rights": "string",
                    "creator_requirements": {{
                        "min_followers": number,
                        "max_followers": number,
                        "platforms": ["Instagram", "YouTube", "TikTok"],
                        "demographics": "string",
                        "location": "string",
                        "languages": ["English", "Hindi"]
                    }},
                    "content_guidelines": "string",
                    "brand_guidelines": "string",
                    "key_messages": ["array", "of", "key", "points"],
                    "hashtags": ["array", "of", "hashtags"],
                    "mention_requirements": "string",
                    "posting_schedule": "string",
                    "approval_process": "string",
                    "payment_terms": "string",
                    "contract_requirements": "string",
                    "performance_metrics": ["views", "engagement", "clicks"],
                    "reporting_requirements": "string",
                    "contact_person": "string",
                    "contact_email": "string",
                    "additional_notes": "string"
                }}
                
                Important:
                - Only extract clearly mentioned information
                - For budget, look for patterns like $10K, 10,000, "ten thousand dollars"
                - For dates, convert to YYYY-MM-DD format
                - For niche, map to one of the standard categories
                - Return empty fields as null, not empty strings
                """
            }
        }
    
    async def process_document(
        self, 
        file_content: bytes, 
        mime_type: str, 
        filename: str = "",
        document_type: str = "campaign_brief"
    ) -> Dict[str, Any]:
        """
        📄 Main document processing entry point
        """
        
        logger.info(f"📄 Processing document: {filename} ({mime_type})")
        
        try:
            # Validate format support
            if mime_type not in self.supported_formats:
                return {
                    "status": "error",
                    "error": f"Unsupported format: {mime_type}",
                    "supported_formats": list(self.supported_formats.values())
                }
            
            # Extract text content
            text_content = await self._extract_text_content(file_content, mime_type, filename)
            
            if not text_content:
                return {
                    "status": "error",
                    "error": "Could not extract text from document",
                    "troubleshooting": "Ensure document is not password protected or corrupted"
                }
            
            # Process with AI
            extracted_data = await self._ai_extract_campaign_data(text_content, document_type)
            
            # Validate and enhance extracted data
            validated_data = await self._validate_and_enhance_data(extracted_data, text_content)
            
            # Generate processing summary
            processing_summary = self._generate_processing_summary(validated_data, text_content)
            
            return {
                "status": "success",
                "extracted_data": validated_data,
                "processing_summary": processing_summary,
                "document_metadata": {
                    "filename": filename,
                    "mime_type": mime_type,
                    "format": self.supported_formats[mime_type],
                    "text_length": len(text_content),
                    "processed_at": datetime.now().isoformat(),
                    "extraction_confidence": self._calculate_extraction_confidence(validated_data)
                },
                "raw_text": text_content[:500] + "..." if len(text_content) > 500 else text_content
            }
            
        except Exception as e:
            logger.error(f"❌ Document processing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "filename": filename,
                "troubleshooting": [
                    "Check if document is corrupted",
                    "Ensure document is not password protected", 
                    "Try converting to PDF format",
                    "Verify file is not empty"
                ]
            }
    
    async def _extract_text_content(self, file_content: bytes, mime_type: str, filename: str) -> Optional[str]:
        """
        📝 Extract text content from different file formats
        """
        
        try:
            if mime_type == "application/pdf":
                return await self._extract_pdf_content(file_content)
            elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return await self._extract_docx_content(file_content)
            elif mime_type in ["text/plain", "text/markdown"]:
                return file_content.decode('utf-8')
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Text extraction failed for {filename}: {e}")
            return None
    
    async def _extract_pdf_content(self, pdf_content: bytes) -> Optional[str]:
        """Extract text from PDF"""
        
        if not PDF_AVAILABLE:
            logger.warning("⚠️  PDF processing libraries not available")
            return None
        
        try:
            # Try pdfplumber first (better for complex layouts)
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(pdf_content)
                temp_file.flush()
                
                try:
                    with pdfplumber.open(temp_file.name) as pdf:
                        text_parts = []
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text_parts.append(page_text)
                        
                        return "\n\n".join(text_parts) if text_parts else None
                        
                except Exception as e:
                    logger.warning(f"⚠️  pdfplumber failed, trying PyPDF2: {e}")
                    
                    # Fallback to PyPDF2
                    try:
                        with open(temp_file.name, 'rb') as pdf_file:
                            pdf_reader = PyPDF2.PdfReader(pdf_file)
                            text_parts = []
                            
                            for page in pdf_reader.pages:
                                page_text = page.extract_text()
                                if page_text:
                                    text_parts.append(page_text)
                            
                            return "\n\n".join(text_parts) if text_parts else None
                            
                    except Exception as e2:
                        logger.error(f"❌ Both PDF extraction methods failed: {e2}")
                        return None
                
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"❌ PDF processing failed: {e}")
            return None
    
    async def _extract_docx_content(self, docx_content: bytes) -> Optional[str]:
        """Extract text from DOCX"""
        
        if not DOCX_AVAILABLE:
            logger.warning("⚠️  DOCX processing library not available")
            return None
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                temp_file.write(docx_content)
                temp_file.flush()
                
                try:
                    with open(temp_file.name, 'rb') as docx_file:
                        result = mammoth.extract_raw_text(docx_file)
                        return result.value if result.value else None
                        
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"❌ DOCX processing failed: {e}")
            return None
    
    async def _ai_extract_campaign_data(self, text_content: str, document_type: str) -> Dict[str, Any]:
        """
        🧠 Use AI to extract structured campaign data
        """
        
        if not self.groq_client:
            return self._fallback_extraction(text_content)
        
        try:
            # Get extraction template
            template = self.extraction_templates.get(document_type, self.extraction_templates["campaign_brief"])
            
            # Prepare prompt
            prompt = template["prompt_template"].format(content=text_content[:4000])  # Limit to 4K chars
            
            # Get AI response
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                extracted_data = json.loads(result_text[json_start:json_end])
                
                # Clean up null values and validate
                cleaned_data = self._clean_extracted_data(extracted_data)
                
                logger.info(f"🧠 AI extraction successful: {len(cleaned_data)} fields extracted")
                return cleaned_data
            else:
                logger.warning("⚠️  No valid JSON in AI response, using fallback")
                return self._fallback_extraction(text_content)
                
        except Exception as e:
            logger.error(f"❌ AI extraction failed: {e}")
            return self._fallback_extraction(text_content)
    
    def _clean_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate extracted data"""
        
        cleaned = {}
        
        for key, value in data.items():
            # Skip null/empty values
            if value is None or value == "" or value == []:
                continue
            
            # Clean string values
            if isinstance(value, str):
                value = value.strip()
                if value:
                    cleaned[key] = value
            
            # Clean numeric values
            elif isinstance(value, (int, float)):
                if value > 0:
                    cleaned[key] = value
            
            # Clean lists
            elif isinstance(value, list):
                clean_list = [item for item in value if item and item.strip()]
                if clean_list:
                    cleaned[key] = clean_list
            
            # Clean objects
            elif isinstance(value, dict):
                clean_obj = self._clean_extracted_data(value)
                if clean_obj:
                    cleaned[key] = clean_obj
        
        return cleaned
    
    def _fallback_extraction(self, text_content: str) -> Dict[str, Any]:
        """Fallback extraction using regex patterns"""
        
        logger.info("🔧 Using fallback extraction (regex patterns)")
        
        extracted = {}
        text_lower = text_content.lower()
        
        # Extract budget
        budget_patterns = [
            r'budget[:\s]*\$?(\d{1,3}(?:,\d{3})*)',
            r'\$(\d{1,3}(?:,\d{3})*)',
            r'(\d+)k budget',
            r'total[:\s]*\$?(\d{1,3}(?:,\d{3})*)'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, text_lower)
            if match:
                budget_str = match.group(1).replace(',', '')
                if 'k' in pattern:
                    extracted["total_budget"] = int(budget_str) * 1000
                else:
                    extracted["total_budget"] = int(budget_str)
                break
        
        # Extract product/brand names (look for capitalized words)
        name_patterns = [
            r'product[:\s]*([A-Z][a-zA-Z\s]+)',
            r'brand[:\s]*([A-Z][a-zA-Z\s]+)',
            r'campaign[:\s]*([A-Z][a-zA-Z\s]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text_content)
            if match:
                name = match.group(1).strip()
                if 'product' in pattern:
                    extracted["product_name"] = name
                elif 'brand' in pattern:
                    extracted["brand_name"] = name
        
        # Extract niche
        niches = ["fitness", "tech", "beauty", "gaming", "food", "lifestyle", "fashion", "travel"]
        for niche in niches:
            if niche in text_lower:
                extracted["product_niche"] = niche
                break
        
        # Extract platforms
        platforms = ["instagram", "youtube", "tiktok", "twitter", "facebook"]
        mentioned_platforms = [p.title() for p in platforms if p in text_lower]
        if mentioned_platforms:
            if "creator_requirements" not in extracted:
                extracted["creator_requirements"] = {}
            extracted["creator_requirements"]["platforms"] = mentioned_platforms
        
        # Extract follower requirements
        follower_patterns = [
            r'(\d+)k?\+?\s*followers',
            r'minimum (\d+)k?\s*followers',
            r'over (\d+)k?\s*followers'
        ]
        
        for pattern in follower_patterns:
            match = re.search(pattern, text_lower)
            if match:
                followers = int(match.group(1))
                if 'k' in match.group(0):
                    followers *= 1000
                
                if "creator_requirements" not in extracted:
                    extracted["creator_requirements"] = {}
                extracted["creator_requirements"]["min_followers"] = followers
                break
        
        # Extract deliverables
        deliverable_keywords = ["video", "post", "story", "reel", "review", "unboxing", "tutorial"]
        found_deliverables = []
        
        for keyword in deliverable_keywords:
            if keyword in text_lower:
                if keyword == "video" and "review" in text_lower:
                    found_deliverables.append("video_review")
                elif keyword == "post":
                    found_deliverables.append("instagram_post")
                elif keyword == "story":
                    found_deliverables.append("instagram_story")
                else:
                    found_deliverables.append(keyword)
        
        if found_deliverables:
            extracted["deliverables"] = list(set(found_deliverables))
        
        logger.info(f"🔧 Fallback extraction completed: {len(extracted)} fields found")
        return extracted
    
    async def _validate_and_enhance_data(self, extracted_data: Dict[str, Any], text_content: str) -> Dict[str, Any]:
        """Validate and enhance extracted data"""
        
        enhanced_data = extracted_data.copy()
        
        # Validate and enhance budget
        if "total_budget" in enhanced_data:
            budget = enhanced_data["total_budget"]
            if budget < 100:
                logger.warning(f"⚠️  Suspiciously low budget: ${budget}")
            elif budget > 1000000:
                logger.warning(f"⚠️  Suspiciously high budget: ${budget}")
        
        # Enhance product niche if missing
        if "product_niche" not in enhanced_data:
            enhanced_data["product_niche"] = self._infer_niche_from_content(text_content)
        
        # Add default deliverables if missing
        if "deliverables" not in enhanced_data:
            enhanced_data["deliverables"] = ["video_review", "instagram_post"]
        
        # Set default timeline if missing
        if "timeline" not in enhanced_data:
            enhanced_data["timeline"] = "2 weeks"
        
        # Add campaign goal if missing
        if "campaign_goal" not in enhanced_data:
            enhanced_data["campaign_goal"] = "Increase brand awareness and drive sales"
        
        # Enhance creator requirements
        if "creator_requirements" not in enhanced_data:
            enhanced_data["creator_requirements"] = {}
        
        creator_reqs = enhanced_data["creator_requirements"]
        
        if "min_followers" not in creator_reqs:
            # Infer from budget
            budget = enhanced_data.get("total_budget", 10000)
            if budget > 20000:
                creator_reqs["min_followers"] = 100000
            elif budget > 10000:
                creator_reqs["min_followers"] = 50000
            else:
                creator_reqs["min_followers"] = 10000
        
        if "platforms" not in creator_reqs:
            creator_reqs["platforms"] = ["Instagram", "YouTube"]
        
        return enhanced_data
    
    def _infer_niche_from_content(self, text_content: str) -> str:
        """Infer product niche from content"""
        
        text_lower = text_content.lower()
        
        niche_keywords = {
            "fitness": ["fitness", "workout", "gym", "protein", "health", "exercise", "training"],
            "tech": ["technology", "app", "software", "device", "gadget", "digital", "smart"],
            "beauty": ["beauty", "makeup", "skincare", "cosmetics", "skin", "hair"],
            "gaming": ["game", "gaming", "esports", "console", "pc", "mobile game"],
            "food": ["food", "restaurant", "recipe", "cooking", "kitchen", "cuisine"],
            "lifestyle": ["lifestyle", "home", "decor", "fashion", "travel", "luxury"]
        }
        
        for niche, keywords in niche_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return niche
        
        return "lifestyle"  # Default
    
    def _calculate_extraction_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence score for extraction"""
        
        # Key fields that indicate good extraction
        key_fields = ["brand_name", "product_name", "total_budget", "product_niche"]
        present_key_fields = sum(1 for field in key_fields if field in extracted_data)
        
        # Total fields extracted
        total_fields = len(extracted_data)
        
        # Base confidence from key fields
        key_confidence = present_key_fields / len(key_fields)
        
        # Bonus for additional fields
        additional_confidence = min(total_fields / 15, 0.3)  # Max 30% bonus
        
        return min(key_confidence + additional_confidence, 1.0)
    
    def _generate_processing_summary(self, extracted_data: Dict[str, Any], text_content: str) -> Dict[str, Any]:
        """Generate processing summary"""
        
        return {
            "total_fields_extracted": len(extracted_data),
            "confidence_score": self._calculate_extraction_confidence(extracted_data),
            "key_fields_found": [
                field for field in ["brand_name", "product_name", "total_budget", "product_niche"]
                if field in extracted_data
            ],
            "missing_key_fields": [
                field for field in ["brand_name", "product_name", "total_budget", "product_niche"]
                if field not in extracted_data
            ],
            "document_length": len(text_content),
            "extraction_method": "ai_powered" if self.groq_client else "regex_fallback",
            "recommendations": self._generate_extraction_recommendations(extracted_data)
        }
    
    def _generate_extraction_recommendations(self, extracted_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving extraction"""
        
        recommendations = []
        
        if "brand_name" not in extracted_data:
            recommendations.append("Brand name not found - consider adding clear brand identification")
        
        if "total_budget" not in extracted_data:
            recommendations.append("Budget not specified - add budget information for better creator matching")
        
        if "creator_requirements" not in extracted_data or not extracted_data.get("creator_requirements"):
            recommendations.append("Creator requirements missing - specify follower count, platforms, demographics")
        
        if "deliverables" not in extracted_data:
            recommendations.append("Deliverables not specified - clarify what content creators should produce")
        
        if len(extracted_data) < 5:
            recommendations.append("Limited information extracted - consider providing more detailed brief")
        
        return recommendations

class BriefValidator:
    """
    ✅ BRIEF VALIDATOR - Validates and scores campaign briefs
    """
    
    @staticmethod
    def validate_campaign_brief(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate completeness and quality of campaign brief"""
        
        validation_result = {
            "is_valid": True,
            "completeness_score": 0.0,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "missing_fields": [],
            "field_quality": {}
        }
        
        # Required fields
        required_fields = {
            "brand_name": "Brand name is required",
            "product_name": "Product name is required", 
            "total_budget": "Budget is required for creator matching",
            "product_niche": "Product niche helps find relevant creators"
        }
        
        # Check required fields
        for field, error_msg in required_fields.items():
            if field not in extracted_data or not extracted_data[field]:
                validation_result["errors"].append(error_msg)
                validation_result["missing_fields"].append(field)
                validation_result["is_valid"] = False
        
        # Validate budget
        budget = extracted_data.get("total_budget")
        if budget:
            if budget < 500:
                validation_result["warnings"].append("Budget below $500 may limit creator options")
            elif budget > 100000:
                validation_result["warnings"].append("High budget - consider splitting into multiple campaigns")
            
            validation_result["field_quality"]["total_budget"] = "good"
        
        # Validate creator requirements
        creator_reqs = extracted_data.get("creator_requirements", {})
        if not creator_reqs:
            validation_result["suggestions"].append("Add creator requirements for better matching")
        else:
            if "min_followers" not in creator_reqs:
                validation_result["suggestions"].append("Specify minimum follower count")
            if "platforms" not in creator_reqs:
                validation_result["suggestions"].append("Specify preferred platforms")
        
        # Calculate completeness score
        total_possible_fields = 15  # Approximate
        present_fields = len(extracted_data)
        validation_result["completeness_score"] = min(present_fields / total_possible_fields, 1.0)
        
        return validation_result