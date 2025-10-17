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
        """Fetch device inventory from SuperOps"""
        query = gql("""
            query GetDevices($filters: DeviceFilterInput) {
                devices(filters: $filters) {
                    id
                    name
                    type
                    operatingSystem
                    ipAddress
                    macAddress
                    lastSeenAt
                    client {
                        id
                        name
                    }
                    site {
                        id
                        name
                    }
                }
            }
        """)

        try:
            result = self.client.execute(query, variable_values={'filters': filters})
            return result.get('devices', [])
        except Exception as e:
            logger.error(f"Error fetching device inventory: {e}")
            raise

    def get_patch_status(self, device_ids: Optional[List[str]] = None) -> List[Dict]:
        """Get patch status for devices"""
        query = gql("""
            query GetPatchStatus($deviceIds: [ID!]) {
                patchStatus(deviceIds: $deviceIds) {
                    deviceId
                    deviceName
                    totalPatches
                    installedPatches
                    pendingPatches
                    failedPatches
                    lastPatchDate
                    complianceStatus
                    criticalPatches {
                        id
                        title
                        severity
                        cveId
                        publishDate
                    }
                }
            }
        """)

        try:
            result = self.client.execute(query, variable_values={'deviceIds': device_ids})
            return result.get('patchStatus', [])
        except Exception as e:
            logger.error(f"Error fetching patch status: {e}")
            raise

    def get_alerts(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Fetch active alerts"""
        query = gql("""
            query GetAlerts($filters: AlertFilterInput) {
                alerts(filters: $filters) {
                    id
                    title
                    description
                    severity
                    status
                    source
                    deviceId
                    deviceName
                    createdAt
                    updatedAt
                    metadata
                }
            }
        """)

        try:
            result = self.client.execute(query, variable_values={'filters': filters})
            return result.get('alerts', [])
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
