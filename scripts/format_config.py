import re
import html
import yaml


def clean_yaml_content(yaml_content):
    cleaned_content = re.sub(r'(\S)\n(\S)', r'\1 \2', yaml_content)
    cleaned_content = re.sub(r'\n+', ' ', cleaned_content)
    cleaned_content = re.sub(r'^\s*\n', '', cleaned_content, flags=re.MULTILINE)
    cleaned_content = re.sub(r'^\s*$', '', cleaned_content, flags=re.MULTILINE)
    cleaned_content = re.sub(r'&quot;', '"', yaml_content)
    cleaned_content = re.sub(r'&lt;', '<', cleaned_content)
    cleaned_content = re.sub(r'&gt;', '>', cleaned_content)
    cleaned_content = re.sub(r'&amp;', '&', cleaned_content)
    cleaned_content = re.sub(r'---', '', cleaned_content)
    cleaned_content = re.sub(r'"', '', cleaned_content)
    cleaned_content = re.sub(r'\.\.\.', '', cleaned_content)

    cleaned_content = cleaned_content.strip()

    return cleaned_content


def format_script(script: str) -> str:
    script = script.replace("&quot;", '"').replace("&amp;", '&').replace("&lt;", "<").replace("&gt;", ">")
    script = script.replace(r"\n", "\n")
    script = re.sub(r'echo "fake".*', '', script)  # Supprimer les lignes echo "fake"
    script = re.sub(r'#.*', '', script)  # Suppression des commentaires
    script = re.sub(r'\${([^}]+)}', r'${\1}', script)  # Formatage propre des variables d'environnement
    script = re.sub(r'\s+', ' ', script)
    script = script.strip()
    script = "|\n  " + "\n  ".join(script.splitlines())

    return script


def reformat_scripts_yaml(yaml_data):
    try:
        decoded_yaml = html.unescape(yaml_data)
        data = yaml.safe_load(decoded_yaml)
        formatted_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return formatted_yaml
    except Exception as e:
        return None


def sanitize_sensitive_data(data):
    sensitive_keywords = [
        'password', 'passwd', 'secret', 'token', 'private_key', 'private-key', 'public-key', 'public_key', 'key', 'cert', 'ssh', 'auth'
    ]

    def explore(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if any(sensitive_word in key.lower() for sensitive_word in sensitive_keywords):
                    data[key] = '[REDACTED]'
                else:
                    explore(value)
        elif isinstance(data, list):
            for item in data:
                explore(item)

    explore(data)

    return data