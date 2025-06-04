import json
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize employment agent
employment_agent = OpenAIAssistantRunnable(
    assistant_id=os.getenv("EMPLOYMENT_AGENT_ID"),
    as_agent=True
)

# Load user profile
try:
    with open('user_profile.json', 'r') as f:
        user_profile = json.load(f)
        
    # Format input for agent with JSON format requirement
    input_dict = {
        "content": f"""Please analyze the following user profile and provide your analysis in JSON format:
        {json.dumps(user_profile, indent=2)}
        
        Your response should be in JSON format with the following structure:
        {{
            "analysis": {{
                "employment_opportunities": [],
                "skill_gaps": [],
                "recommendations": []
            }}
        }}"""
    }
    
    # Get agent response
    print("\nInvoking agent...")
    response = employment_agent.invoke(input_dict)
    
    # Get the output from return_values
    if hasattr(response, 'return_values') and 'output' in response.return_values:
        output = response.return_values['output']
    else:
        output = str(response)
    
    # Print the output
    print("\nEmployment Agent Analysis:")
    print("="*50)
    print(output)
    
    # Save to file
    with open('prompts/employment_analysis.txt', 'w') as f:
        f.write(output)
    print("\nSaved analysis to employment_analysis.txt")

except Exception as e:
    print(f"Error: {str(e)}")
