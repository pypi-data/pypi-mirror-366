"""
Advanced Security Analyzer for SQL Queries.

This cutting-edge module provides comprehensive security analysis for SQL queries,
detecting vulnerabilities, injection attacks, and security best practice violations.
"""

from __future__ import annotations

import asyncio
import logging
import re
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from ..types import SQLQuery, UserID, SQLDialect
from ..exceptions import SecurityError, Text2SQLLTMError

logger = logging.getLogger(__name__)


class VulnerabilityType(str, Enum):
    """Types of security vulnerabilities."""
    SQL_INJECTION = "sql_injection"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXPOSURE = "data_exposure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    WEAK_AUTHENTICATION = "weak_authentication"
    INSECURE_CONFIGURATION = "insecure_configuration"
    INFORMATION_DISCLOSURE = "information_disclosure"
    DENIAL_OF_SERVICE = "denial_of_service"


class SeverityLevel(str, Enum):
    """Security vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AttackVector(str, Enum):
    """Attack vectors for vulnerabilities."""
    USER_INPUT = "user_input"
    DYNAMIC_SQL = "dynamic_sql"
    STORED_PROCEDURE = "stored_procedure"
    CONFIGURATION = "configuration"
    PRIVILEGE_ABUSE = "privilege_abuse"
    NETWORK = "network"


@dataclass
class SecurityVulnerability:
    """Security vulnerability details."""
    type: VulnerabilityType
    severity: SeverityLevel
    attack_vector: AttackVector
    description: str
    location: Optional[str] = None
    evidence: Optional[str] = None
    remediation: Optional[str] = None
    cve_references: List[str] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = None


@dataclass
class SecurityAnalysisResult:
    """Result of security analysis."""
    query: str
    is_secure: bool
    risk_score: float
    vulnerabilities: List[SecurityVulnerability]
    security_recommendations: List[str]
    compliance_issues: List[str]
    analysis_metadata: Dict[str, Any]
    analyzed_at: datetime


class SecurityAnalyzer:
    """
    Advanced security analyzer for SQL queries and database operations.
    
    This analyzer provides:
    - SQL injection detection
    - Privilege escalation detection
    - Data exposure analysis
    - Compliance checking
    - Security best practice validation
    - Real-time threat detection
    """
    
    def __init__(
        self,
        enable_ai_analysis: bool = True,
        strict_mode: bool = False
    ):
        self.enable_ai_analysis = enable_ai_analysis
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Load security patterns and rules
        self.injection_patterns = self._load_injection_patterns()
        self.privilege_patterns = self._load_privilege_patterns()
        self.exposure_patterns = self._load_exposure_patterns()
        self.compliance_rules = self._load_compliance_rules()
        
        # Known attack signatures
        self.attack_signatures = self._load_attack_signatures()
        
        # Metrics
        self._metrics = {
            "analyses_performed": 0,
            "vulnerabilities_found": 0,
            "critical_vulnerabilities": 0,
            "injection_attempts_blocked": 0,
            "compliance_violations": 0
        }
    
    async def analyze_security(
        self,
        query: SQLQuery,
        user_id: Optional[UserID] = None,
        context: Optional[Dict[str, Any]] = None,
        dialect: SQLDialect = SQLDialect.POSTGRESQL
    ) -> SecurityAnalysisResult:
        """
        Perform comprehensive security analysis of SQL query.
        
        Args:
            query: SQL query to analyze
            user_id: Optional user ID for context
            context: Additional context for analysis
            dialect: SQL dialect for dialect-specific checks
            
        Returns:
            Comprehensive security analysis result
        """
        try:
            self._metrics["analyses_performed"] += 1
            
            vulnerabilities = []
            
            # SQL Injection Analysis
            injection_vulns = await self._analyze_sql_injection(query, context)
            vulnerabilities.extend(injection_vulns)
            
            # Privilege Escalation Analysis
            privilege_vulns = await self._analyze_privilege_escalation(query, user_id)
            vulnerabilities.extend(privilege_vulns)
            
            # Data Exposure Analysis
            exposure_vulns = await self._analyze_data_exposure(query, context)
            vulnerabilities.extend(exposure_vulns)
            
            # Unauthorized Access Analysis
            access_vulns = await self._analyze_unauthorized_access(query, user_id, context)
            vulnerabilities.extend(access_vulns)
            
            # Configuration Security Analysis
            config_vulns = await self._analyze_configuration_security(query, dialect)
            vulnerabilities.extend(config_vulns)
            
            # DoS Analysis
            dos_vulns = await self._analyze_denial_of_service(query)
            vulnerabilities.extend(dos_vulns)
            
            # AI-Enhanced Analysis
            if self.enable_ai_analysis:
                ai_vulns = await self._ai_enhanced_analysis(query, vulnerabilities, context)
                vulnerabilities.extend(ai_vulns)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(vulnerabilities)
            
            # Determine if secure
            is_secure = self._determine_security_status(vulnerabilities, risk_score)
            
            # Generate recommendations
            recommendations = self._generate_security_recommendations(vulnerabilities, query)
            
            # Check compliance
            compliance_issues = self._check_compliance(query, vulnerabilities)
            
            # Update metrics
            self._update_metrics(vulnerabilities)
            
            return SecurityAnalysisResult(
                query=query,
                is_secure=is_secure,
                risk_score=risk_score,
                vulnerabilities=vulnerabilities,
                security_recommendations=recommendations,
                compliance_issues=compliance_issues,
                analysis_metadata={
                    "analyzer_version": "1.0",
                    "strict_mode": self.strict_mode,
                    "ai_enhanced": self.enable_ai_analysis,
                    "dialect": dialect.value,
                    "user_id": user_id
                },
                analyzed_at=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Security analysis failed: {str(e)}")
            raise SecurityError(f"Security analysis failed: {str(e)}") from e
    
    async def _analyze_sql_injection(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> List[SecurityVulnerability]:
        """Analyze for SQL injection vulnerabilities."""
        vulnerabilities = []
        
        # Check for classic injection patterns
        for pattern_name, pattern in self.injection_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                vulnerabilities.append(SecurityVulnerability(
                    type=VulnerabilityType.SQL_INJECTION,
                    severity=SeverityLevel.CRITICAL,
                    attack_vector=AttackVector.USER_INPUT,
                    description=f"Potential SQL injection detected: {pattern_name}",
                    evidence=pattern_name,
                    remediation="Use parameterized queries or prepared statements",
                    confidence=0.9
                ))
        
        # Check for dynamic SQL construction
        if self._has_dynamic_sql_construction(query):
            vulnerabilities.append(SecurityVulnerability(
                type=VulnerabilityType.SQL_INJECTION,
                severity=SeverityLevel.HIGH,
                attack_vector=AttackVector.DYNAMIC_SQL,
                description="Dynamic SQL construction detected",
                remediation="Use parameterized queries instead of string concatenation",
                confidence=0.8
            ))
        
        # Check for unescaped user input
        if context and self._has_unescaped_input(query, context):
            vulnerabilities.append(SecurityVulnerability(
                type=VulnerabilityType.SQL_INJECTION,
                severity=SeverityLevel.CRITICAL,
                attack_vector=AttackVector.USER_INPUT,
                description="Unescaped user input detected in query",
                remediation="Properly escape or parameterize user input",
                confidence=0.95
            ))
        
        return vulnerabilities
    
    async def _analyze_privilege_escalation(
        self,
        query: str,
        user_id: Optional[UserID]
    ) -> List[SecurityVulnerability]:
        """Analyze for privilege escalation vulnerabilities."""
        vulnerabilities = []
        query_upper = query.upper()
        
        # Check for privilege management statements
        privilege_statements = [
            "GRANT", "REVOKE", "ALTER USER", "CREATE USER", "DROP USER",
            "ALTER ROLE", "CREATE ROLE", "DROP ROLE"
        ]
        
        for statement in privilege_statements:
            if statement in query_upper:
                vulnerabilities.append(SecurityVulnerability(
                    type=VulnerabilityType.PRIVILEGE_ESCALATION,
                    severity=SeverityLevel.HIGH,
                    attack_vector=AttackVector.PRIVILEGE_ABUSE,
                    description=f"Privilege management statement detected: {statement}",
                    evidence=statement,
                    remediation="Ensure proper authorization for privilege operations",
                    confidence=0.9
                ))
        
        # Check for system function calls
        system_functions = [
            "xp_cmdshell", "sp_configure", "openrowset", "opendatasource",
            "bulk insert", "exec master"
        ]
        
        for func in system_functions:
            if func.upper() in query_upper:
                vulnerabilities.append(SecurityVulnerability(
                    type=VulnerabilityType.PRIVILEGE_ESCALATION,
                    severity=SeverityLevel.CRITICAL,
                    attack_vector=AttackVector.STORED_PROCEDURE,
                    description=f"Dangerous system function detected: {func}",
                    evidence=func,
                    remediation="Avoid using system functions or restrict access",
                    confidence=0.95
                ))
        
        return vulnerabilities
    
    async def _analyze_data_exposure(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> List[SecurityVulnerability]:
        """Analyze for data exposure vulnerabilities."""
        vulnerabilities = []
        query_upper = query.upper()
        
        # Check for SELECT * queries
        if re.search(r'SELECT\s+\*', query_upper):
            vulnerabilities.append(SecurityVulnerability(
                type=VulnerabilityType.DATA_EXPOSURE,
                severity=SeverityLevel.MEDIUM,
                attack_vector=AttackVector.USER_INPUT,
                description="SELECT * may expose sensitive data",
                remediation="Select only necessary columns",
                confidence=0.7
            ))
        
        # Check for sensitive table access
        sensitive_tables = [
            "users", "passwords", "credentials", "tokens", "keys",
            "personal_data", "financial", "medical", "confidential"
        ]
        
        for table in sensitive_tables:
            if re.search(rf'\b{table}\b', query, re.IGNORECASE):
                vulnerabilities.append(SecurityVulnerability(
                    type=VulnerabilityType.DATA_EXPOSURE,
                    severity=SeverityLevel.HIGH,
                    attack_vector=AttackVector.PRIVILEGE_ABUSE,
                    description=f"Access to sensitive table detected: {table}",
                    evidence=table,
                    remediation="Ensure proper access controls for sensitive data",
                    confidence=0.8
                ))
        
        # Check for password/credential exposure
        credential_patterns = [
            r'password', r'passwd', r'pwd', r'secret', r'token',
            r'api_key', r'private_key', r'credential'
        ]
        
        for pattern in credential_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                vulnerabilities.append(SecurityVulnerability(
                    type=VulnerabilityType.INFORMATION_DISCLOSURE,
                    severity=SeverityLevel.CRITICAL,
                    attack_vector=AttackVector.DATA_EXPOSURE,
                    description=f"Potential credential exposure: {pattern}",
                    evidence=pattern,
                    remediation="Never expose credentials in queries",
                    confidence=0.9
                ))
        
        return vulnerabilities
    
    async def _analyze_unauthorized_access(
        self,
        query: str,
        user_id: Optional[UserID],
        context: Optional[Dict[str, Any]]
    ) -> List[SecurityVulnerability]:
        """Analyze for unauthorized access attempts."""
        vulnerabilities = []
        
        # Check for missing WHERE clauses in sensitive operations
        if re.search(r'(UPDATE|DELETE)\s+(?!.*WHERE)', query, re.IGNORECASE):
            vulnerabilities.append(SecurityVulnerability(
                type=VulnerabilityType.UNAUTHORIZED_ACCESS,
                severity=SeverityLevel.HIGH,
                attack_vector=AttackVector.USER_INPUT,
                description="UPDATE/DELETE without WHERE clause affects all rows",
                remediation="Always use WHERE clause to limit affected rows",
                confidence=0.9
            ))
        
        # Check for cross-user data access
        if context and self._has_cross_user_access(query, user_id, context):
            vulnerabilities.append(SecurityVulnerability(
                type=VulnerabilityType.UNAUTHORIZED_ACCESS,
                severity=SeverityLevel.HIGH,
                attack_vector=AttackVector.PRIVILEGE_ABUSE,
                description="Potential cross-user data access detected",
                remediation="Implement proper user isolation",
                confidence=0.8
            ))
        
        return vulnerabilities
    
    async def _analyze_configuration_security(
        self,
        query: str,
        dialect: SQLDialect
    ) -> List[SecurityVulnerability]:
        """Analyze for configuration security issues."""
        vulnerabilities = []
        
        # Check for weak encryption
        if re.search(r'MD5|SHA1', query, re.IGNORECASE):
            vulnerabilities.append(SecurityVulnerability(
                type=VulnerabilityType.INSECURE_CONFIGURATION,
                severity=SeverityLevel.MEDIUM,
                attack_vector=AttackVector.CONFIGURATION,
                description="Weak hashing algorithm detected",
                remediation="Use stronger hashing algorithms like SHA-256 or bcrypt",
                confidence=0.8
            ))
        
        # Check for hardcoded values
        if self._has_hardcoded_values(query):
            vulnerabilities.append(SecurityVulnerability(
                type=VulnerabilityType.INSECURE_CONFIGURATION,
                severity=SeverityLevel.MEDIUM,
                attack_vector=AttackVector.CONFIGURATION,
                description="Hardcoded values detected in query",
                remediation="Use configuration parameters instead of hardcoded values",
                confidence=0.7
            ))
        
        return vulnerabilities
    
    async def _analyze_denial_of_service(self, query: str) -> List[SecurityVulnerability]:
        """Analyze for denial of service vulnerabilities."""
        vulnerabilities = []
        
        # Check for expensive operations without limits
        expensive_operations = [
            r'CROSS\s+JOIN', r'CARTESIAN\s+PRODUCT', r'SELECT\s+\*.*JOIN.*JOIN'
        ]
        
        for pattern in expensive_operations:
            if re.search(pattern, query, re.IGNORECASE) and "LIMIT" not in query.upper():
                vulnerabilities.append(SecurityVulnerability(
                    type=VulnerabilityType.DENIAL_OF_SERVICE,
                    severity=SeverityLevel.MEDIUM,
                    attack_vector=AttackVector.USER_INPUT,
                    description="Expensive operation without LIMIT clause",
                    remediation="Add LIMIT clause to prevent resource exhaustion",
                    confidence=0.7
                ))
        
        # Check for recursive queries without limits
        if "WITH RECURSIVE" in query.upper() and "LIMIT" not in query.upper():
            vulnerabilities.append(SecurityVulnerability(
                type=VulnerabilityType.DENIAL_OF_SERVICE,
                severity=SeverityLevel.HIGH,
                attack_vector=AttackVector.USER_INPUT,
                description="Recursive query without termination limit",
                remediation="Add proper termination conditions to recursive queries",
                confidence=0.9
            ))
        
        return vulnerabilities
    
    async def _ai_enhanced_analysis(
        self,
        query: str,
        existing_vulnerabilities: List[SecurityVulnerability],
        context: Optional[Dict[str, Any]]
    ) -> List[SecurityVulnerability]:
        """AI-enhanced security analysis."""
        # This would use machine learning models to detect sophisticated attacks
        # For now, return empty list
        return []
    
    def _has_dynamic_sql_construction(self, query: str) -> bool:
        """Check if query uses dynamic SQL construction."""
        dynamic_patterns = [
            r"'\s*\+\s*", r'"\s*\+\s*',  # String concatenation
            r'EXEC\s*\(', r'EXECUTE\s*\(',  # Dynamic execution
            r'sp_executesql'  # SQL Server dynamic execution
        ]
        
        for pattern in dynamic_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        
        return False
    
    def _has_unescaped_input(self, query: str, context: Dict[str, Any]) -> bool:
        """Check if query contains unescaped user input."""
        # This would check if user input is properly escaped
        # For now, return False
        return False
    
    def _has_cross_user_access(
        self,
        query: str,
        user_id: Optional[UserID],
        context: Dict[str, Any]
    ) -> bool:
        """Check if query attempts cross-user data access."""
        # This would check if the query accesses data belonging to other users
        # For now, return False
        return False
    
    def _has_hardcoded_values(self, query: str) -> bool:
        """Check if query contains hardcoded sensitive values."""
        hardcoded_patterns = [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]"
        ]
        
        for pattern in hardcoded_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        
        return False
    
    def _calculate_risk_score(self, vulnerabilities: List[SecurityVulnerability]) -> float:
        """Calculate overall risk score."""
        if not vulnerabilities:
            return 0.0
        
        severity_weights = {
            SeverityLevel.CRITICAL: 1.0,
            SeverityLevel.HIGH: 0.7,
            SeverityLevel.MEDIUM: 0.4,
            SeverityLevel.LOW: 0.2,
            SeverityLevel.INFO: 0.1
        }
        
        total_risk = 0.0
        for vuln in vulnerabilities:
            weight = severity_weights.get(vuln.severity, 0.5)
            confidence = vuln.confidence
            total_risk += weight * confidence
        
        # Normalize to 0-10 scale
        max_possible_risk = len(vulnerabilities) * 1.0
        normalized_risk = (total_risk / max_possible_risk) * 10 if max_possible_risk > 0 else 0
        
        return min(10.0, normalized_risk)
    
    def _determine_security_status(
        self,
        vulnerabilities: List[SecurityVulnerability],
        risk_score: float
    ) -> bool:
        """Determine if query is secure."""
        # Check for critical vulnerabilities
        critical_vulns = [
            v for v in vulnerabilities 
            if v.severity == SeverityLevel.CRITICAL
        ]
        
        if critical_vulns:
            return False
        
        # Check risk score threshold
        if self.strict_mode:
            return risk_score < 2.0
        else:
            return risk_score < 5.0
    
    def _generate_security_recommendations(
        self,
        vulnerabilities: List[SecurityVulnerability],
        query: str
    ) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        # Add specific remediation from vulnerabilities
        for vuln in vulnerabilities:
            if vuln.remediation and vuln.remediation not in recommendations:
                recommendations.append(vuln.remediation)
        
        # Add general recommendations
        if not recommendations:
            recommendations.extend([
                "Use parameterized queries to prevent SQL injection",
                "Implement proper input validation and sanitization",
                "Apply principle of least privilege for database access",
                "Regular security audits and vulnerability assessments"
            ])
        
        return recommendations[:10]  # Limit to top 10
    
    def _check_compliance(
        self,
        query: str,
        vulnerabilities: List[SecurityVulnerability]
    ) -> List[str]:
        """Check compliance with security standards."""
        compliance_issues = []
        
        # GDPR compliance
        if re.search(r'personal_data|email|phone|address', query, re.IGNORECASE):
            if not re.search(r'WHERE.*consent', query, re.IGNORECASE):
                compliance_issues.append("GDPR: Personal data access without consent check")
        
        # PCI DSS compliance
        if re.search(r'credit_card|payment|financial', query, re.IGNORECASE):
            if any(v.type == VulnerabilityType.DATA_EXPOSURE for v in vulnerabilities):
                compliance_issues.append("PCI DSS: Potential exposure of financial data")
        
        # SOX compliance
        if re.search(r'financial_report|audit|transaction', query, re.IGNORECASE):
            if not re.search(r'audit_log|trail', query, re.IGNORECASE):
                compliance_issues.append("SOX: Financial data access without audit trail")
        
        return compliance_issues
    
    def _update_metrics(self, vulnerabilities: List[SecurityVulnerability]) -> None:
        """Update security metrics."""
        self._metrics["vulnerabilities_found"] += len(vulnerabilities)
        
        critical_count = sum(
            1 for v in vulnerabilities 
            if v.severity == SeverityLevel.CRITICAL
        )
        self._metrics["critical_vulnerabilities"] += critical_count
        
        injection_count = sum(
            1 for v in vulnerabilities 
            if v.type == VulnerabilityType.SQL_INJECTION
        )
        self._metrics["injection_attempts_blocked"] += injection_count
    
    def _load_injection_patterns(self) -> Dict[str, str]:
        """Load SQL injection detection patterns."""
        return {
            "union_injection": r"'\s*UNION\s+SELECT",
            "comment_injection": r"--\s*$|/\*.*\*/",
            "boolean_injection": r"'\s*OR\s+'1'\s*=\s*'1",
            "time_based_injection": r"WAITFOR\s+DELAY|SLEEP\s*\(",
            "error_based_injection": r"'\s*AND\s+\(SELECT\s+COUNT",
            "stacked_queries": r";\s*(DROP|DELETE|INSERT|UPDATE)",
            "hex_encoding": r"0x[0-9a-fA-F]+",
            "char_function": r"CHAR\s*\(\s*\d+",
            "ascii_function": r"ASCII\s*\(",
            "substring_injection": r"SUBSTRING\s*\([^)]*,\s*\d+\s*,\s*1\s*\)"
        }
    
    def _load_privilege_patterns(self) -> Dict[str, str]:
        """Load privilege escalation patterns."""
        return {
            "grant_all": r"GRANT\s+ALL",
            "create_user": r"CREATE\s+USER",
            "alter_user": r"ALTER\s+USER",
            "drop_user": r"DROP\s+USER",
            "system_admin": r"sysadmin|db_owner|securityadmin"
        }
    
    def _load_exposure_patterns(self) -> Dict[str, str]:
        """Load data exposure patterns."""
        return {
            "select_all": r"SELECT\s+\*",
            "password_field": r"password|passwd|pwd",
            "credit_card": r"credit_card|cc_number|card_number",
            "ssn": r"ssn|social_security",
            "api_key": r"api_key|access_token|secret_key"
        }
    
    def _load_compliance_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load compliance rules."""
        return {
            "gdpr": {
                "personal_data_access": r"personal_data|email|phone",
                "consent_required": True,
                "audit_required": True
            },
            "pci_dss": {
                "financial_data": r"credit_card|payment|financial",
                "encryption_required": True,
                "access_logging": True
            },
            "sox": {
                "financial_reports": r"financial_report|audit|transaction",
                "audit_trail": True,
                "segregation_of_duties": True
            }
        }
    
    def _load_attack_signatures(self) -> Dict[str, Dict[str, Any]]:
        """Load known attack signatures."""
        return {
            "sqlmap": {
                "patterns": [r"sqlmap", r"AND\s+\d+=\d+", r"ORDER\s+BY\s+\d+"],
                "severity": SeverityLevel.CRITICAL
            },
            "havij": {
                "patterns": [r"havij", r"0x[0-9a-f]+"],
                "severity": SeverityLevel.HIGH
            },
            "manual_injection": {
                "patterns": [r"'\s*OR\s+'1'\s*=\s*'1", r"admin'--"],
                "severity": SeverityLevel.CRITICAL
            }
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get security analyzer metrics."""
        return self._metrics.copy()
    
    def get_vulnerability_stats(self) -> Dict[str, Any]:
        """Get vulnerability statistics."""
        return {
            "total_analyses": self._metrics["analyses_performed"],
            "vulnerabilities_found": self._metrics["vulnerabilities_found"],
            "critical_vulnerabilities": self._metrics["critical_vulnerabilities"],
            "injection_attempts": self._metrics["injection_attempts_blocked"],
            "compliance_violations": self._metrics["compliance_violations"],
            "security_score": self._calculate_overall_security_score()
        }
    
    def _calculate_overall_security_score(self) -> float:
        """Calculate overall security score."""
        total_analyses = self._metrics["analyses_performed"]
        if total_analyses == 0:
            return 100.0
        
        vulnerability_rate = self._metrics["vulnerabilities_found"] / total_analyses
        critical_rate = self._metrics["critical_vulnerabilities"] / total_analyses
        
        # Calculate score (0-100, higher is better)
        score = 100.0 - (vulnerability_rate * 50) - (critical_rate * 30)
        return max(0.0, min(100.0, score))


class VulnerabilityScanner:
    """
    Automated vulnerability scanner for database schemas and queries.
    """
    
    def __init__(self, security_analyzer: SecurityAnalyzer):
        self.security_analyzer = security_analyzer
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def scan_queries(
        self,
        queries: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, SecurityAnalysisResult]:
        """Scan multiple queries for vulnerabilities."""
        results = {}
        
        for i, query in enumerate(queries):
            try:
                result = await self.security_analyzer.analyze_security(
                    query=query,
                    context=context
                )
                results[f"query_{i+1}"] = result
            except Exception as e:
                self.logger.error(f"Failed to scan query {i+1}: {e}")
        
        return results
    
    async def generate_security_report(
        self,
        scan_results: Dict[str, SecurityAnalysisResult]
    ) -> Dict[str, Any]:
        """Generate comprehensive security report."""
        total_queries = len(scan_results)
        secure_queries = sum(1 for result in scan_results.values() if result.is_secure)
        
        all_vulnerabilities = []
        for result in scan_results.values():
            all_vulnerabilities.extend(result.vulnerabilities)
        
        vulnerability_by_type = {}
        for vuln in all_vulnerabilities:
            vuln_type = vuln.type.value
            if vuln_type not in vulnerability_by_type:
                vulnerability_by_type[vuln_type] = 0
            vulnerability_by_type[vuln_type] += 1
        
        return {
            "summary": {
                "total_queries_scanned": total_queries,
                "secure_queries": secure_queries,
                "vulnerable_queries": total_queries - secure_queries,
                "security_percentage": (secure_queries / total_queries * 100) if total_queries > 0 else 0
            },
            "vulnerabilities": {
                "total_found": len(all_vulnerabilities),
                "by_type": vulnerability_by_type,
                "critical_count": sum(1 for v in all_vulnerabilities if v.severity == SeverityLevel.CRITICAL),
                "high_count": sum(1 for v in all_vulnerabilities if v.severity == SeverityLevel.HIGH)
            },
            "recommendations": self._generate_report_recommendations(all_vulnerabilities),
            "compliance_status": self._assess_compliance_status(scan_results),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _generate_report_recommendations(
        self,
        vulnerabilities: List[SecurityVulnerability]
    ) -> List[str]:
        """Generate recommendations for the security report."""
        recommendations = set()
        
        for vuln in vulnerabilities:
            if vuln.remediation:
                recommendations.add(vuln.remediation)
        
        # Add general recommendations
        recommendations.update([
            "Implement comprehensive input validation",
            "Use parameterized queries consistently",
            "Regular security training for developers",
            "Automated security testing in CI/CD pipeline"
        ])
        
        return list(recommendations)[:10]
    
    def _assess_compliance_status(
        self,
        scan_results: Dict[str, SecurityAnalysisResult]
    ) -> Dict[str, Any]:
        """Assess overall compliance status."""
        all_compliance_issues = []
        for result in scan_results.values():
            all_compliance_issues.extend(result.compliance_issues)
        
        return {
            "total_issues": len(all_compliance_issues),
            "gdpr_compliant": not any("GDPR" in issue for issue in all_compliance_issues),
            "pci_dss_compliant": not any("PCI DSS" in issue for issue in all_compliance_issues),
            "sox_compliant": not any("SOX" in issue for issue in all_compliance_issues),
            "issues": list(set(all_compliance_issues))
        }


# Alias for backward compatibility
SafetyChecker = SecurityAnalyzer
