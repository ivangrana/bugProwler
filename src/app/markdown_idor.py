def generate_markdown(data):
    markdown = "# 🛡️ IDOR Heuristics Report\n\n"

    for idx, vulnerability in enumerate(data["vulnerabilities"], 1):
        markdown += f"---\n\n"
        markdown += f"## 🔍 Investigation #{idx}: `{vulnerability['path']}`\n\n"
        markdown += f"| **Attribute** | **Value** |\n"
        markdown += f"|:------------- |:--------- |\n"
        markdown += f"| **Path**      | `{vulnerability['path']}` |\n"
        markdown += f"| **Method**    | `{vulnerability['method']}` |\n\n"
        markdown += f"### 🧰 Attack Techniques\n\n"

        for j, attack in enumerate(vulnerability["attacks"], 1):
            markdown += f"{j}. {attack['technique']}\n\n"
            markdown += f"**Description:**\n\n"
            markdown += f"> {attack['description']}\n\n"
            if "example" in attack and attack["example"]:
                markdown += f"**Example Payload:**\n"
                markdown += f"```http\n{attack['example']}\n```\n\n"

        if "recommendations" in vulnerability and vulnerability["recommendations"]:
            markdown += f"### 🛠️ Recommendations\n\n"
            for rec in vulnerability["recommendations"]:
                markdown += f"- {rec}\n"
            markdown += "\n"

    return markdown
