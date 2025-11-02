"""
SuperOps.ai API Client
Handles authentication and API calls to SuperOps platform
"""
import os
import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class SuperOpsClient:
    def __init__(self):
        self.api_token = os.getenv('SUPEROPS_API_TOKEN')
        self.subdomain = os.getenv('SUPEROPS_SUBDOMAIN')
        self.data_center = os.getenv('SUPEROPS_DATA_CENTER', 'us')

        # Determine base URL based on data center
        if self.data_center == 'eu':
            self.base_url = 'https://api-eu.superops.ai/graphql'
        else:
            self.base_url = 'https://api.superops.ai/graphql'

        # Configure GraphQL client
        transport = RequestsHTTPTransport(
            url=self.base_url,
            headers={
                'Authorization': f'Bearer {self.api_token}',
                'CustomerSubDomain': self.subdomain,
                'Content-Type': 'application/json'
            },
            verify=True
        )

        self.client = Client(
            transport=transport,
            fetch_schema_from_transport=False
        )

    def get_device_inventory(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Fetch device inventory from SuperOps using simplified query"""
        # Simplified GraphQL query without complex filters
        query = gql("""
            query {
                devices {
                    nodes {
                        id
                        name
                        deviceType
                        osName
                        primaryIpAddress
                        macAddress
                        lastSeenAt
                        clientName
                        siteName
                    }
                }
            }
        """)

        try:
            result = self.client.execute(query)
            devices = result.get('devices', {}).get('nodes', [])
            
            # Transform to expected format
            return [{
                'id': d.get('id'),
                'name': d.get('name'),
                'type': d.get('deviceType', 'Unknown'),
                'operatingSystem': d.get('osName', 'Unknown'),
                'ipAddress': d.get('primaryIpAddress'),
                'macAddress': d.get('macAddress'),
                'lastSeenAt': d.get('lastSeenAt'),
                'client': {'name': d.get('clientName', 'Unknown')},
                'site': {'name': d.get('siteName', 'Unknown')}
            } for d in devices]
        except Exception as e:
            logger.error(f"Error fetching device inventory: {e}")
            raise

    def get_patch_status(self, device_ids: Optional[List[str]] = None) -> List[Dict]:
        """Get patch status for devices using simplified query"""
        # Simplified query without variables
        query = gql("""
            query {
                patches {
                    nodes {
                        id
                        title
                        description
                        severity
                        category
                        releaseDate
                        status
                        kbArticleId
                        affectedDeviceCount
                    }
                }
            }
        """)

        try:
            result = self.client.execute(query)
            patches = result.get('patches', {}).get('nodes', [])
            
            # Transform to expected format
            return [{
                'id': p.get('id'),
                'title': p.get('title'),
                'description': p.get('description'),
                'severity': p.get('severity', 'MEDIUM').upper(),
                'releaseDate': p.get('releaseDate'),
                'status': p.get('status', 'AVAILABLE').upper(),
                'cveId': None,  # May not be available in all patches
                'relatedCVEs': [],
                'affectedDevices': [],
                'size': 'Unknown',
                'vendor': 'Various',
                'requiresReboot': False
            } for p in patches]
        except Exception as e:
            logger.error(f"Error fetching patch status: {e}")
            raise

    def get_alerts(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Fetch active alerts using simplified query"""
        # Simplified query
        query = gql("""
            query {
                alerts {
                    nodes {
                        id
                        title
                        description
                        severity
                        status
                        deviceId
                        deviceName
                        createdAt
                        updatedAt
                    }
                }
            }
        """)

        try:
            result = self.client.execute(query)
            alerts = result.get('alerts', {}).get('nodes', [])
            
            # Transform to expected format
            return [{
                'id': a.get('id'),
                'title': a.get('title'),
                'description': a.get('description'),
                'severity': a.get('severity', 'MEDIUM').upper(),
                'status': a.get('status', 'ACTIVE').upper(),
                'deviceId': a.get('deviceId'),
                'deviceName': a.get('deviceName'),
                'cveId': None,
                'createdAt': a.get('createdAt'),
                'acknowledgedAt': a.get('updatedAt') if a.get('status') == 'ACKNOWLEDGED' else None
            } for a in alerts]
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            raise

    def execute_script(self, device_id: str, script_name: str, 
                      variables: Optional[Dict] = None) -> Dict:
        """Execute a script on a device via SuperOps"""
        mutation = gql("""
            mutation ExecuteScript($input: ScriptExecutionInput!) {
                executeScript(input: $input) {
                    executionId
                    status
                    message
                }
            }
        """)

        input_data = {
            'deviceId': device_id,
            'scriptName': script_name,
            'variables': variables or {}
        }

        try:
            result = self.client.execute(mutation, variable_values={'input': input_data})
            return result.get('executeScript', {})
        except Exception as e:
            logger.error(f"Error executing script: {e}")
            raise

    def deploy_patch(self, device_ids: List[str], patch_ids: List[str], 
                    schedule: Optional[Dict] = None) -> Dict:
        """Deploy patches to specified devices"""
        mutation = gql("""
            mutation DeployPatch($input: PatchDeploymentInput!) {
                deployPatch(input: $input) {
                    deploymentId
                    status
                    message
                    scheduledFor
                }
            }
        """)

        input_data = {
            'deviceIds': device_ids,
            'patchIds': patch_ids,
            'schedule': schedule
        }

        try:
            result = self.client.execute(mutation, variable_values={'input': input_data})
            return result.get('deployPatch', {})
        except Exception as e:
            logger.error(f"Error deploying patch: {e}")
            raise

    def update_alert_status(self, alert_id: str, status: str, notes: Optional[str] = None) -> Dict:
        """Update alert status"""
        mutation = gql("""
            mutation UpdateAlert($input: AlertUpdateInput!) {
                updateAlert(input: $input) {
                    alertId
                    status
                    updatedAt
                }
            }
        """)

        input_data = {
            'alertId': alert_id,
            'status': status,
            'notes': notes
        }

        try:
            result = self.client.execute(mutation, variable_values={'input': input_data})
            return result.get('updateAlert', {})
        except Exception as e:
            logger.error(f"Error updating alert: {e}")
            raise
