import json
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required environment variables
social_agent_id = os.getenv("SOCIAL_AGENT_ID")
if not social_agent_id:
    raise ValueError("SOCIAL_AGENT_ID environment variable is not set. Please check your .env file.")

# Initialize social agent
social_agent = OpenAIAssistantRunnable(
    assistant_id=social_agent_id,
    as_agent=True
)

# Load user profile
try:
    with open('user_profile.json', 'r') as f:
        user_profile = json.load(f)
        
    # Format input for agent with social analysis categories
    input_dict = {
        "content": f"""Please analyze the following user profile and provide your analysis in JSON format:
        {json.dumps(user_profile, indent=2)}
        
        {{
            "soziale_analyse": {{
                "alleinerziehend": {{
                    "situation": "",
                    "empfehlungen": []
                }},
                "drogenabhängigkeit": {{
                    "situation": "",
                    "empfehlungen": []
                }},
                "wohnverhältnisse": {{
                    "situation": "",
                    "empfehlungen": []
                }},
                "zusätzliche_unterstützung": []
            }}
        }}"""
    }
    
    # Get agent response
    print("\nInvoking agent...")
    response = social_agent.invoke(input_dict)
    
    # Get the output from return_values
    if hasattr(response, 'return_values') and 'output' in response.return_values:
        output = response.return_values['output']
    else:
        output = str(response)
    
    # Print the output
    print("\nSocial Agent Analysis:")
    print("="*50)
    print(output)
    
    # Save to file
    with open('prompts/social_analysis.txt', 'w') as f:
        f.write(output)
    print("\nSaved analysis to social_analysis.txt")

except Exception as e:
    print(f"Error: {str(e)}")
