"""
AI Agents Service for AutoOps
Multi-agent system for intelligent patch management and remediation
Uses AWS Bedrock (with optional CrewAI enhancement)
"""
import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import CrewAI (optional)
try:
    from crewai import Agent, Task, Crew, Process
    from langchain_aws import ChatBedrock
    CREWAI_AVAILABLE = True
    logger.info("CrewAI available - using multi-agent system")
except ImportError:
    CREWAI_AVAILABLE = False
    logger.warning("CrewAI not available - using simplified AI service")

class AIAgentsService:
    """
    Multi-agent AI system for AutoOps
    Coordinates 5 specialized agents for patch management
    """
    
    def __init__(self, bedrock_service=None):
        self.bedrock_service = bedrock_service
        self.agents_initialized = False
        
        if CREWAI_AVAILABLE:
            try:
                self._initialize_crewai_agents()
                self.agents_initialized = True
                logger.info("✅ CrewAI agents initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize CrewAI agents: {e}")
                self.agents_initialized = False
        else:
            logger.info("Using simplified AI agent implementation")
    
    def _initialize_crewai_agents(self):
        """Initialize CrewAI agents with AWS Bedrock"""
        if not CREWAI_AVAILABLE:
            return
        
        # Initialize Bedrock LLM for CrewAI
        region = os.getenv('AWS_REGION', 'us-east-1')
        model_id = os.getenv('BEDROCK_MODEL', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
        
        try:
            self.llm = ChatBedrock(
                model_id=model_id,
                region_name=region,
                model_kwargs={
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            )
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock LLM: {e}")
            self.llm = None
            return
        
        # Agent 1: Patch Prioritization Agent
        self.patch_prioritization_agent = Agent(
            role='Patch Prioritization Specialist',
            goal='Analyze and prioritize patches based on severity, business impact, and risk',
            backstory="""You are an expert in cybersecurity patch management with deep knowledge 
            of CVE scoring, business risk assessment, and operational impact analysis. You excel at 
            determining which patches should be deployed first based on multiple factors.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agent 2: Alert Correlation Agent
        self.alert_correlation_agent = Agent(
            role='Alert Correlation Analyst',
            goal='Correlate related alerts and identify root causes to reduce alert fatigue',
            backstory="""You are a seasoned security analyst who specializes in pattern recognition 
            and alert correlation. You can identify when multiple alerts are symptoms of the same 
            underlying issue and provide actionable insights.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agent 3: Remediation Decision Agent
        self.remediation_agent = Agent(
            role='Remediation Strategy Expert',
            goal='Determine the best remediation approach for vulnerabilities and incidents',
            backstory="""You are an expert in incident response and remediation strategies. You 
            evaluate multiple remediation options, consider business continuity, and recommend 
            the optimal approach balancing security and operational needs.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agent 4: Root Cause Analysis Agent
        self.root_cause_agent = Agent(
            role='Root Cause Analysis Investigator',
            goal='Identify underlying causes of security issues and recommend preventive measures',
            backstory="""You are a systems thinking expert who excels at finding root causes rather 
            than treating symptoms. You analyze patterns, identify systemic weaknesses, and propose 
            long-term solutions.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agent 5: Learning & Optimization Agent
        self.learning_agent = Agent(
            role='Continuous Learning Specialist',
            goal='Learn from deployment outcomes and optimize future decisions',
            backstory="""You are a machine learning expert who analyzes historical data to improve 
            future decisions. You identify what worked, what didn't, and adapt strategies accordingly 
            to continuously improve the system's performance.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        logger.info("All 5 AI agents initialized successfully")
    
    def prioritize_patches(self, patches: List[Dict], context: Optional[Dict] = None) -> Dict:
        """
        Use AI agents to prioritize patches
        
        Args:
            patches: List of patch dictionaries
            context: Optional business context
            
        Returns:
            Prioritized patches with AI reasoning
        """
        if CREWAI_AVAILABLE and self.agents_initialized and self.llm:
            return self._crewai_prioritize_patches(patches, context)
        else:
            return self._simple_prioritize_patches(patches, context)
    
    def _crewai_prioritize_patches(self, patches: List[Dict], context: Optional[Dict]) -> Dict:
        """Use CrewAI for patch prioritization"""
        try:
            # Create task for patch prioritization
            patches_summary = "\n".join([
                f"- {p.get('title')} | Severity: {p.get('severity')} | CVEs: {len(p.get('relatedCVEs', []))}"
                for p in patches[:10]
            ])
            
            task = Task(
                description=f"""Analyze and prioritize these patches for deployment:
                
{patches_summary}

Context: {json.dumps(context) if context else 'Standard production environment'}

Provide a prioritized list with:
1. Priority ranking (1-10)
2. Deployment window recommendation
3. Risk assessment
4. Business justification

Format as JSON array.""",
                agent=self.patch_prioritization_agent,
                expected_output="JSON array of prioritized patches with scores and recommendations"
            )
            
            # Create crew and execute
            crew = Crew(
                agents=[self.patch_prioritization_agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            return {
                'prioritized_patches': self._parse_crew_output(result, patches),
                'ai_generated': True,
                'model': 'CrewAI + Bedrock Claude 3.5',
                'agent': 'Patch Prioritization Specialist'
            }
            
        except Exception as e:
            logger.error(f"CrewAI prioritization failed: {e}")
            return self._simple_prioritize_patches(patches, context)
    
    def _simple_prioritize_patches(self, patches: List[Dict], context: Optional[Dict]) -> Dict:
        """Simplified prioritization using Bedrock directly"""
        if self.bedrock_service:
            try:
                result = self.bedrock_service.prioritize_patches(patches, context)
                result['agent'] = 'Simplified AI'
                return result
            except:
                pass
        
        # Fallback to rule-based
        severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        sorted_patches = sorted(
            patches,
            key=lambda p: (
                severity_order.get(p.get('severity', 'MEDIUM'), 0),
                len(p.get('relatedCVEs', [])),
                -len(p.get('affectedDevices', []))
            ),
            reverse=True
        )
        
        return {
            'prioritized_patches': sorted_patches,
            'ai_generated': False,
            'model': 'Rule-based',
            'agent': 'Simple Priority Sort'
        }
    
    def correlate_alerts(self, alerts: List[Dict]) -> Dict:
        """Correlate related alerts to reduce noise"""
        if CREWAI_AVAILABLE and self.agents_initialized and self.llm:
            return self._crewai_correlate_alerts(alerts)
        else:
            return self._simple_correlate_alerts(alerts)
    
    def _crewai_correlate_alerts(self, alerts: List[Dict]) -> Dict:
        """Use CrewAI for alert correlation"""
        try:
            alerts_summary = "\n".join([
                f"- Alert {a.get('id')}: {a.get('title')} | Device: {a.get('deviceName')} | Severity: {a.get('severity')}"
                for a in alerts[:20]
            ])
            
            task = Task(
                description=f"""Analyze these alerts and identify correlations:

{alerts_summary}

Find:
1. Groups of related alerts
2. Common root causes
3. Priority incidents
4. Recommended actions

Provide analysis as JSON.""",
                agent=self.alert_correlation_agent,
                expected_output="JSON with alert correlations and root cause analysis"
            )
            
            crew = Crew(
                agents=[self.alert_correlation_agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            return {
                'correlations': self._parse_crew_output(result, alerts),
                'total_alerts': len(alerts),
                'ai_generated': True,
                'model': 'CrewAI + Bedrock Claude 3.5',
                'agent': 'Alert Correlation Analyst'
            }
            
        except Exception as e:
            logger.error(f"CrewAI correlation failed: {e}")
            return self._simple_correlate_alerts(alerts)
    
    def _simple_correlate_alerts(self, alerts: List[Dict]) -> Dict:
        """Simple alert correlation by device and severity"""
        correlations = {}
        
        for alert in alerts:
            device_id = alert.get('deviceId', 'unknown')
            severity = alert.get('severity', 'MEDIUM')
            
            key = f"{device_id}_{severity}"
            if key not in correlations:
                correlations[key] = {
                    'device': alert.get('deviceName', device_id),
                    'severity': severity,
                    'alerts': [],
                    'count': 0
                }
            
            correlations[key]['alerts'].append(alert)
            correlations[key]['count'] += 1
        
        # Filter to only show correlated alerts (2+)
        correlated = {k: v for k, v in correlations.items() if v['count'] >= 2}
        
        return {
            'correlations': list(correlated.values()),
            'total_alerts': len(alerts),
            'correlated_groups': len(correlated),
            'ai_generated': False,
            'model': 'Rule-based',
            'agent': 'Simple Grouping'
        }
    
    def decide_remediation(self, vulnerability: Dict, options: List[Dict]) -> Dict:
        """Decide best remediation strategy"""
        if CREWAI_AVAILABLE and self.agents_initialized and self.llm:
            return self._crewai_decide_remediation(vulnerability, options)
        else:
            return self._simple_decide_remediation(vulnerability, options)
    
    def _crewai_decide_remediation(self, vulnerability: Dict, options: List[Dict]) -> Dict:
        """Use CrewAI for remediation decision"""
        try:
            options_summary = "\n".join([
                f"{i+1}. {opt.get('name')}: {opt.get('description')}"
                for i, opt in enumerate(options)
            ])
            
            task = Task(
                description=f"""Choose the best remediation for this vulnerability:

Vulnerability: {vulnerability.get('cveId')} - {vulnerability.get('description')}
Severity: {vulnerability.get('severity')}
CVSS Score: {vulnerability.get('cvssScore')}

Options:
{options_summary}

Provide:
1. Recommended option
2. Justification
3. Risk assessment
4. Implementation steps
5. Rollback plan

Format as JSON.""",
                agent=self.remediation_agent,
                expected_output="JSON with remediation decision and detailed plan"
            )
            
            crew = Crew(
                agents=[self.remediation_agent, self.root_cause_agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            return {
                'decision': self._parse_crew_output(result, options),
                'ai_generated': True,
                'model': 'CrewAI + Bedrock Claude 3.5',
                'agents': ['Remediation Expert', 'Root Cause Analyst']
            }
            
        except Exception as e:
            logger.error(f"CrewAI remediation decision failed: {e}")
            return self._simple_decide_remediation(vulnerability, options)
    
    def _simple_decide_remediation(self, vulnerability: Dict, options: List[Dict]) -> Dict:
        """Simple remediation decision based on severity"""
        cvss_score = vulnerability.get('cvssScore', 5.0)
        severity = vulnerability.get('severity', 'MEDIUM')
        
        if cvss_score >= 9.0 or severity == 'CRITICAL':
            recommendation = options[0] if options else {'name': 'Immediate patching'}
            urgency = 'IMMEDIATE'
        elif cvss_score >= 7.0 or severity == 'HIGH':
            recommendation = options[0] if options else {'name': 'Scheduled patching'}
            urgency = 'URGENT'
        else:
            recommendation = options[-1] if options else {'name': 'Next maintenance window'}
            urgency = 'NORMAL'
        
        return {
            'decision': {
                'recommended_option': recommendation,
                'urgency': urgency,
                'justification': f"Based on CVSS score of {cvss_score} and {severity} severity",
                'confidence': 0.75
            },
            'ai_generated': False,
            'model': 'Rule-based'
        }
    
    def learn_from_outcome(self, action: Dict, outcome: Dict) -> Dict:
        """Learn from deployment outcomes"""
        if CREWAI_AVAILABLE and self.agents_initialized and self.llm:
            return self._crewai_learn_from_outcome(action, outcome)
        else:
            return self._simple_learn_from_outcome(action, outcome)
    
    def _crewai_learn_from_outcome(self, action: Dict, outcome: Dict) -> Dict:
        """Use CrewAI learning agent"""
        try:
            task = Task(
                description=f"""Analyze this deployment outcome and extract learnings:

Action Taken: {json.dumps(action, indent=2)}
Outcome: {json.dumps(outcome, indent=2)}

Provide:
1. What went well
2. What could be improved
3. Recommendations for future similar cases
4. Updated strategy

Format as JSON.""",
                agent=self.learning_agent,
                expected_output="JSON with learnings and recommendations"
            )
            
            crew = Crew(
                agents=[self.learning_agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            return {
                'learnings': self._parse_crew_output(result, {}),
                'ai_generated': True,
                'model': 'CrewAI + Bedrock Claude 3.5',
                'agent': 'Learning Specialist'
            }
            
        except Exception as e:
            logger.error(f"CrewAI learning failed: {e}")
            return self._simple_learn_from_outcome(action, outcome)
    
    def _simple_learn_from_outcome(self, action: Dict, outcome: Dict) -> Dict:
        """Simple outcome tracking"""
        success = outcome.get('status') == 'SUCCESS'
        
        return {
            'learnings': {
                'success': success,
                'timestamp': datetime.utcnow().isoformat(),
                'action_type': action.get('type'),
                'outcome_status': outcome.get('status'),
                'note': 'Outcome recorded for future analysis'
            },
            'ai_generated': False,
            'model': 'Simple tracking'
        }
    
    def _parse_crew_output(self, result, fallback_data):
        """Parse CrewAI output safely"""
        try:
            if hasattr(result, 'raw_output'):
                output = result.raw_output
            elif hasattr(result, 'output'):
                output = result.output
            else:
                output = str(result)
            
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}|\[.*\]', output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return {'raw_output': output, 'fallback': fallback_data}
        except:
            return fallback_data
    
    def get_agent_status(self) -> Dict:
        """Get status of AI agents"""
        return {
            'crewai_available': CREWAI_AVAILABLE,
            'agents_initialized': self.agents_initialized,
            'bedrock_service': self.bedrock_service is not None,
            'agents': {
                'patch_prioritization': self.agents_initialized,
                'alert_correlation': self.agents_initialized,
                'remediation_decision': self.agents_initialized,
                'root_cause_analysis': self.agents_initialized,
                'learning_optimization': self.agents_initialized
            } if self.agents_initialized else {},
            'mode': 'CrewAI Multi-Agent' if self.agents_initialized else 'Simplified AI'
        }
