import logging
from typing import Any
from typing import Dict
from typing import List

import boto3
import neo4j

from cartography.client.core.tx import load
from cartography.graph.job import GraphJob
from cartography.intel.aws.ec2.util import get_botocore_config
from cartography.models.aws.glue.connection import GlueConnectionSchema
from cartography.util import aws_handle_regions
from cartography.util import timeit

logger = logging.getLogger(__name__)


@timeit
@aws_handle_regions
def get_glue_connections(
    boto3_session: boto3.Session, region: str
) -> List[Dict[str, Any]]:
    client = boto3_session.client(
        "glue", region_name=region, config=get_botocore_config()
    )
    paginator = client.get_paginator("get_connections")
    connections = []
    for page in paginator.paginate():
        connections.extend(page.get("ConnectionList", []))

    return connections


def transform_glue_connections(
    connections: List[Dict[str, Any]], region: str
) -> List[Dict[str, Any]]:
    """
    Transform Glue connection data for ingestion
    """
    transformed_connections = []
    for connection in connections:
        transformed_connection = {
            "Name": connection["Name"],
            "Description": connection.get("Description"),
            "ConnectionType": connection.get("ConnectionType"),
            "Status": connection.get("Status"),
            "StatusReason": connection.get("StatusReason"),
            "AuthenticationType": connection.get("AuthenticationConfiguration", {}).get(
                "AuthenticationType"
            ),
            "SecretArn": connection.get("AuthenticationConfiguration", {}).get(
                "SecretArn"
            ),
            "Region": region,
        }
        transformed_connections.append(transformed_connection)
    return transformed_connections


@timeit
def load_glue_connections(
    neo4j_session: neo4j.Session,
    data: List[Dict[str, Any]],
    region: str,
    current_aws_account_id: str,
    aws_update_tag: int,
) -> None:
    logger.info(
        f"Loading Glue {len(data)} connections for region '{region}' into graph.",
    )
    load(
        neo4j_session,
        GlueConnectionSchema(),
        data,
        lastupdated=aws_update_tag,
        Region=region,
        AWS_ID=current_aws_account_id,
    )


@timeit
def cleanup(
    neo4j_session: neo4j.Session,
    common_job_parameters: Dict[str, Any],
) -> None:
    logger.debug("Running Glue cleanup job.")
    GraphJob.from_node_schema(GlueConnectionSchema(), common_job_parameters).run(
        neo4j_session
    )


@timeit
def sync(
    neo4j_session: neo4j.Session,
    boto3_session: boto3.session.Session,
    regions: List[str],
    current_aws_account_id: str,
    update_tag: int,
    common_job_parameters: Dict[str, Any],
) -> None:
    for region in regions:
        logger.info(
            f"Syncing Glue for region '{region}' in account '{current_aws_account_id}'.",
        )

        connections = get_glue_connections(boto3_session, region)
        transformed_connections = transform_glue_connections(connections, region)
        load_glue_connections(
            neo4j_session,
            transformed_connections,
            region,
            current_aws_account_id,
            update_tag,
        )

    cleanup(neo4j_session, common_job_parameters)
