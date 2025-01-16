import yaml

def extract_plugin_keys(yaml_content):
    plugin_keys_set = set()
    for stage in yaml_content.get('stages', []):
        for stage_name, stage_details in stage.items():
            for job_name in stage_details.get('jobs', []):
                if job_name in yaml_content:
                    tasks = yaml_content[job_name].get('tasks', [])
                    if tasks:
                        for task in tasks:
                            if 'any-task' in task:
                                plugin_key = task['any-task'].get('plugin-key')
                                if plugin_key:
                                    plugin_keys_set.add(plugin_key)
    return plugin_keys_set

def count_custom_plugins(data, plugin_keys):
    plugin_counts = {plugin: 0 for plugin in plugin_keys}

    if isinstance(data, str):
        try:
            yaml_content = yaml.safe_load(data)

            plugins_in_config = extract_plugin_keys(yaml_content)

            for plugin in plugin_keys:
                plugin_counts[plugin] = sum(1 for p in plugins_in_config if p == plugin)

        except yaml.YAMLError as e:
            print(f"Erreur lors du parsing YAML: {e}")

    return plugin_counts

def analyse_plugins_repartition(data, counts):
    plugin_counts = {plugin: 0 for plugin in counts}

    for config in data:
        if isinstance(config, str):
            count_result = count_custom_plugins(config, counts)
            for plugin, count in count_result.items():
                plugin_counts[plugin] += count

    return plugin_counts


def analyse_native_plugins_repartition(data, native_plugin_keys):
    plugin_counts = {plugin: 0 for plugin in native_plugin_keys}

    for config in data:
        if isinstance(config, str):
            count_result = count_native_plugins(config, native_plugin_keys)
            for plugin, count in count_result.items():
                plugin_counts[plugin] += count

    return plugin_counts

def count_native_plugins(data, native_plugin_keys):
    plugin_counts = {plugin: 0 for plugin in native_plugin_keys}

    if isinstance(data, str):
        try:
            yaml_content = yaml.safe_load(data)
            plugins_in_config = extract_task_keys(yaml_content)

            for plugin in native_plugin_keys:
                plugin_counts[plugin] = sum(1 for p in plugins_in_config if p == plugin)

        except yaml.YAMLError as e:
            print(f"Erreur lors du parsing YAML: {e}")

    return plugin_counts

def extract_task_keys(yaml_content):
    task_keys_set = set()

    for stage in yaml_content.get('stages', []):
        for stage_details in stage.values():
            for job_name in stage_details.get('jobs', []):
                job_details = yaml_content.get(job_name, {})
                tasks = job_details.get('tasks', [])

                if isinstance(tasks, list):
                    for task in tasks:
                        if isinstance(task, dict):
                            for key in task.keys():
                                if key != 'any-task':
                                    task_keys_set.add(key)
    return task_keys_set

def sort_cd_and_ci_pipelines(dataset):
    cd_pipelines = dataset[dataset['NexusURLCount'] > 0]
    ci_pipelines = dataset[dataset['NexusURLCount'] <= 0]
    return ci_pipelines, cd_pipelines
