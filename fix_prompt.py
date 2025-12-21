#!/usr/bin/env python3
"""Fix prompt template to remove rejection messages and emphasize direct answers."""

with open('backend/retriever.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the rejection message guidelines with direct answer guidelines
old_guidelines = '''            Guidelines:
            - If the question is medical or health-related, give a short and direct answer (3–6 sentences).
            - If the question is unrelated to medicine (e.g., politics, sports, entertainment, etc.), 
              respond only with: "I'm sorry, but I can only answer medical or health-related questions."
            - Do not combine that message with a valid medical answer.
            - Never mention any documents, retrieval systems, or external data.
            - Keep a confident, compassionate tone suitable for a trusted medical advisor.'''

new_guidelines = '''            Guidelines:
            - Answer all medical or health-related questions directly and clearly (3–6 sentences).
            - For sensitive topics (reproductive health, sexual issues, etc.), provide the same professional medical answer as any other health question.
            - Never apologize or say you can't answer medical questions—just answer them.
            - Never mention any documents, retrieval systems, or external data.
            - Keep a confident, compassionate, professional tone.'''

content = content.replace(old_guidelines, new_guidelines)

# Also update the role description to mention no apologies
old_role = '''            - Reproductive and sexual health (including menstruation, pregnancy, first-time sex, hygiene, contraception, etc.).
            Always answer these topics with clarity, empathy, and professionalism.'''

new_role = '''            - Reproductive and sexual health (including penis pain, menstruation, pregnancy, first-time sex, hygiene, contraception, etc.).
            Always answer these topics with clarity, empathy, and professionalism—without apologies.'''

content = content.replace(old_role, new_role)

with open('backend/retriever.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated prompt template successfully")
