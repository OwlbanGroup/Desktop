"""
Compliance and Reporting System
Handles labor law compliance, diversity reporting, and HR analytics
"""

import json
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"

class ReportType(Enum):
    DIVERSITY_EQUITY_INCLUSION = "dei"
    LABOR_LAW_COMPLIANCE = "labor_compliance"
    EMPLOYEE_TURNOVER = "turnover"
    WORKPLACE_SAFETY = "safety"
    BENEFITS_UTILIZATION = "benefits_utilization"
    PERFORMANCE_ANALYTICS = "performance_analytics"
    COMPENSATION_ANALYSIS = "compensation_analysis"

class AuditType(Enum):
    OSHA_COMPLIANCE = "osha"
    FLSA_COMPLIANCE = "flsa"
    EEOC_COMPLIANCE = "eeoc"
    ADA_COMPLIANCE = "ada"
    FMLA_COMPLIANCE = "fmla"
    WORKERS_COMP = "workers_comp"

@dataclass
class ComplianceAudit:
    audit_id: str
    audit_type: AuditType
    department: str
    auditor: str
    audit_date: date
    findings: List[Dict[str, str]]  # List of {"issue": str, "severity": str, "recommendation": str}
    status: ComplianceStatus
    corrective_actions: List[Dict[str, str]]  # List of {"action": str, "deadline": str, "assigned_to": str}
    follow_up_date: Optional[date]
    created_at: datetime
    updated_at: datetime

@dataclass
class DiversityReport:
    report_id: str
    report_year: int
    report_quarter: int
    total_employees: int
    gender_breakdown: Dict[str, int]  # male, female, non_binary, prefer_not_to_say
    ethnicity_breakdown: Dict[str, int]  # various ethnic categories
    age_groups: Dict[str, int]  # under_30, 30_40, 41_50, 51_60, over_60
    department_diversity: Dict[str, Dict[str, int]]
    hiring_diversity: Dict[str, int]
    promotion_diversity: Dict[str, int]
    retention_rates: Dict[str, float]
    created_at: datetime

@dataclass
class HRMetric:
    metric_id: str
    metric_type: str
    department: str
    value: float
    target_value: Optional[float]
    period_start: date
    period_end: date
    calculated_at: datetime
    notes: Optional[str]

class ComplianceReportingManager:
    def __init__(self, audits_file: str = "hr_system/compliance_audits.json",
                 diversity_file: str = "hr_system/diversity_reports.json",
                 metrics_file: str = "hr_system/hr_metrics.json"):
        self.audits_file = audits_file
        self.diversity_file = diversity_file
        self.metrics_file = metrics_file
        self.audits: Dict[str, ComplianceAudit] = {}
        self.diversity_reports: Dict[str, DiversityReport] = {}
        self.metrics: Dict[str, HRMetric] = {}
        self._load_data()

    def _load_data(self):
        """Load compliance and reporting data from files"""
        # Load audits
        try:
            with open(self.audits_file, 'r') as f:
                data = json.load(f)
                for audit_data in data.get('audits', []):
                    audit_data['audit_type'] = AuditType(audit_data['audit_type'])
                    audit_data['audit_date'] = date.fromisoformat(audit_data['audit_date'])
                    audit_data['status'] = ComplianceStatus(audit_data['status'])
                    audit_data['created_at'] = datetime.fromisoformat(audit_data['created_at'])
                    audit_data['updated_at'] = datetime.fromisoformat(audit_data['updated_at'])
                    if audit_data.get('follow_up_date'):
                        audit_data['follow_up_date'] = date.fromisoformat(audit_data['follow_up_date'])
                    audit = ComplianceAudit(**audit_data)
                    self.audits[audit.audit_id] = audit
        except FileNotFoundError:
            self.audits = {}

        # Load diversity reports
        try:
            with open(self.diversity_file, 'r') as f:
                data = json.load(f)
                for report_data in data.get('reports', []):
                    report_data['created_at'] = datetime.fromisoformat(report_data['created_at'])
                    report = DiversityReport(**report_data)
                    self.diversity_reports[report.report_id] = report
        except FileNotFoundError:
            self.diversity_reports = {}

        # Load metrics
        try:
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
                for metric_data in data.get('metrics', []):
                    metric_data['period_start'] = date.fromisoformat(metric_data['period_start'])
                    metric_data['period_end'] = date.fromisoformat(metric_data['period_end'])
                    metric_data['calculated_at'] = datetime.fromisoformat(metric_data['calculated_at'])
                    metric = HRMetric(**metric_data)
                    self.metrics[metric.metric_id] = metric
        except FileNotFoundError:
            self.metrics = {}

    def _save_audits(self):
        """Save compliance audits to file"""
        data = {
            'audits': [asdict(audit) for audit in self.audits.values()],
            'last_updated': datetime.now().isoformat()
        }
        # Convert for JSON serialization
        for audit_data in data['audits']:
            audit_data['audit_type'] = audit_data['audit_type'].value
            audit_data['audit_date'] = audit_data['audit_date'].isoformat()
            audit_data['status'] = audit_data['status'].value
            audit_data['created_at'] = audit_data['created_at'].isoformat()
            audit_data['updated_at'] = audit_data['updated_at'].isoformat()
            if audit_data.get('follow_up_date'):
                audit_data['follow_up_date'] = audit_data['follow_up_date'].isoformat()

        with open(self.audits_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_diversity_reports(self):
        """Save diversity reports to file"""
        data = {
            'reports': [asdict(report) for report in self.diversity_reports.values()],
            'last_updated': datetime.now().isoformat()
        }
        # Convert for JSON serialization
        for report_data in data['reports']:
            report_data['created_at'] = report_data['created_at'].isoformat()

        with open(self.diversity_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_metrics(self):
        """Save HR metrics to file"""
        data = {
            'metrics': [asdict(metric) for metric in self.metrics.values()],
            'last_updated': datetime.now().isoformat()
        }
        # Convert for JSON serialization
        for metric_data in data['metrics']:
            metric_data['period_start'] = metric_data['period_start'].isoformat()
            metric_data['period_end'] = metric_data['period_end'].isoformat()
            metric_data['calculated_at'] = metric_data['calculated_at'].isoformat()

        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_compliance_audit(self, audit_type: AuditType, department: str,
                              auditor: str, audit_date: date,
                              findings: List[Dict[str, str]]) -> ComplianceAudit:
        """Create a new compliance audit"""
        audit_id = str(uuid.uuid4())

        audit = ComplianceAudit(
            audit_id=audit_id,
            audit_type=audit_type,
            department=department,
            auditor=auditor,
            audit_date=audit_date,
            findings=findings,
            status=ComplianceStatus.PENDING_REVIEW,
            corrective_actions=[],
            follow_up_date=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.audits[audit_id] = audit
        self._save_audits()
        return audit

    def update_audit_status(self, audit_id: str, status: ComplianceStatus,
                          corrective_actions: Optional[List[Dict[str, str]]] = None,
                          follow_up_date: Optional[date] = None) -> Optional[ComplianceAudit]:
        """Update audit status and add corrective actions"""
        if audit_id not in self.audits:
            return None

        audit = self.audits[audit_id]
        audit.status = status

        if corrective_actions:
            audit.corrective_actions = corrective_actions

        if follow_up_date:
            audit.follow_up_date = follow_up_date

        audit.updated_at = datetime.now()
        self._save_audits()
        return audit

    def get_audits_by_status(self, status: ComplianceStatus) -> List[ComplianceAudit]:
        """Get audits by compliance status"""
        return [audit for audit in self.audits.values() if audit.status == status]

    def get_audits_by_type(self, audit_type: AuditType) -> List[ComplianceAudit]:
        """Get audits by type"""
        return [audit for audit in self.audits.values() if audit.audit_type == audit_type]

    def create_diversity_report(self, report_year: int, report_quarter: int,
                              total_employees: int, gender_breakdown: Dict[str, int],
                              ethnicity_breakdown: Dict[str, int], age_groups: Dict[str, int],
                              department_diversity: Dict[str, Dict[str, int]],
                              hiring_diversity: Dict[str, int], promotion_diversity: Dict[str, int],
                              retention_rates: Dict[str, float]) -> DiversityReport:
        """Create a diversity report"""
        report_id = str(uuid.uuid4())

        report = DiversityReport(
            report_id=report_id,
            report_year=report_year,
            report_quarter=report_quarter,
            total_employees=total_employees,
            gender_breakdown=gender_breakdown,
            ethnicity_breakdown=ethnicity_breakdown,
            age_groups=age_groups,
            department_diversity=department_diversity,
            hiring_diversity=hiring_diversity,
            promotion_diversity=promotion_diversity,
            retention_rates=retention_rates,
            created_at=datetime.now()
        )

        self.diversity_reports[report_id] = report
        self._save_diversity_reports()
        return report

    def get_diversity_report(self, year: int, quarter: int) -> Optional[DiversityReport]:
        """Get diversity report for specific year and quarter"""
        for report in self.diversity_reports.values():
            if report.report_year == year and report.report_quarter == quarter:
                return report
        return None

    def calculate_diversity_metrics(self, report: DiversityReport) -> Dict[str, float]:
        """Calculate diversity metrics from report"""
        total = report.total_employees

        # Gender diversity index (closer to 1.0 is more diverse)
        gender_values = list(report.gender_breakdown.values())
        gender_diversity = 1 - sum((v/total)**2 for v in gender_values)

        # Ethnicity diversity index
        ethnicity_values = list(report.ethnicity_breakdown.values())
        ethnicity_diversity = 1 - sum((v/total)**2 for v in ethnicity_values)

        # Age diversity index
        age_values = list(report.age_groups.values())
        age_diversity = 1 - sum((v/total)**2 for v in age_values)

        return {
            'gender_diversity_index': gender_diversity,
            'ethnicity_diversity_index': ethnicity_diversity,
            'age_diversity_index': age_diversity,
            'overall_diversity_index': (gender_diversity + ethnicity_diversity + age_diversity) / 3
        }

    def record_hr_metric(self, metric_type: str, department: str, value: float,
                        target_value: Optional[float], period_start: date,
                        period_end: date, notes: Optional[str] = None) -> HRMetric:
        """Record an HR metric"""
        metric_id = str(uuid.uuid4())

        metric = HRMetric(
            metric_id=metric_id,
            metric_type=metric_type,
            department=department,
            value=value,
            target_value=target_value,
            period_start=period_start,
            period_end=period_end,
            calculated_at=datetime.now(),
            notes=notes
        )

        self.metrics[metric_id] = metric
        self._save_metrics()
        return metric

    def get_metrics_by_type(self, metric_type: str, department: Optional[str] = None,
                          period_start: Optional[date] = None, period_end: Optional[date] = None) -> List[HRMetric]:
        """Get metrics by type with optional filters"""
        metrics = [metric for metric in self.metrics.values() if metric.metric_type == metric_type]

        if department:
            metrics = [m for m in metrics if m.department == department]

        if period_start:
            metrics = [m for m in metrics if m.period_start >= period_start]

        if period_end:
            metrics = [m for m in metrics if m.period_end <= period_end]

        return metrics

    def generate_compliance_dashboard(self) -> Dict[str, Any]:
        """Generate compliance dashboard data"""
        total_audits = len(self.audits)
        compliant_audits = len([a for a in self.audits.values() if a.status == ComplianceStatus.COMPLIANT])
        non_compliant_audits = len([a for a in self.audits.values() if a.status == ComplianceStatus.NON_COMPLIANT])
        pending_audits = len([a for a in self.audits.values() if a.status in [ComplianceStatus.PENDING_REVIEW, ComplianceStatus.UNDER_REVIEW]])

        # Compliance by audit type
        compliance_by_type = {}
        for audit_type in AuditType:
            type_audits = [a for a in self.audits.values() if a.audit_type == audit_type]
            if type_audits:
                compliant_count = len([a for a in type_audits if a.status == ComplianceStatus.COMPLIANT])
                compliance_by_type[audit_type.value] = {
                    'total': len(type_audits),
                    'compliant': compliant_count,
                    'compliance_rate': (compliant_count / len(type_audits)) * 100
                }

        return {
            'total_audits': total_audits,
            'compliant_audits': compliant_audits,
            'non_compliant_audits': non_compliant_audits,
            'pending_audits': pending_audits,
            'overall_compliance_rate': (compliant_audits / total_audits * 100) if total_audits > 0 else 0,
            'compliance_by_type': compliance_by_type
        }

    def generate_hr_analytics_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate comprehensive HR analytics report"""
        # Filter metrics by date range
        period_metrics = [m for m in self.metrics.values()
                         if m.period_start >= start_date and m.period_end <= end_date]

        # Group metrics by type
        metrics_by_type = {}
        for metric in period_metrics:
            if metric.metric_type not in metrics_by_type:
                metrics_by_type[metric.metric_type] = []
            metrics_by_type[metric.metric_type].append(metric)

        # Calculate trends and averages
        analytics = {}
        for metric_type, metrics_list in metrics_by_type.items():
            values = [m.value for m in metrics_list]
            targets = [m.target_value for m in metrics_list if m.target_value is not None]

            analytics[metric_type] = {
                'count': len(metrics_list),
                'average_value': sum(values) / len(values) if values else 0,
                'min_value': min(values) if values else 0,
                'max_value': max(values) if values else 0,
                'target_achievement_rate': (len([v for v, t in zip(values, targets) if t and v >= t]) / len(targets) * 100) if targets else 0,
                'trend': self._calculate_trend(values)
            }

        return {
            'report_period': f"{start_date.isoformat()} to {end_date.isoformat()}",
            'total_metrics': len(period_metrics),
            'analytics_by_type': analytics,
            'generated_at': datetime.now().isoformat()
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "insufficient_data"

        # Simple linear trend
        if values[-1] > values[0]:
            return "increasing"
        elif values[-1] < values[0]:
            return "decreasing"
        else:
            return "stable"

    def get_upcoming_audit_followups(self, days_ahead: int = 30) -> List[ComplianceAudit]:
        """Get audits requiring follow-up within specified days"""
        today = date.today()
        future_date = today + timedelta(days=days_ahead)

        return [audit for audit in self.audits.values()
                if audit.follow_up_date and today <= audit.follow_up_date <= future_date]

    def export_compliance_data(self, export_format: str = "json") -> str:
        """Export compliance data for external reporting"""
        data = {
            'audits': [asdict(audit) for audit in self.audits.values()],
            'diversity_reports': [asdict(report) for report in self.diversity_reports.values()],
            'metrics': [asdict(metric) for metric in self.metrics.values()],
            'exported_at': datetime.now().isoformat()
        }

        if export_format == "json":
            return json.dumps(data, indent=2, default=str)
        else:
            # Could implement CSV or other formats
            return json.dumps(data, default=str)
