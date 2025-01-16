import pandas as pd
import plotly.express as px


def generate_complexity_categorization_benchmark(dataset):
    complexity_counts = dataset['complexity_tier'].value_counts()

    color_map = {
        'Low': '#0093F5',
        'Medium': '#FFC401',
        'High': '#F50000',
        'N/A': '#808080'
    }

    fig = px.pie(dataset,
                 names='complexity_tier',
                 title='Complexity of current Bamboo pipelines',
                 color='complexity_tier',
                 color_discrete_map=color_map,
                 hole=.4)

    fig.update_traces(textinfo='percent+label+value',
                      textposition='inside')

    fig.for_each_trace(lambda t: t.update(text=[f"{label} ({complexity_counts[label]} pipelines)"
                                               for label in t.labels]))

    fig.show()

def generate_pipeline_types_parity_benchmark(full_dataset, ci_datased, cd_dataset):
    full_dataset = len(full_dataset)
    ci = len(ci_datased)
    cd = len(cd_dataset)
    total = ci + cd
    na = full_dataset - total
    dataset = {
        'Category': ['CI', 'CD','N/A'],
        'Count': [ci, cd, na]
    }

    df = pd.DataFrame(dataset)

    fig = px.pie(df,
                 names='Category',
                 values='Count',
                 hole=.4)

    fig.show()


def generate_complexity_disparity_diagram(dataset):
    df = dataset['complexity']

    fig = px.histogram(df, x="complexity", nbins=100, title="Complexity of pipelines",
                       histnorm="percent")

    mean_complexity = df.mean()
    fig.add_vline(x=mean_complexity, line_dash="dash", line_color="red",
                  annotation_text=f"Average: {mean_complexity:.2f}", annotation_position="top left")

    fig.update_xaxes(title="Pipeline complexity level", range=[1, 500])
    fig.update_yaxes(title="Percentage (%)")

    fig.update_traces(marker_color="blue", opacity=0.75)
    fig.update_layout(template="plotly_white", bargap=0.2)

    fig.show()