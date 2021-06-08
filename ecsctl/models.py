from typing import List, Literal, Union
from datetime import datetime


class Cluster:
    DEFAULT_COLUMNS = [
        "name",
        "status",
        "instances",
        "services",
        "running_tasks",
        "pending_tasks",
    ]

    def __init__(
        self,
        name: str,
        status: str,
        instances: int,
        services: int,
        running_tasks: int,
        pending_tasks: int,
    ):
        self.name = name
        self.status = status
        self.instances = instances
        self.services = services
        self.running_tasks = running_tasks
        self.pending_tasks = pending_tasks


class Instance:
    DEFAULT_COLUMNS = [
        "id",
        "ec2_instance",
        "status",
        "running_tasks",
        "pending_tasks",
        "registered_at",
    ]

    def __init__(
        self,
        arn: str,
        ec2_instance_id: str,
        status: str,
        agent_connected: bool,
        running_tasks: int,
        pending_tasks: int,
        agent_update_status: str,
        registered_at: datetime,
    ):
        self.id = arn.split("/")[-1]
        self.arg = arn
        self.ec2_instance = ec2_instance_id
        self.status = status
        self.agent_connected = agent_connected
        self.running_tasks = running_tasks
        self.pending_tasks = pending_tasks
        self.agent_update_status = agent_update_status
        self.registered_at = registered_at


class ServiceEvent:
    DEFAULT_COLUMNS = [
        "id",
        "created_at",
        "message",
    ]

    def __init__(self, _id: str, created_at: datetime, message: str):
        self.id = _id
        self.created_at = created_at
        self.message = message


class Service:
    DEFAULT_COLUMNS = [
        "name",
        "status",
        "desired",
        "running",
        "pending",
        "type",
    ]

    def __init__(
        self,
        arn: str,
        name: str,
        cluster_arn: str,
        status: str,
        desired: int,
        running: int,
        pending: int,
        _type: str,
        task_definition: str,
        role_arn: str,
        created_at: datetime,
        created_by: str,
        scheduling_strategy: str,
        events: List[ServiceEvent],
    ):
        self.arn = arn
        self.name = name
        self.cluster_arn = cluster_arn
        self.status = status
        self.desired = desired
        self.running = running
        self.pending = pending
        self.type = _type
        self.task_definition = task_definition
        self.role_arn = role_arn
        self.created_at = created_at
        self.created_by = created_by
        self.scheduling_strategy = scheduling_strategy
        self.events = events

        # "deploymentConfiguration"
        # "placementConstraints"
        # "placementStrategy"
        # "networkConfiguration"


class NetworkBinding:
    def __init__(
        self,
        bind_ip: str,
        container_port: int,
        host_port: int,
        protocol: Literal["tcp", "udp"],
    ):
        self.bind_ip = bind_ip
        self.container_port = container_port
        self.host_port = host_port
        self.protocol = protocol


class NetworkInterface:
    def __init__(self, attachment_id: str, ipv4_address: str, ipv6_address: str):
        self.attachment_id = attachment_id
        self.ipv4_address = ipv4_address
        self.ipv6_address = ipv6_address


class ManagedAgent:
    def __init__(self, name: str, reason: str, status: str, started_at: datetime):
        self.name = name
        self.reason = reason
        self.status = status
        self.started_at = started_at


class Container:
    DEFAULT_COLUMNS = [
        "id",
        "name",
        "image",
        "health",
        "status",
        "exit_code",
        "reason",
    ]

    def __init__(
        self,
        arn: str,
        task_arn: str,
        name: str,
        image: str,
        image_digest: str,
        runtime_id: str,
        status: str,
        exit_code: int,
        reason: str,
        health: Literal["HEALTHY", "UNHEALTHY", "UNKNOWN"],
        cpu: int,
        memory: int,
        memory_reservation: int,
        network_bindings: List[NetworkBinding],
        network_interfaces: List[NetworkInterface],
        managed_agents: List[ManagedAgent],
        gpu_ids: List[str],
    ):
        self.id = arn.split("/")[-1]
        self.arn = arn
        self.task_id = task_arn.split("/")[-1]
        self.task_arn = task_arn
        self.name = name
        self.image = image
        self.image_digest = image_digest
        self.runtime_id = runtime_id
        self.status = status
        self.exit_code = exit_code
        self.reason = reason
        self.health = health
        self.cpu = cpu
        self.memory = memory
        self.memory_reservation = memory_reservation
        self.network_bindings = network_bindings
        self.network_interfaces = network_interfaces
        self.managed_agents = managed_agents
        self.gpu_ids = gpu_ids


class Task:
    DEFAULT_COLUMNS = [
        "id",
        "task_definition",
        "status",
        "health",
        "container_instance_id",
        "started_at",
        "stopped_at",
        "stopped_reason",
    ]

    def __init__(
        self,
        arn: str,
        task_definition_arn: str,
        cluster_arn: str,
        container_instance_arn: str,
        availability_zone: str,
        connectivity: Literal["CONNECTED", "DISCONNECTED"],
        connectivity_at: datetime,
        created_at: datetime,
        status: Literal[
            "PROVISIONING",
            "ACTIVATING",
            "RUNNING",
            "DEPROVISIONING",
            "DEACTIVATING",
            "STOPPED",
        ],
        desired_status: str,
        health: Literal["HEALTHY", "UNHEALTHY", "UNKNOWN"],
        _type: Literal["EC2", "FARGATE", "EXTERNAL"],
        cpu: int,
        memory: int,
        group: str,
        pull_started_at: datetime,
        pull_stopped_at: datetime,
        started_at: datetime,
        started_by: str,
        stopped_at: Union[datetime, None],
        stopped_reason: str,
        tags: List[str],
        containers: List[Container],
    ):
        self.id = arn.split("/")[-1]
        self.arn = arn
        self.task_definition = task_definition_arn.split("/")[-1]
        self.task_definition_arn = task_definition_arn
        self.cluster_arn = cluster_arn
        self.availability_zone = availability_zone
        self.connectivity = connectivity
        self.connectivity_at = connectivity_at
        self.created_at = created_at
        self.status = status
        self.desired_status = desired_status
        self.health = health
        self.type = _type
        self.cpu = cpu
        self.memory = memory
        self.group = group
        self.pull_started_at = pull_started_at
        self.pull_stopped_at = pull_stopped_at
        self.started_at = started_at
        self.started_by = started_by
        self.stopped_at = stopped_at
        self.stopped_reason = stopped_reason
        self.tags = tags

        if self.type == "EC2":
            self.container_instance_id = container_instance_arn.split("/")[-1]
            self.container_instance_arn = container_instance_arn

        self.containers = containers


class TaskDefinition:
    pass
