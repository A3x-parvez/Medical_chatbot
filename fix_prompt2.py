#!/usr/bin/env python3
"""Fix prompt template to remove rejection messages."""

with open('backend/retriever.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace the guidelines section
new_lines = []
i = 0
while i < len(lines):
    if 'Guidelines:' in lines[i] and i > 50:  # Found the prompt template guidelines
        new_lines.append(lines[i])  # Keep "Guidelines:"
        i += 1
        # Skip old guidelines (next 6 lines)
        while i < len(lines) and not lines[i].strip().startswith('Context:'):
            i += 1
        # Add new guidelines
        new_guidelines = [
            "            - Answer all medical or health-related questions directly and clearly (3–6 sentences).\n",
            "            - For sensitive topics (reproductive health, sexual issues, etc.), provide the same professional medical answer as any other health question.\n",
            "            - Never apologize or say you can't answer medical questions—just answer them.\n",
            "            - Never mention any documents, retrieval systems, or external data.\n",
            "            - Keep a confident, compassionate, professional tone.\n",
            "\n"
        ]
        new_lines.extend(new_guidelines)
    else:
        new_lines.append(lines[i])
        i += 1

with open('backend/retriever.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Fixed prompt template - removed rejection messages")
