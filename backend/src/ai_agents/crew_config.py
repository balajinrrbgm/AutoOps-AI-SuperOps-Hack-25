"""
CrewAI Configuration for AutoOps AI Agents
Defines specialized agents for patch management, alert correlation, and remediation
"""
import os
from crewai import Agent, Crew, Task, Process
from crewai.llm import LLM
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class AutoOpsAIAgents:
    def __init__(self):
        # Initialize AWS Bedrock LLM
        self.llm = LLM(
            model=os.getenv('BEDROCK_MODEL', 'bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_region_name=os.getenv('AWS_REGION', 'us-east-1')
        )

    def create_patch_prioritization_agent(self) -> Agent:
        """Agent responsible for analyzing and prioritizing patches"""
        return Agent(
            role='Patch Prioritization Specialist',
            goal='Analyze vulnerabilities and prioritize patches based on risk, criticality, and business impact',
            backstory='''You are an expert in vulnerability management and patch prioritization.
            You analyze CVE data, CVSS scores, exploit availability, and business context to 
            determine which patches should be deployed first. You consider system criticality,
            downtime windows, and potential impact on operations.''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def create_alert_correlation_agent(self) -> Agent:
        """Agent for correlating and deduplicating alerts"""
        return Agent(
            role='Alert Correlation Analyst',
            goal='Correlate related alerts, identify root causes, and reduce alert noise',
            backstory='''You are a skilled alert analyst who excels at finding patterns
            and connections between seemingly unrelated alerts. You can identify duplicate
            alerts, correlate events across systems, and trace issues back to their root cause.
            You help reduce alert fatigue by grouping related incidents.''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def create_remediation_decision_agent(self) -> Agent:
        """Agent for deciding remediation actions"""
        return Agent(
            role='Remediation Decision Maker',
            goal='Determine safe and effective remediation actions within policy guardrails',
            backstory='''You are an experienced operations engineer who makes intelligent
            decisions about how to remediate issues. You understand the impact of different
            remediation actions, can assess risk, and always operate within defined policy
            boundaries. You know when to restart services, apply patches, or escalate to humans.''',
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )

    def create_root_cause_analysis_agent(self) -> Agent:
        """Agent for performing root cause analysis"""
        return Agent(
            role='Root Cause Analysis Expert',
            goal='Investigate incidents deeply to identify true root causes',
            backstory='''You are a senior SRE with deep troubleshooting expertise.
            You analyze logs, metrics, events, and system behavior to identify the true
            root cause of incidents. You go beyond surface symptoms to find underlying
            issues and prevent recurrence.''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def create_learning_feedback_agent(self) -> Agent:
        """Agent for learning from feedback and improving decisions"""
        return Agent(
            role='Learning and Improvement Specialist',
            goal='Learn from past decisions and human feedback to improve future recommendations',
            backstory='''You are a machine learning specialist focused on continuous improvement.
            You analyze the outcomes of past decisions, incorporate human feedback, and adjust
            your models to make better recommendations over time. You identify patterns in
            successful and unsuccessful actions.''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def create_patch_prioritization_task(self, agent: Agent, context: Dict) -> Task:
        """Create task for patch prioritization"""
        return Task(
            description=f'''Analyze the following patches and prioritize them for deployment:

            Patches: {context.get('patches', [])}
            Systems: {context.get('systems', [])}
            Current CVE data: {context.get('cve_data', [])}

            Consider:
            1. CVSS scores and severity
            2. Exploit availability
            3. System criticality
            4. Business impact
            5. Maintenance windows

            Provide prioritized list with rationale for each decision.''',
            agent=agent,
            expected_output='Prioritized patch list with risk scores and deployment recommendations'
        )

    def create_alert_correlation_task(self, agent: Agent, context: Dict) -> Task:
        """Create task for alert correlation"""
        return Task(
            description=f'''Analyze and correlate the following alerts:

            Alerts: {context.get('alerts', [])}

            Identify:
            1. Duplicate or related alerts
            2. Potential root causes
            3. Alert clusters that indicate larger issues
            4. False positives that can be suppressed

            Provide correlated alert groups with root cause analysis.''',
            agent=agent,
            expected_output='Correlated alert groups with identified root causes and suppression recommendations'
        )

    def create_remediation_task(self, agent: Agent, context: Dict) -> Task:
        """Create task for remediation decision"""
        return Task(
            description=f'''Determine remediation actions for the following issue:

            Issue: {context.get('issue', {})}
            System state: {context.get('system_state', {})}
            Policy constraints: {context.get('policies', {})}

            Recommend:
            1. Immediate actions to take
            2. Risk assessment
            3. Rollback plan
            4. Approval requirements

            Ensure all actions comply with policy guardrails.''',
            agent=agent,
            expected_output='Detailed remediation plan with actions, risks, and rollback procedures'
        )

    def create_patch_crew(self, context: Dict) -> Crew:
        """Create a crew for patch management"""
        patch_agent = self.create_patch_prioritization_agent()
        remediation_agent = self.create_remediation_decision_agent()

        tasks = [
            self.create_patch_prioritization_task(patch_agent, context),
            self.create_remediation_task(remediation_agent, context)
        ]

        return Crew(
            agents=[patch_agent, remediation_agent],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )

    def create_alert_crew(self, context: Dict) -> Crew:
        """Create a crew for alert management"""
        correlation_agent = self.create_alert_correlation_agent()
        rca_agent = self.create_root_cause_analysis_agent()
        remediation_agent = self.create_remediation_decision_agent()

        tasks = [
            self.create_alert_correlation_task(correlation_agent, context),
            Task(
                description=f'Perform root cause analysis on correlated alerts',
                agent=rca_agent,
                expected_output='Root cause analysis with evidence and recommendations'
            ),
            self.create_remediation_task(remediation_agent, context)
        ]

        return Crew(
            agents=[correlation_agent, rca_agent, remediation_agent],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
