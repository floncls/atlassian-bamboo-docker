from generate_basic_kpis import extract_nexus_urls,calculate_yaml_complexity, extract_kpis
from format_config import clean_yaml_content, sanitize_sensitive_data
import pandas as pd
import yaml

def parse_yaml_from_excel(excel_file_path, nexus_url_list, sheet_name='<insert_keywords>', yaml_column='yaml'):
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)

    if yaml_column not in df.columns:
        return df

    # Create a copy of the original YAML data
    sanitized_yamls = []
    parsed_data = []
    complexity_data = []
    kpis_data = []
    nexus_url_counts = []
    nexus_url_column = []

    for idx, yaml_content in df[yaml_column].items():
        if isinstance(yaml_content, str):
            yaml_content = yaml_content.strip()
            if not yaml_content:
                parsed_data.append(None)
                complexity_data.append((None, None))
                kpis_data.append(None)
                nexus_url_counts.append(0)
                nexus_url_column.append([])
                sanitized_yamls.append(None)
                continue

            try:
                cleaned_yaml_content = clean_yaml_content(yaml_content)
                parsed_docs = list(yaml.safe_load_all(cleaned_yaml_content))
                if not parsed_docs:
                    parsed_data.append(None)
                    complexity_data.append((None, None))
                    kpis_data.append(None)
                    nexus_url_counts.append(0)
                    nexus_url_column.append([])
                    sanitized_yamls.append(None)
                    continue

                parsed_yaml = parsed_docs[0] if isinstance(parsed_docs[0], dict) else None
                sanitized_yaml = sanitize_sensitive_data(cleaned_yaml_content)
                sanitized_parsed_yaml = sanitize_sensitive_data(parsed_yaml)

                parsed_data.append(sanitized_parsed_yaml)
                sanitized_yamls.append(sanitized_yaml)

                if sanitized_yaml:
                    depth, num_keys = calculate_yaml_complexity(sanitized_parsed_yaml)
                    nexus_urls_found = extract_nexus_urls(sanitized_parsed_yaml, nexus_url_list)
                    nexus_url_count = len(nexus_urls_found)
                else:
                    depth, num_keys, nexus_url_count = None, None, 0

                complexity_data.append((depth, num_keys))
                kpis = extract_kpis(sanitized_parsed_yaml)
                kpis_data.append(kpis)
                nexus_url_counts.append(nexus_url_count)
                nexus_url_column.append(nexus_urls_found)

            except yaml.YAMLError as e:
                if "mapping values are not allowed here" in str(e):
                    parsed_data.append("YAML with script")
                    complexity_data.append((None, None))
                    kpis_data.append(None)
                    nexus_url_counts.append(0)
                    nexus_url_column.append([])
                    sanitized_yamls.append(None)
                else:
                    parsed_data.append(None)
                    complexity_data.append((None, None))
                    kpis_data.append(None)
                    nexus_url_counts.append(0)
                    nexus_url_column.append([])
                    sanitized_yamls.append(None)
            except Exception as e:
                parsed_data.append(None)
                complexity_data.append((None, None))
                kpis_data.append(None)
                nexus_url_counts.append(0)
                nexus_url_column.append([])
                sanitized_yamls.append(None)

    df['yaml'] = sanitized_yamls
    df['YAMLNumKeys'] = [comp[1] for comp in complexity_data]
    df['NexusURLCount'] = nexus_url_counts
    df['NexusURLs'] = nexus_url_column
    df['YAMLDepth'] = [comp[0] for comp in complexity_data]

    kpi_columns = [
        "num_plans", "num_stages", "num_jobs", "num_tasks", "num_triggers",
        "num_dependencies", "num_artifacts", "version", "num_environments",
        "failure_handling_retry", "failure_handling_notify", "env_variables",
        "test_frameworks", "build_tools", "caching_strategy", "parallel_execution",
        "manual_approval_steps", "resources_needed", "build_agents"
    ]

    for kpi in kpi_columns:
        df[kpi] = [kpi_data.get(kpi, 'N/A') if kpi_data else 'N/A' for kpi_data in kpis_data]

    return df

def add_data_to_sheet(file_path, sheet_name, data):
    if isinstance(data, pd.Series):
        data = data.reset_index()

    if isinstance(data, pd.DataFrame):
        for col in data.columns:
            data[col] = data[col].map(
                lambda x: ", ".join(x) if isinstance(x, frozenset) else x
            )

    try:
        with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            data.to_excel(writer, sheet_name=sheet_name, index=False)
    except FileNotFoundError:
        with pd.ExcelWriter(file_path, mode='w', engine='openpyxl') as writer:
            data.to_excel(writer, sheet_name=sheet_name, index=False)