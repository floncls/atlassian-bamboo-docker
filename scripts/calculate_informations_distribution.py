def calculate_yaml_depth_distribution(data):
    depth_counts = data['YAMLDepth'].value_counts().reset_index()
    depth_counts.columns = ['YAMLDepth', 'Count']
    return depth_counts

def calculate_plans_distributions(data):
    num_plans = data['num_plans'].value_counts().reset_index()
    num_plans.columns = ['num_plans', 'Count']
    return num_plans

def calculate_stages_distributions(data):
    num_stages = data['num_stages'].value_counts().reset_index()
    num_stages.columns = ['num_stages', 'Count']
    return num_stages

def calculate_jobs_distributions(data):
    num_jobs = data['num_jobs'].value_counts().reset_index()
    num_jobs.columns = ['num_jobs', 'Count']
    return num_jobs

def calculate_tasks_distributions(data):
    num_tasks = data['num_tasks'].value_counts().reset_index()
    num_tasks.columns = ['num_tasks', 'Count']
    return num_tasks


