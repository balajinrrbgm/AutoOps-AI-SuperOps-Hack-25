"""
AWS Bedrock AI Service
Handles AI-powered analysis using AWS Bedrock Claude models
"""
import os
import json
import logging
from typing import Dict, List, Optional

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logging.warning("boto3 not available - AWS Bedrock features will be disabled")

logger = logging.getLogger(__name__)

class BedrockAIService:
    def __init__(self):
        if not BOTO3_AVAILABLE:
            logger.warning("Bedrock service initialized without boto3")
            self.client = None
            return
            
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.model_id = os.getenv('BEDROCK_MODEL', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
        
        try:
            self.client = boto3.client('bedrock-runtime', region_name=self.region)
            logger.info(f"✅ Bedrock client initialized with model: {self.model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            self.client = None

    def analyze_patch(self, patch_data: Dict) -> Dict:
        """
        Analyze a patch using AI to determine priority, risks, and recommendations
        
        Args:
            patch_data: Dictionary containing patch information
            
        Returns:
            Dictionary with AI analysis results
        """
        if not self.client:
            return self._mock_analysis(patch_data)
        
        try:
            # Prepare the prompt for Claude
            prompt = self._create_patch_analysis_prompt(patch_data)
            
            # Call Bedrock
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            analysis_text = response_body['content'][0]['text']
            
            # Structure the analysis
            return self._parse_analysis(analysis_text, patch_data)
            
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            return self._mock_analysis(patch_data)
        except Exception as e:
            logger.error(f"Error analyzing patch with Bedrock: {e}")
            return self._mock_analysis(patch_data)

    def analyze_vulnerability(self, cve_data: Dict) -> Dict:
        """Analyze a vulnerability and provide recommendations"""
        if not self.client:
            return self._mock_vulnerability_analysis(cve_data)
        
        try:
            prompt = self._create_vulnerability_analysis_prompt(cve_data)
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 800,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            response_body = json.loads(response['body'].read())
            analysis_text = response_body['content'][0]['text']
            
            return self._parse_vulnerability_analysis(analysis_text, cve_data)
            
        except Exception as e:
            logger.error(f"Error analyzing vulnerability: {e}")
            return self._mock_vulnerability_analysis(cve_data)

    def prioritize_patches(self, patches: List[Dict], context: Optional[Dict] = None) -> List[Dict]:
        """
        Prioritize a list of patches using AI
        
        Args:
            patches: List of patch dictionaries
            context: Optional context (business impact, maintenance windows, etc.)
            
        Returns:
            Sorted list of patches with priority scores
        """
        if not self.client:
            return self._mock_prioritization(patches)
        
        try:
            prompt = self._create_prioritization_prompt(patches, context)
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1500,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            response_body = json.loads(response['body'].read())
            analysis_text = response_body['content'][0]['text']
            
            return self._parse_prioritization(analysis_text, patches)
            
        except Exception as e:
            logger.error(f"Error prioritizing patches: {e}")
            return self._mock_prioritization(patches)

    def _create_patch_analysis_prompt(self, patch_data: Dict) -> str:
        """Create a prompt for patch analysis"""
        return f"""You are a cybersecurity expert analyzing a software patch. Provide a comprehensive analysis in JSON format.

Patch Information:
- Title: {patch_data.get('title')}
- Description: {patch_data.get('description')}
- Severity: {patch_data.get('severity')}
- CVEs: {patch_data.get('relatedCVEs', [])}
- Affected Devices: {len(patch_data.get('affectedDevices', []))}
- Requires Reboot: {patch_data.get('requiresReboot')}

Provide analysis in this JSON format:
{{
    "priority_score": <1-10>,
    "deployment_recommendation": "<IMMEDIATE|SCHEDULED|DEFERRED>",
    "risk_assessment": {{
        "security_risk": "<HIGH|MEDIUM|LOW>",
        "business_impact": "<CRITICAL|MODERATE|MINIMAL>",
        "deployment_risk": "<HIGH|MEDIUM|LOW>"
    }},
    "recommended_action": "<action description>",
    "testing_requirements": "<testing needs>",
    "rollback_plan": "<rollback strategy>",
    "estimated_downtime": "<time estimate>",
    "key_considerations": ["<consideration 1>", "<consideration 2>", "..."]
}}

Respond only with the JSON object, no additional text."""

    def _create_vulnerability_analysis_prompt(self, cve_data: Dict) -> str:
        """Create a prompt for vulnerability analysis"""
        return f"""Analyze this CVE vulnerability and provide recommendations in JSON format.

CVE Information:
- ID: {cve_data.get('cveId')}
- CVSS Score: {cve_data.get('cvssScore')}
- Description: {cve_data.get('description')}
- Affected Systems: {cve_data.get('affectedDevices', [])}

Respond with JSON:
{{
    "severity_analysis": "<explanation>",
    "exploit_likelihood": "<HIGH|MEDIUM|LOW>",
    "remediation_urgency": "<IMMEDIATE|URGENT|MODERATE|LOW>",
    "recommended_actions": ["<action 1>", "<action 2>"],
    "compensating_controls": ["<control 1>", "<control 2>"],
    "business_context": "<impact on operations>"
}}

Respond only with JSON, no additional text."""

    def _create_prioritization_prompt(self, patches: List[Dict], context: Optional[Dict]) -> str:
        """Create a prompt for patch prioritization"""
        patches_summary = [
            f"- {p.get('title')} (Severity: {p.get('severity')}, CVEs: {len(p.get('relatedCVEs', []))})"
            for p in patches[:10]  # Limit to first 10
        ]
        
        return f"""Prioritize these patches for deployment. Consider severity, CVEs, and business impact.

Patches:
{chr(10).join(patches_summary)}

Context: {json.dumps(context) if context else 'Standard business environment'}

Respond with JSON array of patch IDs in priority order:
{{
    "prioritized_patches": [
        {{
            "patch_id": "<id>",
            "priority_score": <1-10>,
            "deployment_window": "<IMMEDIATE|THIS_WEEK|THIS_MONTH>",
            "rationale": "<reason>"
        }}
    ]
}}

Respond only with JSON."""

    def _parse_analysis(self, analysis_text: str, patch_data: Dict) -> Dict:
        """Parse AI analysis response"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                analysis['ai_generated'] = True
                analysis['model'] = self.model_id
                return analysis
        except:
            pass
        
        # Fallback to mock if parsing fails
        return self._mock_analysis(patch_data)

    def _parse_vulnerability_analysis(self, analysis_text: str, cve_data: Dict) -> Dict:
        """Parse vulnerability analysis response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return self._mock_vulnerability_analysis(cve_data)

    def _parse_prioritization(self, analysis_text: str, patches: List[Dict]) -> List[Dict]:
        """Parse prioritization response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result.get('prioritized_patches', patches)
        except:
            pass
        
        return self._mock_prioritization(patches)

    def _mock_analysis(self, patch_data: Dict) -> Dict:
        """Generate mock analysis when Bedrock is unavailable"""
        severity = patch_data.get('severity', 'MEDIUM')
        has_cves = len(patch_data.get('relatedCVEs', [])) > 0
        
        return {
            "priority_score": 9 if severity == 'CRITICAL' else 7 if severity == 'HIGH' else 5,
            "deployment_recommendation": "IMMEDIATE" if severity == 'CRITICAL' else "SCHEDULED",
            "risk_assessment": {
                "security_risk": severity,
                "business_impact": "CRITICAL" if has_cves else "MODERATE",
                "deployment_risk": "HIGH" if patch_data.get('requiresReboot') else "MEDIUM"
            },
            "recommended_action": f"Deploy during next maintenance window. Test on development systems first.",
            "testing_requirements": "Verify application functionality after deployment",
            "rollback_plan": "Maintain system snapshot for quick rollback if needed",
            "estimated_downtime": "15-30 minutes" if patch_data.get('requiresReboot') else "< 5 minutes",
            "key_considerations": [
                "Patch addresses known security vulnerabilities",
                "Minimal compatibility issues expected",
                "Rollback procedure available"
            ],
            "ai_generated": False,
            "model": "mock"
        }

    def _mock_vulnerability_analysis(self, cve_data: Dict) -> Dict:
        """Mock vulnerability analysis"""
        score = cve_data.get('cvssScore', 5.0)
        
        return {
            "severity_analysis": f"CVSS score of {score} indicates {'critical' if score >= 9 else 'high' if score >= 7 else 'medium'} severity",
            "exploit_likelihood": "HIGH" if score >= 9 else "MEDIUM" if score >= 7 else "LOW",
            "remediation_urgency": "IMMEDIATE" if score >= 9 else "URGENT" if score >= 7 else "MODERATE",
            "recommended_actions": [
                "Apply security patches immediately",
                "Monitor for exploitation attempts",
                "Review firewall rules"
            ],
            "compensating_controls": [
                "Network segmentation",
                "Enhanced monitoring",
                "Access restrictions"
            ],
            "business_context": "Potential for data breach or service disruption",
            "ai_generated": False
        }

    def _mock_prioritization(self, patches: List[Dict]) -> List[Dict]:
        """Mock patch prioritization"""
        severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        
        prioritized = sorted(
            patches,
            key=lambda p: (
                severity_order.get(p.get('severity', 'MEDIUM'), 0),
                len(p.get('relatedCVEs', [])),
                -len(p.get('affectedDevices', []))
            ),
            reverse=True
        )
        
        return prioritized
