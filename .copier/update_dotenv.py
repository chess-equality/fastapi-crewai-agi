from pathlib import Path
import json

# Update .env.local with the answers from the .copier-answers.yml file
# without using Jinja2 templates. .env.example remains the reference template.
root_path = Path(__file__).parent.parent
answers_path = Path(__file__).parent / ".copier-answers.yml"
answers = json.loads(answers_path.read_text())

template_path = root_path / ".env.example"
output_path = root_path / ".env.local"

env_content = template_path.read_text()
lines = []
for line in env_content.splitlines():
    for key, value in answers.items():
        upper_key = key.upper()
        if line.startswith(f"{upper_key}="):
            if " " in value:
                content = f"{upper_key}={value!r}"
            else:
                content = f"{upper_key}={value}"
            new_line = line.replace(line, content)
            lines.append(new_line)
            break
    else:
        lines.append(line)
output_path.write_text("\n".join(lines))
