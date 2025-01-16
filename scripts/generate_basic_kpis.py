import yaml
import re
import pandas as pd

def calculate_yaml_complexity(yaml_data):
    def get_depth(obj, current_depth=0):
        if isinstance(obj, dict):
            return max((get_depth(v, current_depth + 1) for v in obj.values()), default=current_depth)
        elif isinstance(obj, list):
            return max((get_depth(i, current_depth + 1) for i in obj), default=current_depth)
        return current_depth

    def count_keys(obj):
        if isinstance(obj, dict):
            return sum(count_keys(v) for v in obj.values()) + len(obj)
        elif isinstance(obj, list):
            return sum(count_keys(i) for i in obj)
        return 0

    depth = get_depth(yaml_data)
    num_keys = count_keys(yaml_data)

    return depth, num_keys

def count_plans(yaml_data):
    total_plans = 0
    plan = yaml_data.get('plan', {})
    for line in yaml_data:
        if 'plan' in  line:
            total_plans += 1

    return total_plans


def count_jobs(yaml_data):
    total_jobs = 0

    stages = yaml_data.get('stages', [])
    for stage in stages:
        for stage_name, stage_info in stage.items():
            if 'jobs' in stage_info:
                total_jobs += len(stage_info['jobs'])

    plan = yaml_data.get('plan', {})
    for key, value in plan.items():
        if isinstance(value, dict) and 'tasks' in value:
            total_jobs += 1

    return total_jobs


def count_tasks(yaml_data):
    task_count = 0

    if isinstance(yaml_data, dict):
        for key, value in yaml_data.items():
            if key == 'tasks' and isinstance(value, list):
                task_count += len(value)
            else:
                task_count += count_tasks(value)
    elif isinstance(yaml_data, list):
        for item in yaml_data:
            task_count += count_tasks(item)

    return task_count


def count_dependencies(yaml_data):
    dependencies = yaml_data.get('plan', {}).get('dependencies', {})
    plans = dependencies.get('plans', [])
    return len(plans)


def count_triggers(yaml_data):
    if isinstance(yaml_data, dict):
        triggers = yaml_data.get('triggers', [])
        if triggers is None:
            triggers = []
        return len(triggers)
    else:
        return 0


def count_artifacts(yaml_data):
    artifact_count = 0

    def explore(data):
        nonlocal artifact_count

        if isinstance(data, dict):
            if 'artifacts' in data:
                artifact_count += len(data['artifacts'])

            for value in data.values():
                explore(value)

        elif isinstance(data, list):
            for item in data:
                explore(item)

    explore(yaml_data)
    return artifact_count


def count_environments(yaml_data):
    environments = set()
    def explore(data):
        if isinstance(data, dict):
            if 'environment' in data:
                environment = data['environment']
                if isinstance(environment, str):
                    environments.add(environment)
                elif isinstance(environment, list):
                    environments.update(environment)

            for value in data.values():
                explore(value)

        elif isinstance(data, list):
            for item in data:
                explore(item)

    explore(yaml_data)
    return len(environments)


def count_environment_variables(yaml_data):
    total_env_vars = 0
    if 'variables' in yaml_data:
        total_env_vars += len(yaml_data['variables'])

    def search_environment_in_tasks(data):
        count = 0
        if isinstance(data, dict):
            for key, value in data.items():
                # Vérifier si une clé 'environment' existe
                if key == 'environment' and isinstance(value, dict):
                    count += len(value)
                else:
                    count += search_environment_in_tasks(value)
        elif isinstance(data, list):
            for item in data:
                count += search_environment_in_tasks(item)
        return count

    total_env_vars += search_environment_in_tasks(yaml_data.get('stages', []))
    total_env_vars += search_environment_in_tasks(yaml_data.get('tasks', []))

    return total_env_vars


def get_version(yaml_data):
    return yaml_data.get('version', 'N/A')


def count_retry_in_seconds(yaml_data):
    count = 0

    if isinstance(yaml_data, dict):
        for key, value in yaml_data.items():
            if key == 'retryInSeconds':
                count += 1
            count += count_retry_in_seconds(value)

    elif isinstance(yaml_data, list):
        for item in yaml_data:
            count += count_retry_in_seconds(item)

    return count


def count_failed_statuses(yaml_data):
    plan_failed_count = 0
    job_failed_count = 0

    if isinstance(yaml_data, dict):
        for key, value in yaml_data.items():
            if key == 'plan-failed':
                plan_failed_count += 1
            elif key == 'job-failed':
                job_failed_count += 1
            total_sub_failed = count_failed_statuses(value)
            plan_failed_count += total_sub_failed
            job_failed_count += total_sub_failed

    elif isinstance(yaml_data, list):
        for item in yaml_data:
            total_sub_failed = count_failed_statuses(item)
            plan_failed_count += total_sub_failed
            job_failed_count += total_sub_failed

    return plan_failed_count + job_failed_count


def count_stages(yaml_data):
    stages = yaml_data.get('stages', [])

    return len(stages)

def get_test_framework(yaml_data):
    if not yaml_data:
        return False

    test_indicators = ['test', 'unit_test', 'test_tools', 'test_script', 'testing']

    def explore(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if any(indicator in key.lower() for indicator in test_indicators):
                    return True
                if explore(value):
                    return True
        elif isinstance(data, list):
            for item in data:
                if explore(item):
                    return True
        return False

    return explore(yaml_data)


def count_nexus_urls(yaml_content, nexus_urls):
    if not yaml_content or not isinstance(yaml_content, (dict, list)):
        return 0

    yaml_str = yaml.dump(yaml_content)
    count = 0
    for url in nexus_urls:
        count += len(re.findall(re.escape(url), yaml_str))
    return count

def extract_nexus_urls(yaml_data, nexus_urls):
    if not yaml_data or not isinstance(yaml_data, (dict, list)):
        return []

    yaml_str = yaml.dump(yaml_data, default_flow_style=False)
    found_urls = []

    for url in nexus_urls:
        if re.search(re.escape(url), yaml_str):
            found_urls.append(url)

    return found_urls


def get_build_tools(yaml_data):
    if not yaml_data:
        return []

    build_tools_indicators = [
        'maven', 'gradle', 'ant', 'make', 'msbuild', 'npm', 'yarn', 'webpack', 'gulp', 'docker', 'AMS/bamboo-oci-pack-build'
    ]

    found_tools = []

    def explore(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if any(tool in key.lower() for tool in build_tools_indicators):
                    if key not in found_tools:
                        found_tools.append(key)
                explore(value)
        elif isinstance(data, list):
            for item in data:
                explore(item)

    explore(yaml_data)
    return found_tools


def get_caching_strategy(yaml_data):
    caching_indicators = ['caching-etag', 'npm cache', 'nodejs cache', 'cache-on-agents']
    if not yaml_data:
        return []

    caching_strategies = set()

    def explore(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if any(indicator in key.lower() for indicator in caching_indicators):
                    caching_strategies.add(f"{key}: {value}")
                if isinstance(value, str) and any(indicator in value.lower() for indicator in caching_indicators):
                    caching_strategies.add(f"{key}: {value}")
                explore(value)
        elif isinstance(data, list):
            for item in data:
                explore(item)

    explore(yaml_data)
    return list(caching_strategies)

def get_parallel_execution(yaml_data):
    if not yaml_data:
        return False

    parallel_keywords = ['parallel', 'parallelism', 'concurrency', 'max-parallel','-Dparallel']
    parallel_conf = set()

    def explore(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if any(indicator in key.lower() for indicator in parallel_keywords):
                    parallel_conf.add(f"{key}: {value}")
                if isinstance(value, str) and any(indicator in value.lower() for indicator in parallel_keywords):
                    parallel_conf.add(f"{key}: {value}")
                explore(value)
        elif isinstance(data, list):
            for item in data:
                explore(item)

    explore(yaml_data)

    return len(parallel_conf) > 0


def get_manual_approval_steps(yaml_data):
    if not yaml_data:
        return False

    manual_keywords = ['manually', 'manual', 'manual-approval']
    manual_conf = set()

    def explore(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if any(indicator in key.lower() for indicator in manual_keywords):
                    manual_conf.add(f"{key}: {value}")
                if isinstance(value, str) and any(indicator in value.lower() for indicator in manual_keywords):
                    manual_conf.add(f"{key}: {value}")
                explore(value)
        elif isinstance(data, list):
            for item in data:
                explore(item)

    explore(yaml_data)

    return len(manual_conf) > 0


def get_resources_needed(yaml_data):
    if not yaml_data:
        return set()

    resource_keywords = {'<insert_keywords>'}
    resources = set()

    def explore(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if any(indicator in key.lower() for indicator in resource_keywords):
                    resources.add(f"{key}: {value}")
                if isinstance(value, str) and any(indicator in value.lower() for indicator in resource_keywords):
                    resources.add(f"{key}: {value}")
                explore(value)
        elif isinstance(data, list):
            for item in data:
                explore(item)

    explore(yaml_data)

    return resources


def get_agents(yaml_data):
    if not yaml_data:
        return set()

    agent_keywords = {keyword.lower() for keyword in {'<insert_keywords>'}}

    agents = set()

    def explore(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key.lower() in agent_keywords:
                    agents.add(key)

                if isinstance(value, str):
                    for keyword in agent_keywords:
                        if keyword in value.lower():
                            agents.add(keyword)

                explore(value)

        elif isinstance(data, list):
            for item in data:
                explore(item)

    explore(yaml_data)
    return agents

def analyze_patterns(data):
    keywords = {'<insert_keywords>'}

    matching_keywords = data['build_agents'].apply(
        lambda x: any(keyword.lower() in str(x).lower() for keyword in keywords) if pd.notnull(x) else False
    )

    filtered_keywords = data['build_agents'][matching_keywords]
    non_matching = data['build_agents'][~matching_keywords]

    pattern_counts = filtered_keywords.apply(
        lambda x: frozenset([keyword.lower() for keyword in keywords if keyword.lower() in str(x).lower()])
    ).value_counts()

    pattern_counts[('None',)] = len(non_matching)

    return pattern_counts



def extract_kpis(yaml_data):
    if not isinstance(yaml_data, dict):

        return {}

    kpis = {
        "num_plans": count_plans(yaml_data),
        "num_stages": count_stages(yaml_data),
        "num_jobs": count_jobs(yaml_data),
        "num_tasks": count_tasks(yaml_data),
        "num_triggers": count_triggers(yaml_data),
        "num_dependencies": count_dependencies(yaml_data),
        "num_artifacts": count_artifacts(yaml_data),
        "version": get_version(yaml_data),
        "num_environments": count_environments(yaml_data),
        "failure_handling_retry": count_retry_in_seconds(yaml_data),
        "failure_handling_notify": count_failed_statuses(yaml_data),
        "env_variables": count_environment_variables(yaml_data),
        "test_frameworks": get_test_framework(yaml_data),
        "build_tools": get_build_tools(yaml_data),
        "caching_strategy": get_caching_strategy(yaml_data),
        "parallel_execution": get_parallel_execution(yaml_data),
        "manual_approval_steps": get_manual_approval_steps(yaml_data),
        "resources_needed": get_resources_needed(yaml_data),
        "build_agents": get_agents(yaml_data),
    }
    return kpis

