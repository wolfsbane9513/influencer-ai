# services/admin_panel.py
import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib
import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config.settings import settings

logger = logging.getLogger(__name__)

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    BRAND_MANAGER = "brand_manager"
    AGENCY_MANAGER = "agency_manager"
    CREATOR_MANAGER = "creator_manager"
    CREATOR = "creator"
    CLIENT = "client"
    VIEWER = "viewer"

class Permission(str, Enum):
    # Campaign permissions
    CREATE_CAMPAIGN = "create_campaign"
    VIEW_CAMPAIGN = "view_campaign"
    EDIT_CAMPAIGN = "edit_campaign"
    DELETE_CAMPAIGN = "delete_campaign"
    APPROVE_CAMPAIGN = "approve_campaign"
    
    # Creator permissions
    VIEW_CREATORS = "view_creators"
    EDIT_CREATORS = "edit_creators"
    DELETE_CREATORS = "delete_creators"
    CONTACT_CREATORS = "contact_creators"
    
    # Financial permissions
    VIEW_PAYMENTS = "view_payments"
    PROCESS_PAYMENTS = "process_payments"
    VIEW_FINANCIAL_REPORTS = "view_financial_reports"
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    SYSTEM_SETTINGS = "system_settings"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"

@dataclass
class User:
    id: str
    email: str
    name: str
    role: UserRole
    organization: Optional[str]
    permissions: List[Permission]
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool
    metadata: Dict[str, Any]

@dataclass
class Organization:
    id: str
    name: str
    type: str  # "brand", "agency", "platform"
    plan: str  # "basic", "pro", "enterprise"
    users: List[str]
    settings: Dict[str, Any]
    created_at: datetime

class AdminPanel:
    """
    👑 ADMIN PANEL - Role-Based Management System
    
    Features:
    - Role-based access control (RBAC)
    - User and organization management
    - Permission system
    - Activity monitoring and audit logs
    - System settings and configuration
    - Data health monitoring
    - Performance analytics dashboard
    - Automated alerts and notifications
    """
    
    def __init__(self):
        # User and organization databases (in-memory for demo)
        self.users = {}
        self.organizations = {}
        self.sessions = {}
        self.audit_logs = []
        
        # Security configuration
        self.security_config = {
            "jwt_secret": getattr(settings, 'jwt_secret', 'your-secret-key'),
            "token_expire_hours": 24,
            "max_login_attempts": 5,
            "session_timeout_hours": 8
        }
        
        # Role-permission mapping
        self.role_permissions = self._initialize_role_permissions()
        
        # System monitoring
        self.system_metrics = {
            "active_campaigns": 0,
            "total_users": 0,
            "api_requests_today": 0,
            "error_rate": 0.0,
            "uptime": "99.9%"
        }
        
        # Initialize default admin user
        self._create_default_admin()
        
        logger.info("👑 Admin Panel initialized with role-based access control")
    
    def _initialize_role_permissions(self) -> Dict[UserRole, List[Permission]]:
        """Initialize role-permission mapping"""
        
        return {
            UserRole.SUPER_ADMIN: list(Permission),  # All permissions
            
            UserRole.ADMIN: [
                Permission.CREATE_CAMPAIGN, Permission.VIEW_CAMPAIGN, Permission.EDIT_CAMPAIGN,
                Permission.APPROVE_CAMPAIGN, Permission.VIEW_CREATORS, Permission.EDIT_CREATORS,
                Permission.CONTACT_CREATORS, Permission.VIEW_PAYMENTS, Permission.PROCESS_PAYMENTS,
                Permission.VIEW_FINANCIAL_REPORTS, Permission.MANAGE_USERS, Permission.VIEW_ANALYTICS,
                Permission.EXPORT_DATA
            ],
            
            UserRole.BRAND_MANAGER: [
                Permission.CREATE_CAMPAIGN, Permission.VIEW_CAMPAIGN, Permission.EDIT_CAMPAIGN,
                Permission.VIEW_CREATORS, Permission.CONTACT_CREATORS, Permission.VIEW_PAYMENTS,
                Permission.VIEW_ANALYTICS
            ],
            
            UserRole.AGENCY_MANAGER: [
                Permission.CREATE_CAMPAIGN, Permission.VIEW_CAMPAIGN, Permission.EDIT_CAMPAIGN,
                Permission.VIEW_CREATORS, Permission.EDIT_CREATORS, Permission.CONTACT_CREATORS,
                Permission.VIEW_PAYMENTS, Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA
            ],
            
            UserRole.CREATOR_MANAGER: [
                Permission.VIEW_CREATORS, Permission.EDIT_CREATORS, Permission.CONTACT_CREATORS,
                Permission.VIEW_CAMPAIGN, Permission.VIEW_ANALYTICS
            ],
            
            UserRole.CREATOR: [
                Permission.VIEW_CAMPAIGN, Permission.VIEW_PAYMENTS
            ],
            
            UserRole.CLIENT: [
                Permission.VIEW_CAMPAIGN, Permission.VIEW_ANALYTICS
            ],
            
            UserRole.VIEWER: [
                Permission.VIEW_CAMPAIGN, Permission.VIEW_CREATORS
            ]
        }
    
    def _create_default_admin(self):
        """Create default admin user for system initialization"""
        
        admin_user = User(
            id="admin_001",
            email="admin@influencerflow.ai",
            name="System Administrator",
            role=UserRole.SUPER_ADMIN,
            organization=None,
            permissions=self.role_permissions[UserRole.SUPER_ADMIN],
            created_at=datetime.now(),
            last_login=None,
            is_active=True,
            metadata={
                "created_by": "system",
                "is_default": True,
                "login_attempts": 0
            }
        )
        
        self.users[admin_user.id] = admin_user
        logger.info("👑 Default admin user created")
    
    # Authentication and Authorization
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        🔐 Authenticate user and generate access token
        """
        
        try:
            # Find user by email
            user = None
            for u in self.users.values():
                if u.email.lower() == email.lower():
                    user = u
                    break
            
            if not user:
                self._log_security_event("login_failed", {"email": email, "reason": "user_not_found"})
                return {"status": "failed", "error": "Invalid credentials"}
            
            if not user.is_active:
                self._log_security_event("login_failed", {"email": email, "reason": "user_inactive"})
                return {"status": "failed", "error": "Account is inactive"}
            
            # Check login attempts (simple rate limiting)
            if user.metadata.get("login_attempts", 0) >= self.security_config["max_login_attempts"]:
                return {"status": "failed", "error": "Too many login attempts. Please try again later."}
            
            # Mock password verification (in production, use proper hashing)
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            expected_hash = user.metadata.get("password_hash", "default_hash")
            
            if password_hash != expected_hash and password != "admin123":  # Demo password
                user.metadata["login_attempts"] = user.metadata.get("login_attempts", 0) + 1
                self._log_security_event("login_failed", {"email": email, "reason": "invalid_password"})
                return {"status": "failed", "error": "Invalid credentials"}
            
            # Generate JWT token
            token_payload = {
                "user_id": user.id,
                "email": user.email,
                "role": user.role.value,
                "permissions": [p.value for p in user.permissions],
                "exp": datetime.utcnow() + timedelta(hours=self.security_config["token_expire_hours"])
            }
            
            access_token = jwt.encode(
                token_payload,
                self.security_config["jwt_secret"],
                algorithm="HS256"
            )
            
            # Update user login info
            user.last_login = datetime.now()
            user.metadata["login_attempts"] = 0
            
            # Create session
            session_id = f"session_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.sessions[session_id] = {
                "user_id": user.id,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "ip_address": "127.0.0.1",  # Would be actual IP
                "user_agent": "demo_client"
            }
            
            self._log_security_event("login_success", {"user_id": user.id, "email": email})
            
            return {
                "status": "success",
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": self.security_config["token_expire_hours"] * 3600,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role.value,
                    "permissions": [p.value for p in user.permissions],
                    "organization": user.organization
                },
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        🔍 Verify JWT token and return user info
        """
        
        try:
            payload = jwt.decode(
                token,
                self.security_config["jwt_secret"],
                algorithms=["HS256"]
            )
            
            user_id = payload.get("user_id")
            user = self.users.get(user_id)
            
            if not user or not user.is_active:
                return {"status": "invalid", "error": "User not found or inactive"}
            
            return {
                "status": "valid",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role.value,
                    "permissions": [p.value for p in user.permissions],
                    "organization": user.organization
                }
            }
            
        except jwt.ExpiredSignatureError:
            return {"status": "expired", "error": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"status": "invalid", "error": "Invalid token"}
        except Exception as e:
            logger.error(f"❌ Token verification failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def check_permission(self, user: Dict[str, Any], required_permission: Permission) -> bool:
        """
        ✅ Check if user has required permission
        """
        
        user_permissions = user.get("permissions", [])
        return required_permission.value in user_permissions
    
    # User Management
    
    async def create_user(
        self,
        user_data: Dict[str, Any],
        created_by: str
    ) -> Dict[str, Any]:
        """
        👤 Create new user with role assignment
        """
        
        try:
            # Validate user data
            required_fields = ["email", "name", "role"]
            for field in required_fields:
                if field not in user_data:
                    return {"status": "error", "error": f"Missing required field: {field}"}
            
            # Check if email already exists
            for existing_user in self.users.values():
                if existing_user.email.lower() == user_data["email"].lower():
                    return {"status": "error", "error": "Email already exists"}
            
            # Validate role
            try:
                role = UserRole(user_data["role"])
            except ValueError:
                return {"status": "error", "error": "Invalid role"}
            
            # Generate user ID
            user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create user
            new_user = User(
                id=user_id,
                email=user_data["email"],
                name=user_data["name"],
                role=role,
                organization=user_data.get("organization"),
                permissions=self.role_permissions[role],
                created_at=datetime.now(),
                last_login=None,
                is_active=True,
                metadata={
                    "created_by": created_by,
                    "login_attempts": 0,
                    "password_hash": hashlib.sha256("temppass123".encode()).hexdigest()  # Demo
                }
            )
            
            # Store user
            self.users[user_id] = new_user
            
            self._log_admin_activity("user_created", created_by, {
                "user_id": user_id,
                "email": user_data["email"],
                "role": role.value
            })
            
            logger.info(f"👤 User created: {user_data['email']} ({role.value})")
            
            return {
                "status": "success",
                "user_id": user_id,
                "user": asdict(new_user),
                "temporary_password": "temppass123",
                "next_steps": [
                    "User should log in and change password",
                    "Assign to organization if needed",
                    "Configure additional permissions if required"
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ User creation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_users(
        self,
        filters: Dict[str, Any] = None,
        requesting_user: str = None
    ) -> Dict[str, Any]:
        """
        📋 Get users with optional filtering
        """
        
        try:
            users_list = []
            
            for user in self.users.values():
                # Apply filters
                if filters:
                    if "role" in filters and user.role.value != filters["role"]:
                        continue
                    if "organization" in filters and user.organization != filters["organization"]:
                        continue
                    if "is_active" in filters and user.is_active != filters["is_active"]:
                        continue
                
                # Convert to dict and remove sensitive info
                user_dict = asdict(user)
                user_dict.pop("metadata", None)  # Remove metadata for security
                users_list.append(user_dict)
            
            return {
                "status": "success",
                "users": users_list,
                "total": len(users_list),
                "filters_applied": filters or {},
                "roles_available": [role.value for role in UserRole]
            }
            
        except Exception as e:
            logger.error(f"❌ Get users failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def update_user_role(
        self,
        user_id: str,
        new_role: str,
        updated_by: str
    ) -> Dict[str, Any]:
        """
        🔄 Update user role and permissions
        """
        
        try:
            if user_id not in self.users:
                return {"status": "error", "error": "User not found"}
            
            try:
                role = UserRole(new_role)
            except ValueError:
                return {"status": "error", "error": "Invalid role"}
            
            user = self.users[user_id]
            old_role = user.role
            
            # Update role and permissions
            user.role = role
            user.permissions = self.role_permissions[role]
            
            self._log_admin_activity("user_role_updated", updated_by, {
                "user_id": user_id,
                "old_role": old_role.value,
                "new_role": role.value
            })
            
            logger.info(f"🔄 User role updated: {user.email} from {old_role.value} to {role.value}")
            
            return {
                "status": "success",
                "user_id": user_id,
                "old_role": old_role.value,
                "new_role": role.value,
                "new_permissions": [p.value for p in user.permissions]
            }
            
        except Exception as e:
            logger.error(f"❌ User role update failed: {e}")
            return {"status": "error", "error": str(e)}
    
    # Organization Management
    
    async def create_organization(
        self,
        org_data: Dict[str, Any],
        created_by: str
    ) -> Dict[str, Any]:
        """
        🏢 Create new organization
        """
        
        try:
            required_fields = ["name", "type"]
            for field in required_fields:
                if field not in org_data:
                    return {"status": "error", "error": f"Missing required field: {field}"}
            
            org_id = f"org_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            organization = Organization(
                id=org_id,
                name=org_data["name"],
                type=org_data["type"],
                plan=org_data.get("plan", "basic"),
                users=[],
                settings={
                    "api_rate_limit": 1000,
                    "max_campaigns": 10,
                    "max_users": 5
                },
                created_at=datetime.now()
            )
            
            self.organizations[org_id] = organization
            
            self._log_admin_activity("organization_created", created_by, {
                "org_id": org_id,
                "name": org_data["name"],
                "type": org_data["type"]
            })
            
            return {
                "status": "success",
                "organization_id": org_id,
                "organization": asdict(organization)
            }
            
        except Exception as e:
            logger.error(f"❌ Organization creation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    # System Monitoring and Analytics
    
    async def get_admin_dashboard(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        📊 Get admin dashboard with system overview
        """
        
        try:
            # System overview
            system_overview = {
                "platform_status": "operational",
                "active_users": len([u for u in self.users.values() if u.is_active]),
                "total_organizations": len(self.organizations),
                "active_campaigns": self.system_metrics["active_campaigns"],
                "api_requests_today": self.system_metrics["api_requests_today"],
                "system_uptime": self.system_metrics["uptime"],
                "error_rate": self.system_metrics["error_rate"]
            }
            
            # User analytics
            user_analytics = await self._get_user_analytics()
            
            # Campaign analytics
            campaign_analytics = await self._get_campaign_analytics()
            
            # System health
            system_health = await self._get_system_health()
            
            # Recent activity
            recent_activity = self._get_recent_activity(limit=10)
            
            # Alerts and notifications
            alerts = await self._get_system_alerts()
            
            return {
                "dashboard_data": {
                    "system_overview": system_overview,
                    "user_analytics": user_analytics,
                    "campaign_analytics": campaign_analytics,
                    "system_health": system_health,
                    "recent_activity": recent_activity,
                    "alerts": alerts
                },
                "user_permissions": user.get("permissions", []),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Admin dashboard failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_system_settings(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        ⚙️ Get system settings and configuration
        """
        
        if not self.check_permission(user, Permission.SYSTEM_SETTINGS):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        return {
            "platform_settings": {
                "platform_name": "InfluencerFlow AI",
                "version": "3.0.0-ai-native",
                "maintenance_mode": False,
                "registration_enabled": True,
                "api_rate_limiting": True,
                "email_notifications": True
            },
            "ai_settings": {
                "groq_integration": bool(settings.groq_api_key),
                "elevenlabs_integration": bool(settings.elevenlabs_api_key),
                "ai_features_enabled": True,
                "performance_tracking": True
            },
            "security_settings": {
                "session_timeout_hours": self.security_config["session_timeout_hours"],
                "max_login_attempts": self.security_config["max_login_attempts"],
                "password_policy": "8+ characters required",
                "two_factor_auth": False
            },
            "payment_settings": {
                "auto_payments": True,
                "supported_currencies": ["USD", "INR", "EUR"],
                "payment_providers": ["Stripe", "Razorpay"]
            }
        }
    
    async def update_system_settings(
        self,
        settings_update: Dict[str, Any],
        updated_by: str
    ) -> Dict[str, Any]:
        """
        ⚙️ Update system settings
        """
        
        try:
            # Validate and apply settings updates
            updated_settings = {}
            
            for category, settings_data in settings_update.items():
                if category == "security_settings":
                    # Update security configuration
                    if "session_timeout_hours" in settings_data:
                        self.security_config["session_timeout_hours"] = settings_data["session_timeout_hours"]
                        updated_settings["session_timeout_hours"] = settings_data["session_timeout_hours"]
                
                # Add more setting categories as needed
            
            self._log_admin_activity("system_settings_updated", updated_by, {
                "updated_settings": updated_settings
            })
            
            return {
                "status": "success",
                "updated_settings": updated_settings,
                "message": "System settings updated successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ System settings update failed: {e}")
            return {"status": "error", "error": str(e)}
    
    # Data Management and Health
    
    async def get_data_health_report(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔍 Get comprehensive data health report
        """
        
        try:
            # Creator data health
            creator_health = await self._analyze_creator_data_health()
            
            # Campaign data health
            campaign_health = await self._analyze_campaign_data_health()
            
            # System data health
            system_health = await self._analyze_system_data_health()
            
            # Generate recommendations
            recommendations = await self._generate_data_health_recommendations(
                creator_health, campaign_health, system_health
            )
            
            return {
                "data_health_report": {
                    "overall_score": 85.5,  # Mock score
                    "creator_data": creator_health,
                    "campaign_data": campaign_health,
                    "system_data": system_health,
                    "recommendations": recommendations,
                    "last_analysis": datetime.now().isoformat()
                },
                "action_items": [
                    "Review incomplete creator profiles",
                    "Update stale campaign data",
                    "Optimize database performance"
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Data health report failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def export_data(
        self,
        export_type: str,
        filters: Dict[str, Any],
        user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        📤 Export system data with filtering
        """
        
        if not self.check_permission(user, Permission.EXPORT_DATA):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        try:
            export_data = {}
            
            if export_type == "users":
                export_data = await self._export_users_data(filters)
            elif export_type == "campaigns":
                export_data = await self._export_campaigns_data(filters)
            elif export_type == "creators":
                export_data = await self._export_creators_data(filters)
            elif export_type == "analytics":
                export_data = await self._export_analytics_data(filters)
            
            # Generate export file (mock)
            export_id = f"export_{export_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self._log_admin_activity("data_exported", user["id"], {
                "export_type": export_type,
                "export_id": export_id,
                "filters": filters
            })
            
            return {
                "status": "success",
                "export_id": export_id,
                "export_type": export_type,
                "records_count": len(export_data),
                "download_url": f"/api/admin/exports/{export_id}/download",
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Data export failed: {e}")
            return {"status": "error", "error": str(e)}
    
    # Utility methods
    
    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events"""
        
        self.audit_logs.append({
            "timestamp": datetime.now().isoformat(),
            "type": "security",
            "event": event_type,
            "details": details,
            "severity": "high" if "failed" in event_type else "low"
        })
    
    def _log_admin_activity(self, activity: str, user_id: str, details: Dict[str, Any]):
        """Log admin activities"""
        
        self.audit_logs.append({
            "timestamp": datetime.now().isoformat(),
            "type": "admin_activity",
            "activity": activity,
            "user_id": user_id,
            "details": details
        })
    
    async def _get_user_analytics(self) -> Dict[str, Any]:
        """Get user analytics"""
        
        total_users = len(self.users)
        active_users = len([u for u in self.users.values() if u.is_active])
        
        role_distribution = {}
        for user in self.users.values():
            role = user.role.value
            role_distribution[role] = role_distribution.get(role, 0) + 1
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "role_distribution": role_distribution,
            "new_users_this_month": 3,  # Mock data
            "login_rate": 85.2  # Mock data
        }
    
    async def _get_campaign_analytics(self) -> Dict[str, Any]:
        """Get campaign analytics"""
        
        # Mock campaign analytics
        return {
            "total_campaigns": 47,
            "active_campaigns": 12,
            "completed_campaigns": 35,
            "success_rate": 78.5,
            "average_budget": 8500.0,
            "total_revenue": 125000.0
        }
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        
        return {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 23.1,
            "api_response_time": 180,  # ms
            "database_status": "healthy",
            "ai_services_status": "operational"
        }
    
    def _get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent system activity"""
        
        # Return recent audit logs
        return sorted(self.audit_logs, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    async def _get_system_alerts(self) -> List[Dict[str, Any]]:
        """Get system alerts and notifications"""
        
        alerts = []
        
        # Check for various alert conditions
        if self.system_metrics["error_rate"] > 5.0:
            alerts.append({
                "type": "error_rate",
                "severity": "high",
                "message": f"Error rate is {self.system_metrics['error_rate']}%",
                "action": "Investigate error sources"
            })
        
        # Mock additional alerts
        alerts.extend([
            {
                "type": "maintenance",
                "severity": "low",
                "message": "Scheduled maintenance in 48 hours",
                "action": "Notify users of upcoming maintenance"
            }
        ])
        
        return alerts
    
    # Mock data analysis methods
    
    async def _analyze_creator_data_health(self) -> Dict[str, Any]:
        """Analyze creator data health"""
        return {
            "total_creators": 150,
            "complete_profiles": 142,
            "missing_data_creators": 8,
            "stale_profiles": 12,
            "data_quality_score": 89.5
        }
    
    async def _analyze_campaign_data_health(self) -> Dict[str, Any]:
        """Analyze campaign data health"""
        return {
            "total_campaigns": 47,
            "complete_campaigns": 44,
            "incomplete_campaigns": 3,
            "data_quality_score": 91.2
        }
    
    async def _analyze_system_data_health(self) -> Dict[str, Any]:
        """Analyze system data health"""
        return {
            "database_size": "2.4 GB",
            "orphaned_records": 3,
            "data_consistency": 98.7,
            "backup_status": "current"
        }
    
    async def _generate_data_health_recommendations(self, *args) -> List[str]:
        """Generate data health recommendations"""
        return [
            "Complete missing creator profile data",
            "Archive old campaign records",
            "Update stale creator performance metrics"
        ]
    
    # Export methods (mock implementations)
    
    async def _export_users_data(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Export users data"""
        return [asdict(user) for user in self.users.values()]
    
    async def _export_campaigns_data(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Export campaigns data"""
        return []  # Mock
    
    async def _export_creators_data(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Export creators data"""
        return []  # Mock
    
    async def _export_analytics_data(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Export analytics data"""
        return []  # Mock

# Authentication dependency for FastAPI
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    🔐 FastAPI dependency to get current authenticated user
    """
    
    admin_panel = AdminPanel()  # In production, this would be injected
    
    token = credentials.credentials
    verification_result = await admin_panel.verify_token(token)
    
    if verification_result["status"] != "valid":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=verification_result.get("error", "Invalid authentication credentials"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return verification_result["user"]

async def require_permission(permission: Permission):
    """
    🔒 FastAPI dependency to require specific permission
    """
    
    def permission_checker(user: Dict[str, Any] = Depends(get_current_user)):
        admin_panel = AdminPanel()
        
        if not admin_panel.check_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission.value}"
            )
        
        return user
    
    return permission_checker