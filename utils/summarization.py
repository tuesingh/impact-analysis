import anthropic

def summarize_with_claude(text, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"Summarize this regulatory update for a compliance officer in 2 sentences:\n\n{text}"
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=300,
        temperature=0.2,
        system="You are a compliance assistant.",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
