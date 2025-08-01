"""
Snyk Scan information
"""

from datetime import datetime
from typing import Optional, Union

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import epoch_to_datetime, get_current_datetime, is_valid_fqdn
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import Asset, AssetCategory, AssetStatus, AssetType, ImportValidater, IssueStatus, Vulnerability
from regscale.models.integration_models.flat_file_importer import FlatFileImporter


class Snyk(FlatFileImporter):
    """
    Snyk Scan information
    """

    def __init__(self, **kwargs):
        self.not_implemented_error = "Unsupported file type for Snyk integration. Only XLSX and JSON are supported."
        self.name = kwargs.get("name")
        self.auto_fixable = "AUTOFIXABLE"
        self.fmt = "%Y-%m-%d"
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        if "json" in kwargs.get("file_type", ""):
            self.project_name = "projectName"
            self.issue_severity = "severity"
            self.vuln_title = "title"
            self.required_headers = [
                "projectName",
                "vulnerabilities",
            ]
        else:
            self.project_name = "PROJECT_NAME"
            self.issue_severity = "ISSUE_SEVERITY"
            self.vuln_title = "PROBLEM_TITLE"
            self.required_headers = [
                self.project_name,
                self.issue_severity,
                self.vuln_title,
                self.auto_fixable,
            ]
        self.mapping_file = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")
        self.validater = ImportValidater(
            self.required_headers, kwargs.get("file_path"), self.mapping_file, self.disable_mapping
        )
        self.headers = self.validater.parsed_headers
        self.mapping = self.validater.mapping
        if "json" in kwargs.get("file_type", ""):
            asset_count = 1
            vuln_count = len(self.mapping.get_value(self.validater.data, "vulnerabilities", []))
        else:
            asset_count = None
            vuln_count = None
        logger = create_logger()
        self.logger = logger
        super().__init__(
            logger=logger,
            app=Application(),
            headers=self.headers,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            asset_count=asset_count,
            vuln_count=vuln_count,
            extra_headers_allowed=True,
            **kwargs,
        )

    def determine_first_seen(self, dat: dict) -> str:
        """
        Determine the first seen date of the vulnerability

        :param dict dat: Data row from CSV file
        :return: The first seen date as a string
        :rtype: str
        """
        return datetime.combine(
            datetime.strptime(epoch_to_datetime(self.create_epoch, self.fmt), self.dt_format),
            self.mapping.get_value(dat, "FIRST_INTRODUCED", datetime.now().time()),
        ).strftime(self.dt_format)

    def create_asset(self, dat: Optional[dict] = None) -> Union[Asset, IntegrationAsset]:
        """
        Create an asset from a row in the Snyk file

        :param Optional[dict] dat: Data row from XLSX file or JSON file, defaults to None
        :return: RegScale Asset if XLSX, IntegrationAsset if JSON
        :rtype: Union[Asset, IntegrationAsset]
        """
        if "json" in self.attributes.file_type:
            return self._parse_json_asset(data=dat)
        elif "xlsx" in self.attributes.file_type:
            return self._parse_xlsx_asset(dat)
        else:
            raise NotImplementedError(self.not_implemented_error)

    def _parse_xlsx_asset(self, dat: Optional[dict] = None) -> Asset:
        """
        Create an asset from a row in the Snyk file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale Asset object
        :rtype: Asset
        """
        name = self.extract_host(self.mapping.get_value(dat, self.project_name))
        valid_name = is_valid_fqdn(name)
        return Asset(
            **{
                "id": 0,
                "name": name,
                "ipAddress": "0.0.0.0",
                "isPublic": True,
                "status": "Active (On Network)",
                "assetCategory": "Software",
                "bLatestScan": True,
                "bAuthenticatedScan": True,
                "scanningTool": self.name,
                "assetOwnerId": self.config["userId"],
                "assetType": "Other",
                "fqdn": name if valid_name else None,
                "systemAdministratorId": self.config["userId"],
                "parentId": self.attributes.parent_id,
                "parentModule": self.attributes.parent_module,
            }
        )

    def _parse_json_asset(self, **kwargs) -> IntegrationAsset:
        """
        Parse assets from Snyk json scan data.

        :return: Integration asset
        :rtype: IntegrationAsset
        """
        data = kwargs.pop("data")
        name = self.extract_host(self.mapping.get_value(data, self.project_name))
        valid_name = is_valid_fqdn(name)
        return IntegrationAsset(
            identifier=name,
            name=name,
            status=AssetStatus.Active,
            asset_category=AssetCategory.Software,
            is_latest_scan=True,
            is_authenticated_scan=True,
            scanning_tool=self.name,
            asset_type=AssetType.Other,
            fqdn=name if valid_name else None,
            system_administrator_id=self.config["userId"],
            parent_id=self.attributes.parent_id,
            parent_module=self.attributes.parent_module,
        )

    def create_vuln(
        self, dat: Optional[dict] = None, **kwargs
    ) -> Optional[Union[list[IntegrationFinding], Vulnerability]]:
        """
        Create a vulnerability from a row in the Snyk file

        :param Optional[dict] dat: Data row from XLSX or JSON file, defaults to None
        :raises TypeError: If dat is not a dictionary
        :return: RegScale Vulnerability object if xlsx or list of IntegrationFindings if JSON
        :rtype: Optional[Union[list[IntegrationFinding], Vulnerability]]
        """
        if "json" in self.attributes.file_type:
            return self._parse_json_findings(**kwargs)
        elif "xlsx" in self.attributes.file_type:
            return self._parse_xlsx_finding(dat, **kwargs)
        else:
            raise NotImplementedError(self.not_implemented_error)

    def _parse_xlsx_finding(self, dat: Optional[dict] = None, **_) -> Optional[Vulnerability]:
        """
        Create a vulnerability from a row in the Snyk csv file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale Vulnerability object or None
        :rtype: Optional[Vulnerability]
        """
        regscale_vuln = None
        severity = self.mapping.get_value(dat, self.issue_severity).lower()
        hostname = self.extract_host(self.mapping.get_value(dat, self.project_name))
        description = self.mapping.get_value(dat, self.vuln_title)
        solution = self.mapping.get_value(dat, self.auto_fixable)
        config = self.attributes.app.config
        asset_match = [asset for asset in self.data["assets"] if asset.name == hostname]
        asset = asset_match[0] if asset_match else None
        if dat and asset_match:
            regscale_vuln = Vulnerability(
                id=0,
                scanId=0,  # set later
                parentId=asset.id,
                parentModule="assets",
                ipAddress="0.0.0.0",  # No ip address available
                lastSeen=get_current_datetime(),
                firstSeen=self.determine_first_seen(dat),
                daysOpen=None,
                dns=hostname,
                mitigated=None,
                operatingSystem=None,
                severity=severity,
                plugInName=description,
                cve=", ".join(self.mapping.get_value(dat, "CVE", "")),
                vprScore=None,
                tenantsId=0,
                title=f"{description} on asset {asset.name}",
                description=description,
                plugInText=self.mapping.get_value(dat, self.vuln_title),
                createdById=config["userId"],
                lastUpdatedById=config["userId"],
                dateCreated=get_current_datetime(),
                extra_data={"solution": solution},
            )
        return regscale_vuln

    def _parse_json_findings(self, **kwargs) -> list[IntegrationFinding]:
        """
        Create a vulnerability from a row in the Snyk csv file

        :return: List of IntegrationFinding objects
        :rtype: list[IntegrationFinding]
        """
        findings = []
        vulns = self.mapping.get_value(kwargs.get("data", self.validater.data), "vulnerabilities", [])
        if not vulns:
            return findings
        for dat in vulns:
            severity = self.finding_severity_map.get(dat.get(self.issue_severity, "Low").title())
            hostname = self.extract_host(self.mapping.get_value(dat, self.project_name)) or self.extract_host(
                self.mapping.get_value(self.validater.data, self.project_name)
            )
            description = self.mapping.get_value(dat, "description") or self.mapping.get_value(dat, self.vuln_title)
            solution = self.mapping.get_value(dat, self.auto_fixable)
            # if auto fixable is not available, check for upgradeable or patchable, this is for .json files
            if not solution:
                upgradeable = self.mapping.get_value(dat, "isUpgradeable", False)
                patchable = self.mapping.get_value(dat, "isPatchable", False)
                if upgradeable or patchable:
                    solution = "Upgrade or patch the vulnerable component."
            cves = ", ".join(self.mapping.get_value(dat, "CVE", ""))
            if not cves:
                cves = ", ".join(dat.get("identifiers", {}).get("CVE", []))
            findings.append(
                IntegrationFinding(
                    title=dat.get("title") or description,
                    description=description,
                    severity=severity,
                    status=IssueStatus.Open,
                    plugin_name=description,
                    plugin_id=dat.get("id"),
                    plugin_text=self.mapping.get_value(dat, self.vuln_title),
                    asset_identifier=hostname,
                    cve=cves,
                    cvss_score=dat.get("cvssScore"),
                    first_seen=self.determine_first_seen(dat),
                    last_seen=get_current_datetime(),
                    scan_date=self.attributes.scan_date,
                    dns=hostname,
                    vpr_score=None,
                    remediation=solution,
                    category="Software",
                    control_labels=[],
                )
            )
        return findings

    @staticmethod
    def extract_host(s: str) -> str:
        """
        Extract the host from the project name

        :param str s: The project name
        :return: The host
        :rtype: str
        """
        try:
            res = (s.split("|"))[1].split("/")[0]
        except IndexError:
            res = s
        return res
