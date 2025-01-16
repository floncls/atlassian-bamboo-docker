from save_to_excel import parse_yaml_from_excel, add_data_to_sheet
from calculate_complexity import calculate_complexity, categorize_complexity
from fetch_plugin_informations import sort_cd_and_ci_pipelines, analyse_plugins_repartition, analyse_native_plugins_repartition
from fetch_script_commands import analyse_scripts_length
from generate_basic_kpis import analyze_patterns
from calculate_informations_distribution import calculate_yaml_depth_distribution, calculate_plans_distributions, calculate_stages_distributions, calculate_jobs_distributions, calculate_tasks_distributions
from generate_graphs import *
import pandas as pd

if __name__ == "__main__":
    NEXUS_URLS = []
    excel_file_path = '../bamboo_export/<your_file_name>'
    parsed_df = parse_yaml_from_excel(excel_file_path, NEXUS_URLS, sheet_name='', yaml_column='yaml')
    parsed_df.to_excel('./kpi_output/<your_file_name>', index=False, engine='openpyxl', sheet_name="Parsed Data with KPIs")
    print("KPI definition done.  Adding extra informations....")


    data = pd.read_excel("kpi_output/<your_file_name>")
    updated_data = calculate_complexity(data)
    updated_data['complexity_tier'] = updated_data['complexity'].apply(categorize_complexity)
    num_pipelines_with_nexus_url = updated_data[updated_data['NexusURLCount'] > 0].shape[0]
    pipelines_ci, pipelines_cd = sort_cd_and_ci_pipelines(data)

    external_plugin_keys = []

    native_plugin_keys = []


    external_plugin_counts = analyse_plugins_repartition(data['yaml'], external_plugin_keys)
    external_plugin_counts_df = pd.DataFrame(list(external_plugin_counts.items()), columns=['Custom Plugins', 'Number'])
    native_plugin_counts = analyse_native_plugins_repartition(data['yaml'], native_plugin_keys)
    native_plugin_counts_df = pd.DataFrame(list(native_plugin_counts.items()), columns=['Native Plugins', 'Number'])
    scripts_length = analyse_scripts_length(data['yaml'])

    add_data_to_sheet("./kpi_output/<your_file_name>", 'CI Pipelines Agent Patterns', analyze_patterns(pipelines_ci))
    add_data_to_sheet("./kpi_output/<your_file_name>", 'CD Pipelines Agent Patterns', analyze_patterns(pipelines_cd))
    add_data_to_sheet("./kpi_output/<your_file_name>", 'Depth level Average', calculate_yaml_depth_distribution(data))
    add_data_to_sheet("./kpi_output/<your_file_name>", 'Average Plans Number', calculate_plans_distributions(data))
    add_data_to_sheet("./kpi_output/<your_file_name>", 'Average Stages Number', calculate_stages_distributions(data))
    add_data_to_sheet("./kpi_output/<your_file_name>", 'Average Jobs Number', calculate_jobs_distributions(data))
    add_data_to_sheet("./kpi_output/<your_file_name>", 'Average Tasks Number', calculate_tasks_distributions(data))
    add_data_to_sheet("./kpi_output/<your_file_name>", 'External Plugins patterns',external_plugin_counts_df)
    add_data_to_sheet("./kpi_output/<your_file_name>", 'Native Plugins patterns',native_plugin_counts_df)
    add_data_to_sheet("./kpi_output/<your_file_name>", 'Script length',scripts_length)

    generate_complexity_categorization_benchmark(updated_data)
    generate_complexity_categorization_benchmark(pipelines_ci)
    generate_complexity_categorization_benchmark(pipelines_cd)
    generate_pipeline_types_parity_benchmark(updated_data, pipelines_ci, pipelines_cd)
    generate_complexity_disparity_diagram(pipelines_ci)
    generate_complexity_disparity_diagram(pipelines_cd)