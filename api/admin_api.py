# api/admin_api.py
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, status, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from services.admin_panel import AdminPanel, Permission, UserRole, get_current_user, require_permission
from services.creator_crm import CreatorCRM
from services.performance_tracker import PerformanceTracker
from services.payment_service import PaymentService, PaymentAnalytics

logger = logging.getLogger(__name__)

# Initialize services
admin_panel = AdminPanel()
creator_crm = CreatorCRM()
performance_tracker = PerformanceTracker()
payment_service = PaymentService()
payment_analytics = PaymentAnalytics(payment_service)

# API Router
admin_router = APIRouter()

# Pydantic models for API requests
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str
    role: str
    organization: Optional[str] = None

class UpdateUserRoleRequest(BaseModel):
    new_role: str

class CreateOrganizationRequest(BaseModel):
    name: str
    type: str  # "brand", "agency", "platform"
    plan: str = "basic"

class SystemSettingsUpdate(BaseModel):
    settings: Dict[str, Any]

class CreatorSearchRequest(BaseModel):
    filters: Dict[str, Any]
    sort_by: str = "performance_score"
    limit: int = 20

# ================================
# AUTHENTICATION ENDPOINTS
# ================================

@admin_router.post("/auth/login")
async def login(login_data: LoginRequest):
    """
    🔐 Admin login endpoint
    """
    
    try:
        result = await admin_panel.authenticate_user(
            login_data.email, 
            login_data.password
        )
        
        if result["status"] == "success":
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Login successful",
                    "access_token": result["access_token"],
                    "token_type": result["token_type"],
                    "expires_in": result["expires_in"],
                    "user": result["user"],
                    "session_id": result["session_id"],
                    "dashboard_url": "/api/admin/dashboard"
                }
            )
        else:
            return JSONResponse(
                status_code=401,
                content={
                    "error": result["error"],
                    "status": result["status"]
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Login endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/auth/verify-token")
async def verify_token(user: Dict[str, Any] = Depends(get_current_user)):
    """
    ✅ Verify token and get user info
    """
    
    return {
        "status": "valid",
        "user": user,
        "permissions": user.get("permissions", []),
        "verified_at": datetime.now().isoformat()
    }

@admin_router.post("/auth/logout")
async def logout(user: Dict[str, Any] = Depends(get_current_user)):
    """
    🚪 Logout and invalidate session
    """
    
    # In production, would invalidate the session/token
    return {
        "status": "success",
        "message": "Logged out successfully",
        "redirect_url": "/login"
    }

# ================================
# ADMIN DASHBOARD
# ================================

@admin_router.get("/dashboard")
async def get_admin_dashboard(user: Dict[str, Any] = Depends(get_current_user)):
    """
    📊 Get comprehensive admin dashboard
    """
    
    try:
        dashboard_data = await admin_panel.get_admin_dashboard(user)
        
        # Add additional dashboard components based on user role
        if admin_panel.check_permission(user, Permission.VIEW_ANALYTICS):
            # Add advanced analytics
            dashboard_data["advanced_analytics"] = await _get_advanced_analytics()
        
        if admin_panel.check_permission(user, Permission.VIEW_CREATORS):
            # Add creator insights
            dashboard_data["creator_insights"] = await _get_creator_dashboard_insights()
        
        if admin_panel.check_permission(user, Permission.VIEW_PAYMENTS):
            # Add payment insights
            dashboard_data["payment_insights"] = await _get_payment_dashboard_insights()
        
        return {
            "dashboard": dashboard_data,
            "user_context": {
                "role": user["role"],
                "permissions": user["permissions"],
                "organization": user.get("organization")
            },
            "navigation": _generate_navigation_menu(user),
            "quick_actions": _generate_quick_actions(user)
        }
        
    except Exception as e:
        logger.error(f"❌ Admin dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# USER MANAGEMENT
# ================================

@admin_router.post("/users")
async def create_user(
    user_data: CreateUserRequest,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.MANAGE_USERS))
):
    """
    👤 Create new user
    """
    
    try:
        result = await admin_panel.create_user(
            user_data.dict(),
            current_user["id"]
        )
        
        if result["status"] == "success":
            return JSONResponse(
                status_code=201,
                content={
                    "message": "User created successfully",
                    "user": result["user"],
                    "temporary_password": result["temporary_password"],
                    "next_steps": result["next_steps"]
                }
            )
        else:
            return JSONResponse(
                status_code=422,
                content={
                    "error": result["error"],
                    "status": result["status"]
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Create user failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/users")
async def get_users(
    role: Optional[str] = Query(None, description="Filter by role"),
    organization: Optional[str] = Query(None, description="Filter by organization"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: Dict[str, Any] = Depends(require_permission(Permission.MANAGE_USERS))
):
    """
    📋 Get users with filtering
    """
    
    try:
        filters = {}
        if role:
            filters["role"] = role
        if organization:
            filters["organization"] = organization
        if is_active is not None:
            filters["is_active"] = is_active
        
        result = await admin_panel.get_users(
            filters=filters,
            requesting_user=current_user["id"]
        )
        
        return {
            "users": result["users"],
            "total": result["total"],
            "filters": result["filters_applied"],
            "available_roles": result["roles_available"],
            "user_statistics": _calculate_user_statistics(result["users"])
        }
        
    except Exception as e:
        logger.error(f"❌ Get users failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_update: UpdateUserRoleRequest,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.MANAGE_USERS))
):
    """
    🔄 Update user role
    """
    
    try:
        result = await admin_panel.update_user_role(
            user_id,
            role_update.new_role,
            current_user["id"]
        )
        
        if result["status"] == "success":
            return {
                "message": "User role updated successfully",
                "user_id": result["user_id"],
                "role_change": {
                    "from": result["old_role"],
                    "to": result["new_role"]
                },
                "new_permissions": result["new_permissions"]
            }
        else:
            return JSONResponse(
                status_code=422,
                content={
                    "error": result["error"],
                    "status": result["status"]
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Update user role failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# CREATOR MANAGEMENT
# ================================

@admin_router.get("/creators")
async def get_creators(
    search: CreatorSearchRequest = Body(...),
    current_user: Dict[str, Any] = Depends(require_permission(Permission.VIEW_CREATORS))
):
    """
    👥 Advanced creator search and management
    """
    
    try:
        result = await creator_crm.search_creators(
            filters=search.filters,
            sort_by=search.sort_by,
            limit=search.limit
        )
        
        return {
            "creators": result["results"],
            "total_found": result["total_found"],
            "returned": result["returned"],
            "search_insights": result["search_insights"],
            "filters_applied": result["filters_applied"],
            "suggestions": result["suggestions"],
            "bulk_actions": _get_creator_bulk_actions(current_user)
        }
        
    except Exception as e:
        logger.error(f"❌ Creator search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/creators/{creator_id}")
async def get_creator_profile(
    creator_id: str,
    include_insights: bool = Query(True, description="Include AI insights"),
    current_user: Dict[str, Any] = Depends(require_permission(Permission.VIEW_CREATORS))
):
    """
    👤 Get detailed creator profile
    """
    
    try:
        result = await creator_crm.get_creator_profile(
            creator_id,
            include_insights=include_insights
        )
        
        if result["status"] == "found":
            return {
                "creator_profile": result["profile"],
                "recommendations": result["recommendations"],
                "available_actions": _get_creator_actions(current_user),
                "profile_completeness": result["profile"]["crm_metadata"]["data_completeness"]
            }
        else:
            raise HTTPException(status_code=404, detail="Creator not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get creator profile failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/creators")
async def add_creator(
    creator_data: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(require_permission(Permission.EDIT_CREATORS))
):
    """
    ➕ Add new creator to CRM
    """
    
    try:
        result = await creator_crm.add_creator(
            creator_data,
            source="admin_panel",
            verification_level="comprehensive"
        )
        
        if result["status"] == "success":
            return JSONResponse(
                status_code=201,
                content={
                    "message": "Creator added successfully",
                    "creator_id": result["creator_id"],
                    "insights": result["insights"],
                    "next_steps": result["next_steps"]
                }
            )
        else:
            return JSONResponse(
                status_code=422,
                content={
                    "error": result.get("errors", ["Unknown error"]),
                    "suggestions": result.get("suggestions", [])
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Add creator failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/creators/analytics")
async def get_creator_analytics(
    time_period: str = Query("30_days", description="Analytics time period"),
    current_user: Dict[str, Any] = Depends(require_permission(Permission.VIEW_ANALYTICS))
):
    """
    📈 Get creator analytics and insights
    """
    
    try:
        analytics = await creator_crm.get_crm_analytics(time_period)
        
        return {
            "creator_analytics": analytics,
            "insights": await _generate_creator_insights_summary(analytics),
            "recommendations": await _generate_creator_strategy_recommendations(analytics)
        }
        
    except Exception as e:
        logger.error(f"❌ Creator analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# CAMPAIGN MANAGEMENT
# ================================

@admin_router.get("/campaigns")
async def get_campaigns(
    status: Optional[str] = Query(None, description="Filter by status"),
    creator_id: Optional[str] = Query(None, description="Filter by creator"),
    date_from: Optional[str] = Query(None, description="Start date filter"),
    date_to: Optional[str] = Query(None, description="End date filter"),
    current_user: Dict[str, Any] = Depends(require_permission(Permission.VIEW_CAMPAIGN))
):
    """
    📋 Get campaigns with filtering and analytics
    """
    
    try:
        # Get campaigns from active campaigns (in production, would be from database)
        from main import active_campaigns
        
        campaigns_list = []
        for task_id, campaign_state in active_campaigns.items():
            campaign_info = {
                "task_id": task_id,
                "campaign_id": campaign_state.campaign_id,
                "brand_name": campaign_state.campaign_data.brand_name,
                "product_name": campaign_state.campaign_data.product_name,
                "status": campaign_state.current_stage,
                "budget": campaign_state.campaign_data.total_budget,
                "creators_count": len(campaign_state.discovered_influencers),
                "successful_negotiations": campaign_state.successful_negotiations,
                "total_cost": campaign_state.total_cost,
                "started_at": campaign_state.started_at.isoformat(),
                "completed_at": campaign_state.completed_at.isoformat() if campaign_state.completed_at else None
            }
            
            # Apply filters
            if status and campaign_info["status"] != status:
                continue
            
            campaigns_list.append(campaign_info)
        
        # Calculate campaign analytics
        campaign_analytics = _calculate_campaign_analytics(campaigns_list)
        
        return {
            "campaigns": campaigns_list,
            "total": len(campaigns_list),
            "analytics": campaign_analytics,
            "filters_applied": {
                "status": status,
                "creator_id": creator_id,
                "date_range": f"{date_from} to {date_to}" if date_from and date_to else None
            },
            "available_actions": _get_campaign_actions(current_user)
        }
        
    except Exception as e:
        logger.error(f"❌ Get campaigns failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/campaigns/{campaign_id}/performance")
async def get_campaign_performance(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.VIEW_ANALYTICS))
):
    """
    📊 Get detailed campaign performance analytics
    """
    
    try:
        # Check if campaign is being tracked
        if campaign_id in performance_tracker.tracked_campaigns:
            dashboard = await performance_tracker.get_campaign_performance_dashboard(campaign_id)
            
            return {
                "performance_dashboard": dashboard,
                "real_time_tracking": True,
                "recommendations": dashboard.get("recommendations", []),
                "export_options": dashboard.get("export_options", {})
            }
        else:
            # Get historical performance data
            return {
                "message": "Campaign not currently tracked",
                "real_time_tracking": False,
                "historical_data": await _get_historical_performance(campaign_id),
                "suggestion": "Start real-time tracking for detailed insights"
            }
            
    except Exception as e:
        logger.error(f"❌ Campaign performance failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# PAYMENT MANAGEMENT
# ================================

@admin_router.get("/payments")
async def get_payments(
    status: Optional[str] = Query(None, description="Filter by payment status"),
    creator_id: Optional[str] = Query(None, description="Filter by creator"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign"),
    current_user: Dict[str, Any] = Depends(require_permission(Permission.VIEW_PAYMENTS))
):
    """
    💰 Get payment records and analytics
    """
    
    try:
        # Get payment data
        payment_records = []
        
        for campaign_id_key, payment_plan in payment_service.payment_records.items():
            for creator_payment in payment_plan["creator_payments"]:
                payment_record = {
                    "campaign_id": campaign_id_key,
                    "creator_id": creator_payment["creator_id"],
                    "total_amount": creator_payment["total_amount"],
                    "currency": creator_payment["currency"],
                    "status": creator_payment["status"],
                    "milestones": creator_payment["milestones"],
                    "created_at": creator_payment["created_at"]
                }
                
                # Apply filters
                if status and payment_record["status"] != status:
                    continue
                if creator_id and payment_record["creator_id"] != creator_id:
                    continue
                if campaign_id and payment_record["campaign_id"] != campaign_id:
                    continue
                
                payment_records.append(payment_record)
        
        # Calculate payment analytics
        payment_analytics_data = _calculate_payment_analytics(payment_records)
        
        return {
            "payments": payment_records,
            "total": len(payment_records),
            "analytics": payment_analytics_data,
            "filters_applied": {
                "status": status,
                "creator_id": creator_id,
                "campaign_id": campaign_id
            },
            "available_actions": _get_payment_actions(current_user)
        }
        
    except Exception as e:
        logger.error(f"❌ Get payments failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/payments/{campaign_id}/trigger-milestone")
async def trigger_payment_milestone(
    campaign_id: str,
    creator_id: str = Body(...),
    milestone_trigger: str = Body(...),
    verification_data: Dict[str, Any] = Body({}),
    current_user: Dict[str, Any] = Depends(require_permission(Permission.PROCESS_PAYMENTS))
):
    """
    🎯 Trigger payment milestone
    """
    
    try:
        result = await payment_service.trigger_milestone_payment(
            campaign_id,
            creator_id,
            milestone_trigger,
            verification_data
        )
        
        if result["status"] == "processed":
            return {
                "message": "Payment milestone triggered successfully",
                "milestone": result["milestone"],
                "payment_result": result["payment_result"],
                "campaign_update": result["campaign_update"]
            }
        else:
            return JSONResponse(
                status_code=422,
                content={
                    "error": result["error"],
                    "status": result["status"]
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Trigger payment milestone failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# SYSTEM MANAGEMENT
# ================================

@admin_router.get("/system/settings")
async def get_system_settings(
    current_user: Dict[str, Any] = Depends(require_permission(Permission.SYSTEM_SETTINGS))
):
    """
    ⚙️ Get system settings
    """
    
    try:
        settings = await admin_panel.get_system_settings(current_user)
        
        return {
            "system_settings": settings,
            "user_permissions": current_user["permissions"],
            "editable_settings": _get_editable_settings(current_user)
        }
        
    except Exception as e:
        logger.error(f"❌ Get system settings failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.put("/system/settings")
async def update_system_settings(
    settings_update: SystemSettingsUpdate,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.SYSTEM_SETTINGS))
):
    """
    ⚙️ Update system settings
    """
    
    try:
        result = await admin_panel.update_system_settings(
            settings_update.settings,
            current_user["id"]
        )
        
        if result["status"] == "success":
            return {
                "message": result["message"],
                "updated_settings": result["updated_settings"]
            }
        else:
            return JSONResponse(
                status_code=422,
                content={
                    "error": result["error"],
                    "status": result["status"]
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Update system settings failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/system/health")
async def get_system_health(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🔍 Get system health and status
    """
    
    try:
        # Get comprehensive system health
        health_data = await admin_panel.get_data_health_report(current_user)
        
        # Add additional health metrics
        additional_metrics = {
            "ai_services_status": _check_ai_services_health(),
            "database_health": _check_database_health(),
            "api_performance": _check_api_performance(),
            "storage_status": _check_storage_status()
        }
        
        return {
            "system_health": health_data,
            "additional_metrics": additional_metrics,
            "recommendations": health_data.get("action_items", []),
            "last_check": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ System health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/system/audit-logs")
async def get_audit_logs(
    limit: int = Query(50, description="Number of logs to return"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    current_user: Dict[str, Any] = Depends(require_permission(Permission.VIEW_ANALYTICS))
):
    """
    📜 Get system audit logs
    """
    
    try:
        # Get audit logs from admin panel
        all_logs = admin_panel.audit_logs
        
        # Apply filters
        filtered_logs = []
        for log in all_logs:
            if event_type and log.get("type") != event_type:
                continue
            filtered_logs.append(log)
        
        # Sort by timestamp (most recent first)
        filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Limit results
        limited_logs = filtered_logs[:limit]
        
        return {
            "audit_logs": limited_logs,
            "total_logs": len(all_logs),
            "filtered_logs": len(filtered_logs),
            "returned": len(limited_logs),
            "filters": {
                "event_type": event_type,
                "limit": limit
            },
            "available_event_types": list(set(log.get("type") for log in all_logs))
        }
        
    except Exception as e:
        logger.error(f"❌ Get audit logs failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# DATA EXPORT AND REPORTING
# ================================

@admin_router.post("/export/{data_type}")
async def export_data(
    data_type: str,
    filters: Dict[str, Any] = Body({}),
    current_user: Dict[str, Any] = Depends(require_permission(Permission.EXPORT_DATA))
):
    """
    📤 Export system data
    """
    
    try:
        result = await admin_panel.export_data(
            data_type,
            filters,
            current_user
        )
        
        if result["status"] == "success":
            return {
                "message": "Data export initiated",
                "export_details": {
                    "export_id": result["export_id"],
                    "export_type": result["export_type"],
                    "records_count": result["records_count"],
                    "download_url": result["download_url"],
                    "expires_at": result["expires_at"]
                }
            }
        else:
            return JSONResponse(
                status_code=422,
                content={
                    "error": result["error"],
                    "status": result["status"]
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Data export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# HELPER FUNCTIONS
# ================================

async def _get_advanced_analytics() -> Dict[str, Any]:
    """Get advanced analytics for dashboard"""
    return {
        "campaign_success_rate": 78.5,
        "average_roi": 185.2,
        "creator_satisfaction": 4.6,
        "platform_growth": 23.1
    }

async def _get_creator_dashboard_insights() -> Dict[str, Any]:
    """Get creator insights for dashboard"""
    return {
        "total_creators": len(creator_crm.creator_database),
        "active_creators": len([c for c in creator_crm.creator_database.values() if c.availability.value == "excellent"]),
        "top_performing_creators": 3,
        "new_creators_this_month": 8
    }

async def _get_payment_dashboard_insights() -> Dict[str, Any]:
    """Get payment insights for dashboard"""
    return {
        "total_payments_processed": 127,
        "payment_success_rate": 98.4,
        "average_payment_time": "2.3 days",
        "outstanding_payments": 5
    }

def _generate_navigation_menu(user: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate navigation menu based on user permissions"""
    
    menu = [
        {"label": "Dashboard", "url": "/admin/dashboard", "icon": "dashboard"}
    ]
    
    if admin_panel.check_permission(user, Permission.VIEW_CAMPAIGN):
        menu.append({"label": "Campaigns", "url": "/admin/campaigns", "icon": "campaign"})
    
    if admin_panel.check_permission(user, Permission.VIEW_CREATORS):
        menu.append({"label": "Creators", "url": "/admin/creators", "icon": "users"})
    
    if admin_panel.check_permission(user, Permission.VIEW_PAYMENTS):
        menu.append({"label": "Payments", "url": "/admin/payments", "icon": "credit-card"})
    
    if admin_panel.check_permission(user, Permission.MANAGE_USERS):
        menu.append({"label": "Users", "url": "/admin/users", "icon": "user-check"})
    
    if admin_panel.check_permission(user, Permission.SYSTEM_SETTINGS):
        menu.append({"label": "Settings", "url": "/admin/settings", "icon": "settings"})
    
    return menu

def _generate_quick_actions(user: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate quick actions based on user permissions"""
    
    actions = []
    
    if admin_panel.check_permission(user, Permission.CREATE_CAMPAIGN):
        actions.append({
            "label": "Create Campaign",
            "url": "/admin/campaigns/create",
            "icon": "plus",
            "type": "primary"
        })
    
    if admin_panel.check_permission(user, Permission.EDIT_CREATORS):
        actions.append({
            "label": "Add Creator",
            "url": "/admin/creators/add",
            "icon": "user-plus",
            "type": "secondary"
        })
    
    if admin_panel.check_permission(user, Permission.MANAGE_USERS):
        actions.append({
            "label": "Invite User",
            "url": "/admin/users/invite",
            "icon": "mail",
            "type": "secondary"
        })
    
    return actions

def _calculate_user_statistics(users: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate user statistics"""
    
    total_users = len(users)
    active_users = len([u for u in users if u.get("is_active", False)])
    
    role_counts = {}
    for user in users:
        role = user.get("role", "unknown")
        role_counts[role] = role_counts.get(role, 0) + 1
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "activation_rate": (active_users / max(total_users, 1)) * 100,
        "role_distribution": role_counts
    }

def _get_creator_bulk_actions(user: Dict[str, Any]) -> List[str]:
    """Get available bulk actions for creators"""
    
    actions = []
    
    if admin_panel.check_permission(user, Permission.CONTACT_CREATORS):
        actions.append("send_message")
        actions.append("schedule_outreach")
    
    if admin_panel.check_permission(user, Permission.EDIT_CREATORS):
        actions.append("update_status")
        actions.append("bulk_edit")
    
    if admin_panel.check_permission(user, Permission.EXPORT_DATA):
        actions.append("export_selected")
    
    return actions

def _get_creator_actions(user: Dict[str, Any]) -> List[str]:
    """Get available actions for individual creator"""
    
    actions = ["view_profile"]
    
    if admin_panel.check_permission(user, Permission.CONTACT_CREATORS):
        actions.extend(["send_message", "schedule_call"])
    
    if admin_panel.check_permission(user, Permission.EDIT_CREATORS):
        actions.extend(["edit_profile", "update_status"])
    
    return actions

def _calculate_campaign_analytics(campaigns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate campaign analytics"""
    
    total_campaigns = len(campaigns)
    completed_campaigns = len([c for c in campaigns if c["completed_at"]])
    total_budget = sum(c["budget"] for c in campaigns)
    total_spent = sum(c["total_cost"] for c in campaigns)
    
    return {
        "total_campaigns": total_campaigns,
        "completed_campaigns": completed_campaigns,
        "active_campaigns": total_campaigns - completed_campaigns,
        "completion_rate": (completed_campaigns / max(total_campaigns, 1)) * 100,
        "total_budget": total_budget,
        "total_spent": total_spent,
        "budget_utilization": (total_spent / max(total_budget, 1)) * 100,
        "average_campaign_budget": total_budget / max(total_campaigns, 1)
    }

def _get_campaign_actions(user: Dict[str, Any]) -> List[str]:
    """Get available campaign actions"""
    
    actions = ["view_details"]
    
    if admin_panel.check_permission(user, Permission.EDIT_CAMPAIGN):
        actions.extend(["edit_campaign", "pause_campaign"])
    
    if admin_panel.check_permission(user, Permission.VIEW_ANALYTICS):
        actions.append("view_analytics")
    
    return actions

def _calculate_payment_analytics(payments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate payment analytics"""
    
    total_payments = len(payments)
    total_amount = sum(p["total_amount"] for p in payments)
    
    status_counts = {}
    for payment in payments:
        status = payment["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "total_payments": total_payments,
        "total_amount": total_amount,
        "average_payment": total_amount / max(total_payments, 1),
        "status_distribution": status_counts
    }

def _get_payment_actions(user: Dict[str, Any]) -> List[str]:
    """Get available payment actions"""
    
    actions = ["view_details"]
    
    if admin_panel.check_permission(user, Permission.PROCESS_PAYMENTS):
        actions.extend(["trigger_payment", "refund_payment"])
    
    if admin_panel.check_permission(user, Permission.EXPORT_DATA):
        actions.append("export_records")
    
    return actions

def _get_editable_settings(user: Dict[str, Any]) -> List[str]:
    """Get editable settings based on user permissions"""
    
    editable = []
    
    if admin_panel.check_permission(user, Permission.SYSTEM_SETTINGS):
        editable.extend([
            "platform_settings",
            "security_settings", 
            "ai_settings",
            "payment_settings"
        ])
    
    return editable

# Mock health check functions
def _check_ai_services_health() -> Dict[str, Any]:
    """Check AI services health"""
    return {
        "groq_api": "operational",
        "elevenlabs_api": "operational", 
        "performance_tracker": "operational",
        "document_processor": "operational"
    }

def _check_database_health() -> Dict[str, Any]:
    """Check database health"""
    return {
        "connection_status": "healthy",
        "query_performance": "good",
        "storage_usage": "23%",
        "backup_status": "current"
    }

def _check_api_performance() -> Dict[str, Any]:
    """Check API performance"""
    return {
        "average_response_time": "180ms",
        "error_rate": "0.2%",
        "requests_per_minute": 145,
        "cache_hit_rate": "87%"
    }

def _check_storage_status() -> Dict[str, Any]:
    """Check storage status"""
    return {
        "disk_usage": "45%",
        "available_space": "2.1TB",
        "backup_storage": "healthy",
        "cdn_status": "operational"
    }

async def _get_historical_performance(campaign_id: str) -> Dict[str, Any]:
    """Get historical performance data"""
    return {
        "message": "Historical performance data would be retrieved from database",
        "available": False
    }

async def _generate_creator_insights_summary(analytics: Dict[str, Any]) -> List[str]:
    """Generate creator insights summary"""
    return [
        "Creator engagement rates are trending upward",
        "Micro-influencers showing strongest ROI",
        "Fitness niche showing highest growth potential"
    ]

async def _generate_creator_strategy_recommendations(analytics: Dict[str, Any]) -> List[str]:
    """Generate creator strategy recommendations"""
    return [
        "Focus recruitment on micro-influencers (10K-100K followers)",
        "Expand into emerging platforms like TikTok",
        "Implement automated onboarding for new creators"
    ]