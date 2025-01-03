import json

def markdown_to_json(response: str) -> dict:
    """
    Cleans markdown code block formatting from a JSON string response.
    
    Args:
        response (str): Raw response string potentially containing markdown formatting
        
    Returns:
        dict: Cleaned JSON string with markdown formatting removed
    """
    response = response.replace("```json", "").replace("```", "").strip()
    return json.loads(response)