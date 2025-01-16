import pandas as pd

def calculate_w1(depth):
    max_depth = depth.max()
    if max_depth == 0:
        raise ValueError("YAMLDepth contains only null values")

    thresholds = [0.2 * max_depth, 0.4 * max_depth, 0.6 * max_depth, 0.8 * max_depth, max_depth]

    def assign_weight(depth_value):
        if depth_value <= thresholds[0]:
            return 1
        elif depth_value <= thresholds[1]:
            return 2
        elif depth_value <= thresholds[2]:
            return 3
        elif depth_value <= thresholds[3]:
            return 4
        else:
            return 5

    return depth.apply(assign_weight)


def calculate_w2(num_keys):
    max_keys = num_keys.max()
    thresholds = [0.15 * max_keys, 0.33 * max_keys, 0.66 * max_keys, max_keys]

    def assign_weight(key_count):
        if key_count <= thresholds[0]:
            return 0.5
        elif key_count <= thresholds[1]:
            return 1
        elif key_count <= thresholds[2]:
            return 2
        else:
            return 3

    return num_keys.apply(assign_weight)


def calculate_w3(num_jobs):
    thresholds = [4, 8, 12, 16, 20]

    def assign_weight(job_count):
        if job_count <= thresholds[0]:
            return 1
        elif job_count <= thresholds[1]:
            return 2
        elif job_count <= thresholds[2]:
            return 3
        elif job_count <= thresholds[3]:
            return 4
        else:
            return 5

    return num_jobs.apply(assign_weight)


def calculate_w4(num_stages):
    thresholds = [3, 6, 10]

    def assign_weight(stage_count):
        if stage_count <= thresholds[0]:
            return 1
        elif stage_count <= thresholds[1]:
            return 2
        else:
            return 3

    return num_stages.apply(assign_weight)


def calculate_w5(num_artifacts):
    thresholds = [3, 6, 10]

    def assign_weight(artifact_count):
        if artifact_count <= thresholds[0]:
            return 2
        elif artifact_count <= thresholds[1]:
            return 3
        else:
            return 4

    return num_artifacts.apply(assign_weight)


def calculate_w6(triggers):
    thresholds = [3, 6, 10]

    def assign_weight(trigger_count):
        if trigger_count <= thresholds[0]:
            return 1
        elif trigger_count <= thresholds[1]:
            return 2
        else:
            return 3

    return triggers.apply(assign_weight)


def calculate_w7(tasks):
    max_tasks = tasks.max()
    if max_tasks == 0:
        raise ValueError("Tasks column contains only null values")

    thresholds = [0.2 * max_tasks, 0.4 * max_tasks, 0.6 * max_tasks, 0.8 * max_tasks, max_tasks]

    def assign_weight(task_count):
        if task_count <= thresholds[0]:
            return 1
        elif task_count <= thresholds[1]:
            return 2
        elif task_count <= thresholds[2]:
            return 3
        elif task_count <= thresholds[3]:
            return 4
        else:
            return 5

    return tasks.apply(assign_weight)


def calculate_complexity(dataset):
    depth = dataset["YAMLDepth"]
    num_keys = dataset["YAMLNumKeys"]
    num_jobs = dataset["num_jobs"]
    num_stages = dataset["num_stages"]
    num_artifacts = dataset["num_artifacts"]
    triggers = dataset["num_triggers"]
    tasks = dataset["num_tasks"]

    w1 = calculate_w1(depth)
    w2 = calculate_w2(num_keys)
    w3 = calculate_w3(num_jobs)
    w4 = calculate_w4(num_stages)
    w5 = calculate_w5(num_artifacts)
    w6 = calculate_w6(triggers)
    w7 = calculate_w7(tasks)

    dataset["complexity"] = (
            (w1 * depth) +
            (w2 * num_keys) +
            (w3 * num_jobs) +
            (w4 * num_stages) +
            (w5 * num_artifacts) +
            (w6 * triggers) +
            (w7 * tasks)
    )
    return dataset


def categorize_complexity(complexity):
    if pd.isna(complexity) or complexity == 'N/A' or complexity == '':
        return 'N/A'

    try:
        complexity = float(complexity)
    except ValueError:
        return 'N/A'

    if complexity < 50:
        return 'Low'
    elif complexity <= 150:
        return 'Medium'
    else:
        return 'High'