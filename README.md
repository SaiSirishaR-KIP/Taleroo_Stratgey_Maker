# Strategy Maker

This script generates personalized strategies using OpenAI assistants to analyze user profiles and create comprehensive action plans.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
INTEGRATION_AGENT_ID=your_integration_agent_id
SOCIAL_AGENT_ID=your_social_agent_id
EMPLOYMENT_AGENT_ID=your_employment_agent_id
STRATEGY_COMPOSER_ID=your_strategy_composer_id
```

3. Prepare your `user_profile.json` file with the user's information.

4. Wrapers around OpenAI assistants for different tasks: test_employment.py, test_social.py, test_integration.py

### modify the categories to be extracted from each of the agent calls.

5. Strategy_composer --> feeds on user profile, agent recommendations and communicates with the assistant, startegy_maker for a timeline need to be followed by the users to reach their goal.

## Usage

Run the script:
```bash
python strategy_composer.py
```

The script will:
1. Load the user profile from `user_profile.json`
2. Send the profile to three specialized agents:
   - Integration Agent
   - Social Agent
   - Employment Agent
3. Collect the outputs from all agents
4. Send the combined outputs to the Meta agent - Strategy Maker
5. Generate a final strategy in `generated_strategy.json` using strategy_composer.py

## Output

The script generates a `generated_strategy.json` file containing the final strategy composed from all agent analyses.



