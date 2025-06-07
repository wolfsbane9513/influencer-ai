# models/workflow.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ================================
# WORKFLOW ENUMS
# ================================

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
    ESCALATED = "escalated"

class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"

# ================================
# CORE WORKFLOW MODELS
# ================================

class WorkflowStep(BaseModel):
    """Individual step in a workflow"""
    step_id: str
    step_name: str
    step_type: str  # data_collection, negotiation, approval, etc.
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration_minutes: int = 30
    actual_duration_minutes: Optional[int] = None
    assigned_to: Optional[str] = None  # User ID or system
    dependencies: List[str] = []  # Step IDs this step depends on
    outputs: Dict[str, Any] = {}  # Step outputs
    metadata: Dict[str, Any] = {}  # Additional step data

class WorkflowTemplate(BaseModel):
    """Template for creating workflows"""
    template_id: str
    template_name: str
    description: str
    category: str  # campaign, approval, contract, etc.
    steps: List[WorkflowStep]
    estimated_total_duration_minutes: int
    required_approvals: List[str] = []
    notification_settings: Dict[str, Any] = {}
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

class WorkflowInstance(BaseModel):
    """Active workflow instance"""
    workflow_id: str
    template_id: str
    workflow_name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    priority: WorkflowPriority = WorkflowPriority.MEDIUM
    
    # Context
    campaign_id: Optional[str] = None
    creator_id: Optional[str] = None
    initiated_by: str  # User ID
    assigned_to: Optional[str] = None
    
    # Progress tracking
    current_step_id: Optional[str] = None
    completed_steps: List[str] = []
    progress_percentage: float = 0.0
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.now)
    estimated_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    
    # Steps and data
    steps: List[WorkflowStep] = []
    workflow_data: Dict[str, Any] = {}  # Shared data across steps
    
    # Notifications and approvals
    pending_approvals: List[str] = []
    completed_approvals: List[str] = []
    notifications_sent: List[str] = []
    
    def get_current_step(self) -> Optional[WorkflowStep]:
        """Get current active step"""
        if self.current_step_id:
            for step in self.steps:
                if step.step_id == self.current_step_id:
                    return step
        return None
    
    def get_next_step(self) -> Optional[WorkflowStep]:
        """Get next step to execute"""
        for step in self.steps:
            if step.status == WorkflowStatus.PENDING:
                # Check if dependencies are met
                if all(dep_id in self.completed_steps for dep_id in step.dependencies):
                    return step
        return None
    
    def mark_step_completed(self, step_id: str, outputs: Optional[Dict[str, Any]] = None):
        """Mark a step as completed"""
        for step in self.steps:
            if step.step_id == step_id:
                step.status = WorkflowStatus.COMPLETED
                step.completed_at = datetime.now()
                if step.started_at:
                    step.actual_duration_minutes = int((step.completed_at - step.started_at).total_seconds() / 60)
                if outputs:
                    step.outputs.update(outputs)
                
                if step_id not in self.completed_steps:
                    self.completed_steps.append(step_id)
                
                # Update progress
                self.progress_percentage = (len(self.completed_steps) / len(self.steps)) * 100
                break
    
    def add_workflow_data(self, key: str, value: Any):
        """Add data to workflow context"""
        self.workflow_data[key] = value

# ================================
# APPROVAL WORKFLOW MODELS
# ================================

class ApprovalRequest(BaseModel):
    """Individual approval request"""
    approval_id: str
    workflow_id: str
    step_id: str
    approval_type: str  # human_review, sponsor_approval, legal_review
    
    # Request details
    title: str
    description: str
    requested_by: str  # User ID
    assigned_to: str   # Approver user ID
    priority: WorkflowPriority = WorkflowPriority.MEDIUM
    
    # Approval data
    status: ApprovalStatus = ApprovalStatus.PENDING
    decision_reason: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    # Context and attachments
    context_data: Dict[str, Any] = {}
    attachments: List[str] = []  # File paths or URLs
    
    # Timing and escalation
    created_at: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    escalation_date: Optional[datetime] = None
    escalation_to: Optional[str] = None
    
    # Approval options
    approval_options: List[str] = ["approve", "reject", "request_changes"]
    auto_approve_threshold: Optional[float] = None

class ApprovalWorkflow(BaseModel):
    """Manages approval workflows"""
    workflow_id: str
    approval_chain: List[ApprovalRequest] = []
    parallel_approvals: List[List[str]] = []  # Groups of approvals that can run in parallel
    sequential_approvals: List[str] = []      # Approvals that must run in sequence
    
    # Workflow status
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_approval_id: Optional[str] = None
    completed_approvals: List[str] = []
    
    def get_pending_approvals(self) -> List[ApprovalRequest]:
        """Get all pending approval requests"""
        return [req for req in self.approval_chain if req.status == ApprovalStatus.PENDING]
    
    def get_next_approval(self) -> Optional[ApprovalRequest]:
        """Get next approval to process"""
        for req in self.approval_chain:
            if req.status == ApprovalStatus.PENDING:
                return req
        return None

# ================================
# NOTIFICATION MODELS
# ================================

class NotificationTemplate(BaseModel):
    """Template for notifications"""
    template_id: str
    template_name: str
    notification_type: NotificationType
    subject_template: str
    body_template: str
    trigger_events: List[str]  # workflow_started, step_completed, approval_needed, etc.
    recipient_rules: Dict[str, Any]  # Rules for determining recipients
    is_active: bool = True

class NotificationRequest(BaseModel):
    """Individual notification to send"""
    notification_id: str
    workflow_id: str
    template_id: str
    notification_type: NotificationType
    
    # Recipients
    recipients: List[str]  # Email addresses, phone numbers, user IDs, etc.
    
    # Content
    subject: str
    body: str
    attachments: List[str] = []
    
    # Metadata
    priority: WorkflowPriority = WorkflowPriority.MEDIUM
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivery_status: str = "pending"  # pending, sent, delivered, failed
    
    # Context
    context_data: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)

# ================================
# WORKFLOW ANALYTICS MODELS
# ================================

class WorkflowMetrics(BaseModel):
    """Metrics for workflow performance"""
    workflow_id: str
    template_id: str
    
    # Timing metrics
    total_duration_minutes: Optional[int] = None
    average_step_duration: Optional[float] = None
    bottleneck_steps: List[str] = []
    
    # Success metrics
    completion_rate: float = 0.0
    error_rate: float = 0.0
    approval_success_rate: float = 0.0
    
    # Step performance
    step_metrics: Dict[str, Dict[str, Any]] = {}  # step_id -> metrics
    
    # Resource utilization
    human_hours_required: Optional[float] = None
    automated_percentage: float = 0.0
    
    # Quality metrics
    rework_count: int = 0
    escalation_count: int = 0
    
    # Timestamps
    calculated_at: datetime = Field(default_factory=datetime.now)

class WorkflowAnalytics(BaseModel):
    """Comprehensive workflow analytics"""
    analytics_id: str
    time_period: str  # daily, weekly, monthly
    
    # Overall metrics
    total_workflows: int = 0
    completed_workflows: int = 0
    failed_workflows: int = 0
    cancelled_workflows: int = 0
    
    # Performance trends
    average_completion_time: Optional[float] = None
    completion_rate_trend: List[float] = []
    volume_trend: List[int] = []
    
    # Template performance
    template_metrics: Dict[str, WorkflowMetrics] = {}
    
    # Bottleneck analysis
    common_bottlenecks: List[str] = []
    approval_bottlenecks: List[str] = []
    
    # Resource analysis
    peak_usage_hours: List[int] = []
    human_vs_automated_ratio: float = 0.0
    
    # Generated at
    generated_at: datetime = Field(default_factory=datetime.now)

# ================================
# WORKFLOW CONFIGURATION MODELS
# ================================

class WorkflowConfiguration(BaseModel):
    """Configuration for workflow behavior"""
    config_id: str
    workflow_template_id: str
    
    # Timing configuration
    default_step_timeout_minutes: int = 60
    approval_timeout_hours: int = 24
    escalation_timeout_hours: int = 48
    
    # Notification configuration
    notification_enabled: bool = True
    notification_templates: List[str] = []
    reminder_intervals: List[int] = [24, 48, 72]  # Hours
    
    # Approval configuration
    require_approval: bool = True
    parallel_approvals_enabled: bool = False
    auto_approve_threshold: Optional[float] = None
    
    # Error handling
    max_retry_attempts: int = 3
    retry_delay_minutes: int = 30
    failure_escalation_enabled: bool = True
    
    # Integration settings
    external_integrations: List[str] = []
    webhook_urls: List[str] = []
    
    # Customization
    custom_fields: Dict[str, Any] = {}
    business_rules: List[Dict[str, Any]] = []

# ================================
# WORKFLOW AUDIT MODELS
# ================================

class WorkflowAuditLog(BaseModel):
    """Audit log entry for workflow changes"""
    log_id: str
    workflow_id: str
    step_id: Optional[str] = None
    
    # Event details
    event_type: str  # step_started, step_completed, approval_requested, etc.
    event_description: str
    performed_by: str  # User ID or "system"
    
    # Before/after state
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    
    # Context
    context_data: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.now)

class WorkflowReport(BaseModel):
    """Comprehensive workflow report"""
    report_id: str
    report_type: str  # summary, detailed, audit, performance
    workflow_id: str
    
    # Report content
    summary: Dict[str, Any] = {}
    detailed_steps: List[Dict[str, Any]] = []
    audit_trail: List[WorkflowAuditLog] = []
    metrics: Optional[WorkflowMetrics] = None
    
    # Report metadata
    generated_by: str
    generated_at: datetime = Field(default_factory=datetime.now)
    report_format: str = "json"  # json, pdf, excel
    
    # Sharing and access
    shared_with: List[str] = []
    access_level: str = "private"  # private, team, public

# ================================
# HELPER FUNCTIONS
# ================================

def create_campaign_workflow_template() -> WorkflowTemplate:
    """Create standard campaign workflow template"""
    
    steps = [
        WorkflowStep(
            step_id="data_collection",
            step_name="Campaign Data Collection",
            step_type="data_collection",
            estimated_duration_minutes=15
        ),
        WorkflowStep(
            step_id="data_validation",
            step_name="Data Validation",
            step_type="validation",
            estimated_duration_minutes=5,
            dependencies=["data_collection"]
        ),
        WorkflowStep(
            step_id="influencer_discovery",
            step_name="Influencer Discovery",
            step_type="discovery",
            estimated_duration_minutes=10,
            dependencies=["data_validation"]
        ),
        WorkflowStep(
            step_id="influencer_selection",
            step_name="Influencer Selection",
            step_type="selection",
            estimated_duration_minutes=5,
            dependencies=["influencer_discovery"]
        ),
        WorkflowStep(
            step_id="negotiations",
            step_name="Influencer Negotiations",
            step_type="negotiation",
            estimated_duration_minutes=60,
            dependencies=["influencer_selection"]
        ),
        WorkflowStep(
            step_id="human_review",
            step_name="Human Review",
            step_type="approval",
            estimated_duration_minutes=120,
            dependencies=["negotiations"]
        ),
        WorkflowStep(
            step_id="sponsor_approval",
            step_name="Sponsor Approval",
            step_type="approval",
            estimated_duration_minutes=480,  # 8 hours
            dependencies=["human_review"]
        ),
        WorkflowStep(
            step_id="contract_generation",
            step_name="Contract Generation",
            step_type="contract",
            estimated_duration_minutes=10,
            dependencies=["sponsor_approval"]
        ),
        WorkflowStep(
            step_id="contract_delivery",
            step_name="Contract Delivery",
            step_type="delivery",
            estimated_duration_minutes=5,
            dependencies=["contract_generation"]
        )
    ]
    
    return WorkflowTemplate(
        template_id="standard_campaign_workflow",
        template_name="Standard Campaign Workflow",
        description="Complete influencer campaign workflow with human oversight",
        category="campaign",
        steps=steps,
        estimated_total_duration_minutes=sum(step.estimated_duration_minutes for step in steps),
        required_approvals=["human_review", "sponsor_approval"]
    )

def create_approval_workflow_template() -> WorkflowTemplate:
    """Create approval-focused workflow template"""
    
    steps = [
        WorkflowStep(
            step_id="approval_request",
            step_name="Create Approval Request",
            step_type="approval_creation",
            estimated_duration_minutes=5
        ),
        WorkflowStep(
            step_id="reviewer_assignment",
            step_name="Assign Reviewer",
            step_type="assignment",
            estimated_duration_minutes=2,
            dependencies=["approval_request"]
        ),
        WorkflowStep(
            step_id="review_process",
            step_name="Review Process",
            step_type="approval",
            estimated_duration_minutes=240,  # 4 hours
            dependencies=["reviewer_assignment"]
        ),
        WorkflowStep(
            step_id="decision_processing",
            step_name="Process Decision",
            step_type="decision",
            estimated_duration_minutes=5,
            dependencies=["review_process"]
        ),
        WorkflowStep(
            step_id="notification",
            step_name="Send Notifications",
            step_type="notification",
            estimated_duration_minutes=2,
            dependencies=["decision_processing"]
        )
    ]
    
    return WorkflowTemplate(
        template_id="approval_workflow",
        template_name="Approval Workflow",
        description="Standard approval workflow with notifications",
        category="approval",
        steps=steps,
        estimated_total_duration_minutes=sum(step.estimated_duration_minutes for step in steps),
        required_approvals=["review_process"]
    )