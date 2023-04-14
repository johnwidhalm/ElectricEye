#This file is part of ElectricEye.
#SPDX-License-Identifier: Apache-2.0

#Licensed to the Apache Software Foundation (ASF) under one
#or more contributor license agreements.  See the NOTICE file
#distributed with this work for additional information
#regarding copyright ownership.  The ASF licenses this file
#to you under the Apache License, Version 2.0 (the
#"License"); you may not use this file except in compliance
#with the License.  You may obtain a copy of the License at

#http://www.apache.org/licenses/LICENSE-2.0

#Unless required by applicable law or agreed to in writing,
#software distributed under the License is distributed on an
#"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#KIND, either express or implied.  See the License for the
#specific language governing permissions and limitations
#under the License.

import datetime
from check_register import CheckRegister
import googleapiclient.discovery

registry = CheckRegister()

def get_cloudsql_dbs(cache: dict, gcpProjectId: str):
    '''
    AggregatedList result provides Zone information as well as every single Instance in a Project
    '''
    response = cache.get("get_cloudsql_dbs")
    if response:
        return response

    #  CloudSQL requires SQL Admin API - also doesnt need an aggregatedList
    service = googleapiclient.discovery.build('sqladmin', 'v1beta4')
    instances = service.instances().list(project=gcpProjectId).execute()
    
    cache["get_cloudsql_dbs"] = instances["items"]

    return cache["get_cloudsql_dbs"]

@registry.register_check("cloudsql")
def cloudsql_instance_public_check(cache: dict, awsAccountId: str, awsRegion: str, awsPartition: str, gcpProjectId: str):
    """
    [GCP.CloudSQL.1] CloudSQL Instances should not be publicly reachable
    """
    iso8601Time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for csql in get_cloudsql_dbs(cache, gcpProjectId):
        name = csql["name"]
        zone = csql["gceZone"]
        databaseVersion = csql["databaseVersion"]
        createTime = csql["createTime"]
        state = csql["state"]
        maintenanceVersion = csql["maintenanceVersion"]
        ipAddress = csql["ipAddresses"][0]["ipAddress"]
        # If this value is True, it means a Public IP is assigned
        if csql["settings"]["ipConfiguration"]["ipv4Enabled"] == True:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{gcpProjectId}/{zone}/{name}/cloudsql-public-instance-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": f"{gcpProjectId}/{zone}/{name}/cloudsql-public-instance-check",
                "AwsAccountId": awsAccountId,
                "Types": ["Software and Configuration Checks"],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "HIGH"},
                "Confidence": 99,
                "Title": "[GCP.CloudSQL.1] CloudSQL Instances should not be publicly reachable",
                "Description": f"CloudSQL instance {name} in {zone} is publicly reachable due to an external IP assignment. While not inherently dangerous as this check does not take into account any additional security controls, databases should only be available to private IP address space and use minimalistic VPC Firewall Rules along with strong authentication. Publicly reachable databases without complentary security controls may leave your database resource and the data therein susceptible to destruction, manipulation, and/or capture by adversaries and unauthorized personnel. Refer to the remediation instructions if this configuration is not intended.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your CloudSQL instance should not have a public IP assigned refer to the Configure public IP section of the GCP CloudSQL guide.",
                        "Url": "https://cloud.google.com/sql/docs/mysql/configure-ip",
                    }
                },
                "ProductFields": {
                    "ProductName": "ElectricEye",
                    "Provider": "GCP",
                    "AssetClass": "Database",
                    "AssetService": "CloudSQL",
                    "AssetType": "CloudSQL Instance"
                },
                "Resources": [
                    {
                        "Type": "GcpCloudSqlInstance",
                        "Id": f"{gcpProjectId}/{zone}/{name}",
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "Other": {
                                "GcpProjectId": gcpProjectId,
                                "Zone": zone,
                                "Name": name,
                                "DatabaseVersion": databaseVersion,
                                "MaintenanceVersion": maintenanceVersion,
                                "CreatedAt": createTime,
                                "State": state,
                                "IpAddress": ipAddress,
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "FAILED",
                    "RelatedRequirements": [
                        "NIST CSF PR.AC-3",
                        "NIST SP 800-53 AC-1",
                        "NIST SP 800-53 AC-17",
                        "NIST SP 800-53 AC-19",
                        "NIST SP 800-53 AC-20",
                        "NIST SP 800-53 SC-15",
                        "AICPA TSC CC6.6",
                        "ISO 27001:2013 A.6.2.1",
                        "ISO 27001:2013 A.6.2.2",
                        "ISO 27001:2013 A.11.2.6",
                        "ISO 27001:2013 A.13.1.1",
                        "ISO 27001:2013 A.13.2.1"
                    ]
                },
                "Workflow": {"Status": "NEW"},
                "RecordState": "ACTIVE"
            }
            yield finding 
        else:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{gcpProjectId}/{zone}/{name}/cloudsql-public-instance-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": f"{gcpProjectId}/{zone}/{name}/cloudsql-public-instance-check",
                "AwsAccountId": awsAccountId,
                "Types": ["Software and Configuration Checks"],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "INFORMATIONAL"},
                "Confidence": 99,
                "Title": "[GCP.CloudSQL.1] CloudSQL Instances should not be publicly reachable",
                "Description": f"CloudSQL instance {name} in {zone} is not publicly reachable due to not having an external IP assignment.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your CloudSQL instance should not have a public IP assigned refer to the Configure public IP section of the GCP CloudSQL guide.",
                        "Url": "https://cloud.google.com/sql/docs/mysql/configure-ip",
                    }
                },
                "ProductFields": {
                    "ProductName": "ElectricEye",
                    "Provider": "GCP",
                    "AssetClass": "Database",
                    "AssetService": "CloudSQL",
                    "AssetType": "CloudSQL Instance"
                },
                "Resources": [
                    {
                        "Type": "GcpCloudSqlInstance",
                        "Id": f"{gcpProjectId}/{zone}/{name}",
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "Other": {
                                "GcpProjectId": gcpProjectId,
                                "Zone": zone,
                                "Name": name,
                                "DatabaseVersion": databaseVersion,
                                "MaintenanceVersion": maintenanceVersion,
                                "CreatedAt": createTime,
                                "State": state,
                                "IpAddress": ipAddress,
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "PASSED",
                    "RelatedRequirements": [
                        "NIST CSF PR.AC-3",
                        "NIST SP 800-53 AC-1",
                        "NIST SP 800-53 AC-17",
                        "NIST SP 800-53 AC-19",
                        "NIST SP 800-53 AC-20",
                        "NIST SP 800-53 SC-15",
                        "AICPA TSC CC6.6",
                        "ISO 27001:2013 A.6.2.1",
                        "ISO 27001:2013 A.6.2.2",
                        "ISO 27001:2013 A.11.2.6",
                        "ISO 27001:2013 A.13.1.1",
                        "ISO 27001:2013 A.13.2.1"
                    ]
                },
                "Workflow": {"Status": "RESOLVED"},
                "RecordState": "ARCHIVED"
            }
            yield finding

@registry.register_check("cloudsql")
def cloudsql_instance_standard_backup_check(cache: dict, awsAccountId: str, awsRegion: str, awsPartition: str, gcpProjectId: str):
    """
    [GCP.CloudSQL.2] CloudSQL Instances should have automated backups configured
    """
    iso8601Time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for csql in get_cloudsql_dbs(cache, gcpProjectId):
        name = csql["name"]
        zone = csql["gceZone"]
        databaseVersion = csql["databaseVersion"]
        createTime = csql["createTime"]
        state = csql["state"]
        maintenanceVersion = csql["maintenanceVersion"]
        ipAddress = csql["ipAddresses"][0]["ipAddress"]
        # Check if basic backups are enabled - this is a failing check
        if csql["settings"]["backupConfiguration"]["enabled"] == False:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{gcpProjectId}/{zone}/{name}/cloudsql-instance-basic-backup-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": f"{gcpProjectId}/{zone}/{name}/cloudsql-instance-basic-backup-check",
                "AwsAccountId": awsAccountId,
                "Types": ["Software and Configuration Checks"],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "MEDIUM"},
                "Confidence": 99,
                "Title": "[GCP.CloudSQL.2] CloudSQL Instances should have automated backups configured",
                "Description": f"CloudSQL instance {name} in {zone} does not have backups enabled. Automated backups are used to restore a Cloud SQL instance, and provide a way to recover data in the event of a disaster, such as hardware failure, human error, or a natural disaster or protect against data loss by providing a copy of the data that can be restored if the original data is lost or corrupted. Cloud SQL backups can be automated and managed through the GCP console or API, simplifying the process of creating and managing backups. Cloud SQL backups are stored in a separate location, which can help reduce the risk of data loss due to regional outages or disasters. Additionally, backups can be configured to fit the needs of the organization, helping to reduce unnecessary costs. Refer to the remediation instructions if this configuration is not intended.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your CloudSQL instance should have backups enabled refer to the Automated backup and transaction log retention section of the GCP CloudSQL guide.",
                        "Url": "https://cloud.google.com/sql/docs/mysql/backup-recovery/backups#retention",
                    }
                },
                "ProductFields": {
                    "ProductName": "ElectricEye",
                    "Provider": "GCP",
                    "AssetClass": "Database",
                    "AssetService": "CloudSQL",
                    "AssetType": "CloudSQL Instance"
                },
                "Resources": [
                    {
                        "Type": "GcpCloudSqlInstance",
                        "Id": f"{gcpProjectId}/{zone}/{name}",
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "Other": {
                                "GcpProjectId": gcpProjectId,
                                "Zone": zone,
                                "Name": name,
                                "DatabaseVersion": databaseVersion,
                                "MaintenanceVersion": maintenanceVersion,
                                "CreatedAt": createTime,
                                "State": state,
                                "IpAddress": ipAddress,
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "FAILED",
                    "RelatedRequirements": [
                        "NIST CSF ID.BE-5",
                        "NIST CSF PR.PT-5",
                        "NIST SP 800-53 CP-2",
                        "NIST SP 800-53 CP-11",
                        "NIST SP 800-53 SA-13",
                        "NIST SP 800-53 SA14",
                        "AICPA TSC CC3.1",
                        "AICPA TSC A1.2",
                        "ISO 27001:2013 A.11.1.4",
                        "ISO 27001:2013 A.17.1.1",
                        "ISO 27001:2013 A.17.1.2",
                        "ISO 27001:2013 A.17.2.1"
                    ]
                },
                "Workflow": {"Status": "NEW"},
                "RecordState": "ACTIVE"
            }
            yield finding
        else:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{gcpProjectId}/{zone}/{name}/cloudsql-instance-basic-backup-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": f"{gcpProjectId}/{zone}/{name}/cloudsql-instance-basic-backup-check",
                "AwsAccountId": awsAccountId,
                "Types": ["Software and Configuration Checks"],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "INFORMATIONAL"},
                "Confidence": 99,
                "Title": "[GCP.CloudSQL.2] CloudSQL Instances should have automated backups configured",
                "Description": f"CloudSQL instance {name} in {zone} has automated backups enabled.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your CloudSQL instance should have backups enabled refer to the Automated backup and transaction log retention section of the GCP CloudSQL guide.",
                        "Url": "https://cloud.google.com/sql/docs/mysql/backup-recovery/backups#retention",
                    }
                },
                "ProductFields": {
                    "ProductName": "ElectricEye",
                    "Provider": "GCP",
                    "AssetClass": "Database",
                    "AssetService": "CloudSQL",
                    "AssetType": "CloudSQL Instance"
                },
                "Resources": [
                    {
                        "Type": "GcpCloudSqlInstance",
                        "Id": f"{gcpProjectId}/{zone}/{name}",
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "Other": {
                                "GcpProjectId": gcpProjectId,
                                "Zone": zone,
                                "Name": name,
                                "DatabaseVersion": databaseVersion,
                                "MaintenanceVersion": maintenanceVersion,
                                "CreatedAt": createTime,
                                "State": state,
                                "IpAddress": ipAddress,
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "PASSED",
                    "RelatedRequirements": [
                        "NIST CSF ID.BE-5",
                        "NIST CSF PR.PT-5",
                        "NIST SP 800-53 CP-2",
                        "NIST SP 800-53 CP-11",
                        "NIST SP 800-53 SA-13",
                        "NIST SP 800-53 SA14",
                        "AICPA TSC CC3.1",
                        "AICPA TSC A1.2",
                        "ISO 27001:2013 A.11.1.4",
                        "ISO 27001:2013 A.17.1.1",
                        "ISO 27001:2013 A.17.1.2",
                        "ISO 27001:2013 A.17.2.1"
                    ]
                },
                "Workflow": {"Status": "RESOLVED"},
                "RecordState": "ARCHIVED"
            }
            yield finding 

@registry.register_check("cloudsql")
def cloudsql_instance_mysql_pitr_backup_check(cache: dict, awsAccountId: str, awsRegion: str, awsPartition: str, gcpProjectId: str):
    """
    [GCP.CloudSQL.3] CloudSQL MySQL Instances with mission-critical workloads should have point-in-time recovery (PITR) configured
    """
    iso8601Time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for csql in get_cloudsql_dbs(cache, gcpProjectId):
        name = csql["name"]
        zone = csql["gceZone"]
        databaseVersion = csql["databaseVersion"]
        # Check if the DB engine (to use an AWS term, lol) matches what we want
        # example output is MYSQL_8_0_26 or POSTGRES_14
        dbEngine = databaseVersion.split("_")[0]
        if dbEngine != "MYSQL":
            continue
        createTime = csql["createTime"]
        state = csql["state"]
        maintenanceVersion = csql["maintenanceVersion"]
        ipAddress = csql["ipAddresses"][0]["ipAddress"]
        # "binaryLogEnabled" only appears for Mysql
        if csql["settings"]["backupConfiguration"]["binaryLogEnabled"] == False:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{gcpProjectId}/{zone}/{name}/cloudsql-instance-mysql-pitr-backup-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": f"{gcpProjectId}/{zone}/{name}/cloudsql-instance-mysql-pitr-backup-check",
                "AwsAccountId": awsAccountId,
                "Types": ["Software and Configuration Checks"],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "LOW"},
                "Confidence": 99,
                "Title": "[GCP.CloudSQL.3] CloudSQL MySQL Instances with mission-critical workloads should have point-in-time recovery (PITR) configured",
                "Description": f"CloudSQL instance {name} in {zone} does not have point-in-time recovery (PITR) configured. For databases that are part of business- or mission-critical applications or that need to maintain as little data loss as possible, considered enabling PITR. PITR, or Binary Logs for MySQL, allows the restoration of data from a specific point in time, making it easier to recover from data corruption or malicious activities, such as ransomware attacks. This is because PITR provides a way to revert the database to a state before the attack occurred, minimizing the impact of the attack and reducing the amount of data that is lost. Refer to the remediation instructions if this configuration is not intended.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your MYSQL CloudSQL instance should have PITR backups enabled refer to the Use point-in-time recovery section of the GCP MySQL CloudSQL guide.",
                        "Url": "https://cloud.google.com/sql/docs/mysql/backup-recovery/pitr",
                    }
                },
                "ProductFields": {
                    "ProductName": "ElectricEye",
                    "Provider": "GCP",
                    "AssetClass": "Database",
                    "AssetService": "CloudSQL",
                    "AssetType": "CloudSQL Instance"
                },
                "Resources": [
                    {
                        "Type": "GcpCloudSqlInstance",
                        "Id": f"{gcpProjectId}/{zone}/{name}",
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "Other": {
                                "GcpProjectId": gcpProjectId,
                                "Zone": zone,
                                "Name": name,
                                "DatabaseVersion": databaseVersion,
                                "MaintenanceVersion": maintenanceVersion,
                                "CreatedAt": createTime,
                                "State": state,
                                "IpAddress": ipAddress,
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "FAILED",
                    "RelatedRequirements": [
                        "NIST CSF ID.BE-5",
                        "NIST CSF PR.PT-5",
                        "NIST SP 800-53 CP-2",
                        "NIST SP 800-53 CP-11",
                        "NIST SP 800-53 SA-13",
                        "NIST SP 800-53 SA14",
                        "AICPA TSC CC3.1",
                        "AICPA TSC A1.2",
                        "ISO 27001:2013 A.11.1.4",
                        "ISO 27001:2013 A.17.1.1",
                        "ISO 27001:2013 A.17.1.2",
                        "ISO 27001:2013 A.17.2.1"
                    ]
                },
                "Workflow": {"Status": "NEW"},
                "RecordState": "ACTIVE"
            }
            yield finding
        else:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{gcpProjectId}/{zone}/{name}/cloudsql-instance-mysql-pitr-backup-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": f"{gcpProjectId}/{zone}/{name}/cloudsql-instance-mysql-pitr-backup-check",
                "AwsAccountId": awsAccountId,
                "Types": ["Software and Configuration Checks"],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "INFORMATIONAL"},
                "Confidence": 99,
                "Title": "[GCP.CloudSQL.3] CloudSQL MySQL Instances with mission-critical workloads should have point-in-time recovery (PITR) configured",
                "Description": f"CloudSQL instance {name} in {zone} has point-in-time recovery (PITR) configured.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your MYSQL CloudSQL instance should have PITR backups enabled refer to the Use point-in-time recovery section of the GCP MySQL CloudSQL guide.",
                        "Url": "https://cloud.google.com/sql/docs/mysql/backup-recovery/pitr",
                    }
                },
                "ProductFields": {
                    "ProductName": "ElectricEye",
                    "Provider": "GCP",
                    "AssetClass": "Database",
                    "AssetService": "CloudSQL",
                    "AssetType": "CloudSQL Instance"
                },
                "Resources": [
                    {
                        "Type": "GcpCloudSqlInstance",
                        "Id": f"{gcpProjectId}/{zone}/{name}",
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "Other": {
                                "GcpProjectId": gcpProjectId,
                                "Zone": zone,
                                "Name": name,
                                "DatabaseVersion": databaseVersion,
                                "MaintenanceVersion": maintenanceVersion,
                                "CreatedAt": createTime,
                                "State": state,
                                "IpAddress": ipAddress,
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "PASSED",
                    "RelatedRequirements": [
                        "NIST CSF ID.BE-5",
                        "NIST CSF PR.PT-5",
                        "NIST SP 800-53 CP-2",
                        "NIST SP 800-53 CP-11",
                        "NIST SP 800-53 SA-13",
                        "NIST SP 800-53 SA14",
                        "AICPA TSC CC3.1",
                        "AICPA TSC A1.2",
                        "ISO 27001:2013 A.11.1.4",
                        "ISO 27001:2013 A.17.1.1",
                        "ISO 27001:2013 A.17.1.2",
                        "ISO 27001:2013 A.17.2.1"
                    ]
                },
                "Workflow": {"Status": "RESOLVED"},
                "RecordState": "ARCHIVED"
            }
            yield finding

@registry.register_check("cloudsql")
def cloudsql_instance_mysql_pitr_backup_check(cache: dict, awsAccountId: str, awsRegion: str, awsPartition: str, gcpProjectId: str):
    """
    [GCP.CloudSQL.4] CloudSQL PostgreSQL Instances with mission-critical workloads should have point-in-time recovery (PITR) configured
    """
    iso8601Time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for csql in get_cloudsql_dbs(cache, gcpProjectId):
        name = csql["name"]
        zone = csql["gceZone"]
        databaseVersion = csql["databaseVersion"]
        # Check if the DB engine (to use an AWS term, lol) matches what we want
        # example output is MYSQL_8_0_26 or POSTGRES_14
        dbEngine = databaseVersion.split("_")[0]
        if dbEngine != "POSTGRES":
            continue
        createTime = csql["createTime"]
        state = csql["state"]
        maintenanceVersion = csql["maintenanceVersion"]
        ipAddress = csql["ipAddresses"][0]["ipAddress"]
        # "pointInTimeRecoveryEnabled" only appears for Psql
        if csql["settings"]["backupConfiguration"]["pointInTimeRecoveryEnabled"] == False:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{gcpProjectId}/{zone}/{name}/cloudsql-instance-psql-pitr-backup-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": f"{gcpProjectId}/{zone}/{name}/cloudsql-instance-psql-pitr-backup-check",
                "AwsAccountId": awsAccountId,
                "Types": ["Software and Configuration Checks"],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "LOW"},
                "Confidence": 99,
                "Title": "[GCP.CloudSQL.4] CloudSQL PostgreSQL Instances with mission-critical workloads should have point-in-time recovery (PITR) configured",
                "Description": f"CloudSQL instance {name} in {zone} does not have point-in-time recovery (PITR) configured. For databases that are part of business- or mission-critical applications or that need to maintain as little data loss as possible, considered enabling PITR. PITR, or Write-Ahead Logging (WAL) for MySQL, allows the restoration of data from a specific point in time, making it easier to recover from data corruption or malicious activities, such as ransomware attacks. This is because PITR provides a way to revert the database to a state before the attack occurred, minimizing the impact of the attack and reducing the amount of data that is lost. Refer to the remediation instructions if this configuration is not intended.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your PostgreSQL CloudSQL instance should have PITR backups enabled refer to the Use point-in-time recovery section of the GCP PostgreSQL CloudSQL guide.",
                        "Url": "https://cloud.google.com/sql/docs/postgres/backup-recovery/pitr",
                    }
                },
                "ProductFields": {
                    "ProductName": "ElectricEye",
                    "Provider": "GCP",
                    "AssetClass": "Database",
                    "AssetService": "CloudSQL",
                    "AssetType": "CloudSQL Instance"
                },
                "Resources": [
                    {
                        "Type": "GcpCloudSqlInstance",
                        "Id": f"{gcpProjectId}/{zone}/{name}",
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "Other": {
                                "GcpProjectId": gcpProjectId,
                                "Zone": zone,
                                "Name": name,
                                "DatabaseVersion": databaseVersion,
                                "MaintenanceVersion": maintenanceVersion,
                                "CreatedAt": createTime,
                                "State": state,
                                "IpAddress": ipAddress,
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "FAILED",
                    "RelatedRequirements": [
                        "NIST CSF ID.BE-5",
                        "NIST CSF PR.PT-5",
                        "NIST SP 800-53 CP-2",
                        "NIST SP 800-53 CP-11",
                        "NIST SP 800-53 SA-13",
                        "NIST SP 800-53 SA14",
                        "AICPA TSC CC3.1",
                        "AICPA TSC A1.2",
                        "ISO 27001:2013 A.11.1.4",
                        "ISO 27001:2013 A.17.1.1",
                        "ISO 27001:2013 A.17.1.2",
                        "ISO 27001:2013 A.17.2.1"
                    ]
                },
                "Workflow": {"Status": "NEW"},
                "RecordState": "ACTIVE"
            }
            yield finding
        else:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{gcpProjectId}/{zone}/{name}/cloudsql-instance-psql-pitr-backup-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": f"{gcpProjectId}/{zone}/{name}/cloudsql-instance-psql-pitr-backup-check",
                "AwsAccountId": awsAccountId,
                "Types": ["Software and Configuration Checks"],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "INFORMATIONAL"},
                "Confidence": 99,
                "Title": "[GCP.CloudSQL.4] CloudSQL PostgreSQL Instances with mission-critical workloads should have point-in-time recovery (PITR) configured",
                "Description": f"CloudSQL instance {name} in {zone} has point-in-time recovery (PITR) configured.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your PostgreSQL CloudSQL instance should have PITR backups enabled refer to the Use point-in-time recovery section of the GCP PostgreSQL CloudSQL guide.",
                        "Url": "https://cloud.google.com/sql/docs/postgres/backup-recovery/pitr",
                    }
                },
                "ProductFields": {
                    "ProductName": "ElectricEye",
                    "Provider": "GCP",
                    "AssetClass": "Database",
                    "AssetService": "CloudSQL",
                    "AssetType": "CloudSQL Instance"
                },
                "Resources": [
                    {
                        "Type": "GcpCloudSqlInstance",
                        "Id": f"{gcpProjectId}/{zone}/{name}",
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "Other": {
                                "GcpProjectId": gcpProjectId,
                                "Zone": zone,
                                "Name": name,
                                "DatabaseVersion": databaseVersion,
                                "MaintenanceVersion": maintenanceVersion,
                                "CreatedAt": createTime,
                                "State": state,
                                "IpAddress": ipAddress,
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "PASSED",
                    "RelatedRequirements": [
                        "NIST CSF ID.BE-5",
                        "NIST CSF PR.PT-5",
                        "NIST SP 800-53 CP-2",
                        "NIST SP 800-53 CP-11",
                        "NIST SP 800-53 SA-13",
                        "NIST SP 800-53 SA14",
                        "AICPA TSC CC3.1",
                        "AICPA TSC A1.2",
                        "ISO 27001:2013 A.11.1.4",
                        "ISO 27001:2013 A.17.1.1",
                        "ISO 27001:2013 A.17.1.2",
                        "ISO 27001:2013 A.17.2.1"
                    ]
                },
                "Workflow": {"Status": "RESOLVED"},
                "RecordState": "ARCHIVED"
            }
            yield finding

# Private Path Access ipConfiguration.enablePrivatePathForGoogleCloudServices
@registry.register_check("cloudsql")
def cloudsql_instance_private_gcp_services_connection_check(cache: dict, awsAccountId: str, awsRegion: str, awsPartition: str, gcpProjectId: str):
    """
    [GCP.CloudSQL.5] CloudSQL Instances should enable private path for Google Cloud Services connectivity
    """
    iso8601Time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for csql in get_cloudsql_dbs(cache, gcpProjectId):
        name = csql["name"]
        zone = csql["gceZone"]
        databaseVersion = csql["databaseVersion"]
        createTime = csql["createTime"]
        state = csql["state"]
        maintenanceVersion = csql["maintenanceVersion"]
        ipAddress = csql["ipAddresses"][0]["ipAddress"]
        if 'privateNetwork' in csql["settings"]["ipConfiguration"]:
            print(csql["settings"]["ipConfiguration"]["ipv4Enabled"])
        """# "pointInTimeRecoveryEnabled" only appears for Psql
        if csql["settings"]["backupConfiguration"]["pointInTimeRecoveryEnabled"] == False:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{gcpProjectId}/{zone}/{name}/cloudsql-instance-psql-pitr-backup-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": f"{gcpProjectId}/{zone}/{name}/cloudsql-instance-psql-pitr-backup-check",
                "AwsAccountId": awsAccountId,
                "Types": ["Software and Configuration Checks"],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "LOW"},
                "Confidence": 99,
                "Title": "[GCP.CloudSQL.4] CloudSQL PostgreSQL Instances with mission-critical workloads should have point-in-time recovery (PITR) configured",
                "Description": f"CloudSQL instance {name} in {zone} does not have point-in-time recovery (PITR) configured. For databases that are part of business- or mission-critical applications or that need to maintain as little data loss as possible, considered enabling PITR. PITR, or Write-Ahead Logging (WAL) for MySQL, allows the restoration of data from a specific point in time, making it easier to recover from data corruption or malicious activities, such as ransomware attacks. This is because PITR provides a way to revert the database to a state before the attack occurred, minimizing the impact of the attack and reducing the amount of data that is lost. Refer to the remediation instructions if this configuration is not intended.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your PostgreSQL CloudSQL instance should have PITR backups enabled refer to the Use point-in-time recovery section of the GCP PostgreSQL CloudSQL guide.",
                        "Url": "https://cloud.google.com/sql/docs/postgres/backup-recovery/pitr",
                    }
                },
                "ProductFields": {
                    "ProductName": "ElectricEye",
                    "Provider": "GCP",
                    "AssetClass": "Database",
                    "AssetService": "CloudSQL",
                    "AssetType": "CloudSQL Instance"
                },
                "Resources": [
                    {
                        "Type": "GcpCloudSqlInstance",
                        "Id": f"{gcpProjectId}/{zone}/{name}",
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "Other": {
                                "GcpProjectId": gcpProjectId,
                                "Zone": zone,
                                "Name": name,
                                "DatabaseVersion": databaseVersion,
                                "MaintenanceVersion": maintenanceVersion,
                                "CreatedAt": createTime,
                                "State": state,
                                "IpAddress": ipAddress,
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "FAILED",
                    "RelatedRequirements": [
                        "NIST CSF ID.BE-5",
                        "NIST CSF PR.PT-5",
                        "NIST SP 800-53 CP-2",
                        "NIST SP 800-53 CP-11",
                        "NIST SP 800-53 SA-13",
                        "NIST SP 800-53 SA14",
                        "AICPA TSC CC3.1",
                        "AICPA TSC A1.2",
                        "ISO 27001:2013 A.11.1.4",
                        "ISO 27001:2013 A.17.1.1",
                        "ISO 27001:2013 A.17.1.2",
                        "ISO 27001:2013 A.17.2.1"
                    ]
                },
                "Workflow": {"Status": "NEW"},
                "RecordState": "ACTIVE"
            }
            yield finding"""

# Password Policy Enabled passwordValidationPolicy.enablePasswordPolicy

# Password Policy min length CIS (14) passwordValidationPolicy.minLength

# Password Policy Reuse CIS .reuseInterval

# Password Policy disallow username in PW .disallowUsernameSubstring

# Password Policy change interval .passwordChangeInterval

# Storage Autoresize storageAutoResize

# Deletion Protection deletionProtectionEnabled

# Enable Insights Config ... "insightsConfig": {},

# For Insights Config, Log Client IP insightsConfig.recordClientAddress

# Enforce SSL Connections ipConfiguration.requireSsl - can be missing 

# To be continued...?