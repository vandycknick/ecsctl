import click
import json
import os
import subprocess

from click import Context
from ecsctl import console
from ecsctl.api import EcsApi
from ecsctl.config import Config
from ecsctl.serializers import (
    serialize_ecs_cluster,
    serialize_ecs_instance,
    serialize_ecs_service,
    serialize_ecs_task,
)
from ecsctl.console import Color, Console
from typing import List, Tuple, Dict, Optional


class Dependencies:
    def __init__(
        self, config: Config, ecs_api: EcsApi, props: Dict[str, str], console: Console
    ):
        self.config = config
        self.ecs_api = ecs_api
        self.props = props
        self.console = console


def get_dependencies(
    dep: Dependencies,
) -> Tuple[Config, EcsApi, Dict[str, str], Console]:
    return (dep.config, dep.ecs_api, dep.props, dep.console)


@click.group()
@click.option("-p", "--profile", envvar="AWS_PROFILE")
@click.option("-r", "--region", envvar="AWS_REGION")
@click.option("-o", "--output", envvar="ECS_CTL_OUTPUT", default="table")
@click.pass_context
def cli(ctx: Context, profile: str, region: str, output: str):
    config = Config()
    # TODO: bail out when profile is None
    ecs_api = EcsApi(profile or config.profile, region)
    console = Console()

    ctx.obj = Dependencies(
        config,
        ecs_api,
        {"profile": profile, "output": output, "region": region},
        console,
    )


@cli.group(short_help="Get ECS cluster resources")
def get():
    pass


@get.command(name="clusters")
@click.argument("cluster_names", nargs=-1)
@click.pass_context
def get_clusters(ctx: Context, cluster_names: List[str]):
    (_, ecs_api, props, console) = get_dependencies(ctx.obj)

    clusters = ecs_api.get_clusters(cluster_names=list(cluster_names))

    clusters = sorted(clusters, key=lambda x: x.name)

    if props.get("output", None) == "json":
        cluster_json = json.dumps(
            [serialize_ecs_cluster(cluster) for cluster in clusters]
        )
        console.print(cluster_json)
    else:
        console.table(clusters)


@get.command(name="instances")
@click.argument("instance_names", nargs=-1)
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("--sort-by", required=False, default="registered_at")
@click.pass_context
def get_instances(
    ctx: Context,
    cluster: str,
    instance_names: Optional[List[str]],
    sort_by: Optional[str],
):
    (config, ecs_api, props, console) = get_dependencies(ctx.obj)

    instances = ecs_api.get_instances(
        cluster or config.default_cluster, instance_names=list(instance_names)
    )

    instances = sorted(instances, key=lambda x: x.__dict__[sort_by], reverse=True)

    if props.get("output", None) == "json":
        console.print(
            json.dumps([serialize_ecs_instance(instance) for instance in instances])
        )
    else:
        console.table(instances)


@get.command(name="services")
@click.argument("service_names", nargs=-1)
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.pass_context
def get_services(ctx: Context, service_names: List[str], cluster: str):
    (config, ecs_api, props, console) = get_dependencies(ctx.obj)

    services = ecs_api.get_services(
        cluster or config.default_cluster, service_names=list(service_names)
    )

    services = sorted(services, key=lambda x: x.name)

    if props.get("output", None) == "json":
        console.print(
            json.dumps([serialize_ecs_service(service) for service in services])
        )
    else:
        console.table(services)


@get.command(name="events")
@click.argument("service_name", nargs=1, required=True)
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.pass_context
def get_events(ctx: Context, service_name: str, cluster: str):
    (config, ecs_api, _, console) = get_dependencies(ctx.obj)

    events = ecs_api.get_events_for_service(
        cluster or config.default_cluster, service_name=service_name
    )

    events = sorted(events, key=lambda x: x.created_at, reverse=True)
    console.table(events)

    # if props.get("output", None) == "json":
    #     print(json.dumps([serialize_ecs_service(service) for service in services]))
    # if props.get("output", None) == "pretty":
    #     print([serialize_ecs_service(service) for service in services])
    # else:
    #     render_table(services)


@get.command(name="tasks")
@click.argument("task_names", nargs=-1, required=False)
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("-s", "--service", required=False)
@click.option("-i", "--instance", required=False)
@click.option("--status", default="RUNNING")
@click.pass_context
def get_tasks(
    ctx: Context,
    cluster: str,
    task_names: Optional[List[str]],
    instance: Optional[str],
    service: Optional[str],
    status: Optional[str],
):
    (config, ecs_api, props, console) = get_dependencies(ctx.obj)

    tasks = ecs_api.get_tasks(
        cluster or config.default_cluster,
        task_names_or_arns=list(task_names),
        instance=instance,
        service=service,
        status=status,
    )

    if props.get("output", None) == "json":
        console.print(json.dumps([serialize_ecs_task(task) for task in tasks]))
    else:
        if len(tasks) > 0:
            console.table(tasks)
        else:
            console.print("No tasks found for the given search criteria")


@cli.command(short_help="Execute commands inside an ECS cluster")
@click.option("-c", "--cluster", envvar="ECS_DEFAULT_CLUSTER", required=False)
@click.option("-t", "--task", required=False)
@click.option("-s", "--service", required=False)
@click.option("--ec2", is_flag=True, default=False)
@click.pass_context
def exec(ctx: Context, cluster: str, task: str, service: str, ec2: bool):
    if not ec2:
        raise Exception(
            "Only executing into an ec2 instance supported at the moment. Please add --ec2 to jump into a shell in the ec2 instance a service or task is running on."
        )

    (config, ecs_api, props, console) = get_dependencies(ctx.obj)

    if not config.meets_ssm_prereqs:
        console.print(
            "This feature requires the following to be setup correctly:",
            color=Color.YELLOW,
        )
        console.print(
            "     - You have the AWS cli installed and available on your PATH.",
            color=Color.YELLOW,
        )
        console.print(
            "     - You have SSM setup and working correctly.", color=Color.YELLOW
        )
        console.print(
            "     - You have the SSM AWS cli plugin installed: https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html[/yellow]",
            color=Color.YELLOW,
        )
        console.print("")

        response = console.input(
            "Do you have all prerequisites setup correctly? (y/N) "
        )

        if response.lower() == "y":
            config.set_meets_ssm_prereqs()
            config.save()

    with console.status("Looking up EC2 instance") as status:
        task = ecs_api.get_task_by_id_or_arn(cluster or config.default_cluster, task)

        constainer_instances = ecs_api.get_instances(
            cluster or config.default_cluster, [task.container_instance_id]
        )

        ec2_instance = constainer_instances[0].ec2_instance

        status.update(f"Launching shell in {ec2_instance}")

        if props.get("profile", None) is None:
            cmd = ["aws", "ssm", "start-session", "--target", ec2_instance]
        else:
            cmd = [
                "aws",
                "--profile",
                props.get("profile"),
                "ssm",
                "start-session",
                "--target",
                ec2_instance,
            ]

        env = os.environ.copy()

        shell = subprocess.Popen(cmd, env=env)
        import time

        time.sleep(2)
        status.stop()

        while True:
            try:
                shell.wait()
                break
            except KeyboardInterrupt as _:
                pass
