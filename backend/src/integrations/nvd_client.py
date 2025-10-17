"""
NIST NVD API Client
Fetches vulnerability data from the National Vulnerability Database
"""
import os
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class NVDClient:
    def __init__(self):
        self.api_key = os.getenv('NVD_API_KEY')  # Optional but recommended
        self.base_url = 'https://services.nvd.nist.gov/rest/json/cves/2.0'

        # Rate limiting: 6 seconds without API key, 0.6 with key
        self.delay = 0.6 if self.api_key else 6.0
        self.last_request_time = 0

    def _rate_limit(self):
        """Implement rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, params: Dict) -> Dict:
        """Make API request with rate limiting"""
        self._rate_limit()

        headers = {}
        if self.api_key:
            headers['apiKey'] = self.api_key

        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"NVD API request failed: {e}")
            raise

    def get_cve_by_id(self, cve_id: str) -> Optional[Dict]:
        """Get specific CVE by ID"""
        params = {'cveId': cve_id}
        result = self._make_request(params)

        vulnerabilities = result.get('vulnerabilities', [])
        return vulnerabilities[0] if vulnerabilities else None

    def search_recent_cves(self, days: int = 7) -> List[Dict]:
        """Search for CVEs published in recent days"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        params = {
            'pubStartDate': start_date.strftime('%Y-%m-%dT%H:%M:%S.000'),
            'pubEndDate': end_date.strftime('%Y-%m-%dT%H:%M:%S.000'),
            'resultsPerPage': 100
        }

        result = self._make_request(params)
        return result.get('vulnerabilities', [])

    def search_by_cpe(self, cpe_name: str) -> List[Dict]:
        """Search CVEs by CPE name"""
        params = {
            'cpeName': cpe_name,
            'resultsPerPage': 100
        }

        result = self._make_request(params)
        return result.get('vulnerabilities', [])

    def search_by_keyword(self, keyword: str, severity: Optional[str] = None) -> List[Dict]:
        """Search CVEs by keyword and optionally filter by severity"""
        params = {
            'keywordSearch': keyword,
            'resultsPerPage': 100
        }

        if severity:
            params['cvssV3Severity'] = severity.upper()

        result = self._make_request(params)
        return result.get('vulnerabilities', [])

    def get_severity_score(self, cve_data: Dict) -> Dict:
        """Extract severity and score from CVE data"""
        cve = cve_data.get('cve', {})
        metrics = cve.get('metrics', {})

        # Try CVSS v3.1 first, then v3.0, then v2.0
        if 'cvssMetricV31' in metrics:
            cvss = metrics['cvssMetricV31'][0]['cvssData']
            return {
                'version': '3.1',
                'score': cvss.get('baseScore'),
                'severity': cvss.get('baseSeverity'),
                'vector': cvss.get('vectorString')
            }
        elif 'cvssMetricV30' in metrics:
            cvss = metrics['cvssMetricV30'][0]['cvssData']
            return {
                'version': '3.0',
                'score': cvss.get('baseScore'),
                'severity': cvss.get('baseSeverity'),
                'vector': cvss.get('vectorString')
            }
        elif 'cvssMetricV2' in metrics:
            cvss = metrics['cvssMetricV2'][0]['cvssData']
            return {
                'version': '2.0',
                'score': cvss.get('baseScore'),
                'severity': cvss.get('severity'),
                'vector': cvss.get('vectorString')
            }

        return {'version': None, 'score': None, 'severity': 'UNKNOWN', 'vector': None}
