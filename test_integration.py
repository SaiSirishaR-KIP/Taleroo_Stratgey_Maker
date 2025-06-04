import json
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required environment variables
integration_agent_id = os.getenv("INTEGRATION_AGENT_ID")
if not integration_agent_id:
    raise ValueError("INTEGRATION_AGENT_ID environment variable is not set. Please check your .env file.")

# Initialize integration agent
integration_agent = OpenAIAssistantRunnable(
    assistant_id=integration_agent_id,
    as_agent=True
)

# Load user profile
try:
    with open('user_profile.json', 'r') as f:
        user_profile = json.load(f)
        
    # Format input for agent with integration analysis categories
    input_dict = {
        "content": f"""Please analyze the following user profile and provide your analysis in JSON format:
        {json.dumps(user_profile, indent=2)}
        
        {{
            "integrations_analyse": {{
                "finanzielle_unterstützung": {{
                    "bedarf": "",
                    "möglichkeiten": []
                }},
                "jobcenter_anbindung": {{
                    "status": "",
                    "empfehlungen": []
                }},
                "sprachliche_integration": {{
                    "bedarf": "",
                    "kursempfehlungen": []
                }},
                "zusätzliche_unterstützung": []
            }}
        }}"""
    }
    
    # Get agent response
    print("\nInvoking agent...")
    response = integration_agent.invoke(input_dict)
    
    # Get the output from return_values
    if hasattr(response, 'return_values') and 'output' in response.return_values:
        output = response.return_values['output']
    else:
        output = str(response)
    
    # Print the output
    print("\nIntegration Agent Analysis:")
    print("="*50)
    print(output)
    
    # Save to file
    with open('prompts/integration_analysis.txt', 'w') as f:
        f.write(output)
    print("\nSaved analysis to integration_analysis.txt")

except Exception as e:
    print(f"Error: {str(e)}")
