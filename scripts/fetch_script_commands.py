import re
from collections import Counter
import pandas as pd
import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


def categorize_script_complexity(length):
    if length is not 0:
        if length <= 0:
            raise ValueError("Length must be positive")
        elif length <= 700:
            result = 'Low'
        elif length <= 5000:
            result = 'Medium'
        else:
            result = 'High'
        return result


def analyse_scripts_length(data):
    sheet_data = {
        'Script': [],
        'Script length': [],
        'Complexity': []
    }
    for a in data:
        if pd.notna(a) and isinstance(a, str):
            try:
                parsed_data = yaml.safe_load(a)
                for key, value in parsed_data.items():
                    if key not in ['plan', 'stages', 'variables', 'repositories', 'triggers', 'notifications', 'labels',
                                   'dependencies', 'branches', 'plan-permissions', 'version', 'other']:
                        stage = value
                        for item in stage:
                            if item == 'tasks':
                                task = stage[item]
                                if task is not None and isinstance(task, list):
                                    for i_task in task:
                                        if isinstance(i_task, dict):
                                            for k, v in i_task.items():
                                                if k == 'script':
                                                    script = v
                                                    if isinstance(script, dict) and 'scripts' in script:
                                                        scripts = script['scripts']
                                                        for single_script in scripts:
                                                            if single_script is not None:
                                                                length = len(single_script)
                                                                complexity = categorize_script_complexity(length)

                                                                sheet_data['Script'].append(single_script)
                                                                sheet_data['Script length'].append(length)
                                                                sheet_data['Complexity'].append(complexity)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML: {e}")

    sheet = pd.DataFrame(sheet_data)
    return sheet

def extract_commands(script):
    # Enhanced pattern to catch more command types
    command_pattern = r'^[\w\.-]+|(?<=\|)\s*[\w\.-]+|(?<=&&)\s*[\w\.-]+'
    commands = re.findall(command_pattern, script, re.MULTILINE)
    return [cmd.strip() for cmd in commands if cmd.strip()]


def analyze_commands(yaml_data):
    all_scripts = []
    script_commands = []

    # Debug counter
    processed_scripts = 0

    for a in yaml_data:
        if pd.notna(a) and isinstance(a, str):
            try:
                parsed_data = yaml.safe_load(a)
                for key, value in parsed_data.items():
                    if key not in ['plan', 'stages', 'variables', 'repositories', 'triggers', 'notifications',
                                   'labels',
                                   'dependencies', 'branches', 'plan-permissions', 'version', 'other']:
                        stage = value
                        for item in stage:
                            if item == 'tasks':
                                task = stage[item]
                                if task is not None and isinstance(task, list):
                                    for i_task in task:
                                        if isinstance(i_task, dict):
                                            for k, v in i_task.items():
                                                if k == 'script':
                                                    script = v
                                                    if isinstance(script, dict) and 'scripts' in script:
                                                        for single_script in script['scripts']:
                                                            if single_script is None:
                                                                continue
                                                            if isinstance(single_script, str):
                                                                commands = extract_commands(single_script)
                                                                if commands:
                                                                    all_scripts.append(single_script)
                                                                    script_commands.append(' '.join(commands))

            except yaml.YAMLError as e:
                print(f"Error parsing YAML: {e}")

    print(f"\nTotal scripts processed: {processed_scripts}")
    print(f"Scripts with valid commands: {len(script_commands)}")

    if not script_commands:
        return pd.DataFrame(columns=['Command', 'Frequency']), {}, [], []

    all_commands = []
    for cmd_str in script_commands:
        all_commands.extend(cmd_str.split())

    command_counts = Counter(all_commands)
    command_df = pd.DataFrame(command_counts.items(), columns=['Command', 'Frequency'])
    command_df = command_df.sort_values(by='Frequency', ascending=False)

    if len(script_commands) >= 2:
        vectorizer = TfidfVectorizer(max_features=100, stop_words=None)
        command_features = vectorizer.fit_transform(script_commands)

        n_clusters = min(5, len(script_commands))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(command_features)

        # Analyze command patterns per cluster
        cluster_patterns = {}
        for i in range(n_clusters):
            cluster_scripts = [script_commands[j] for j in range(len(clusters)) if clusters[j] == i]
            cluster_commands = ' '.join(cluster_scripts).split()
            most_common = Counter(cluster_commands).most_common(5)
            cluster_patterns[f"Cluster {i}"] = most_common
    else:
        clusters = []
        cluster_patterns = {}

    return command_df, cluster_patterns, clusters, all_scripts

# Load and analyze data
data = pd.read_excel("kpi_output/parsed_output_with_kpis_and_complexity.xlsx")
yaml_data = data['yaml']
command_df, cluster_patterns, clusters, all_scripts = analyze_commands(yaml_data)

# Print basic statistics
print("\nCommand frequency analysis:")
print(command_df)

print('cluster patterns')
print(cluster_patterns)
