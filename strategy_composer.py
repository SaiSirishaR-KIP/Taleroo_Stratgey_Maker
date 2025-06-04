import json
import os
import subprocess
import concurrent.futures
from typing import Dict, Any, List
from datetime import datetime, timedelta
from langchain.agents import AgentExecutor
from langchain.agents.openai_assistant.base import OpenAIAssistantRunnable
from dotenv import load_dotenv
import re

class StrategyComposer:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = prompts_dir
        self.analysis_files = {
            "employment": os.path.join(prompts_dir, "employment_analysis.txt"),
            "social": os.path.join(prompts_dir, "social_analysis.txt"),
            "integration": os.path.join(prompts_dir, "integration_analysis.txt")
        }
        self.test_scripts = {
            "employment": "test_employment.py",
            "social": "test_social.py",
            "integration": "test_integration.py"
        }
        # Load environment variables
        load_dotenv()
        # Initialize strategy assistant
        self.strategy_assistant = OpenAIAssistantRunnable(
            assistant_id=os.getenv("STRATEGY_ASSISTANT_ID"),
            as_agent=True
        )

    def run_single_script(self, script_type: str, script_name: str) -> tuple:
        """Run a single test script and return its result."""
        try:
            print(f"\nRunning {script_name}...")
            result = subprocess.run(['python', script_name], 
                                 capture_output=True, 
                                 text=True)
            
            if result.returncode == 0:
                print(f"Successfully ran {script_name}")
                return script_type, True, result.stdout
            else:
                print(f"Error running {script_name}:")
                print(result.stderr)
                return script_type, False, result.stderr
        except Exception as e:
            error_msg = f"Failed to run {script_name}: {str(e)}"
            print(error_msg)
            return script_type, False, error_msg

    def run_test_scripts(self):
        """Run all test scripts in parallel and collect their outputs."""
        print("Running test scripts in parallel...")
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all scripts to run in parallel
            future_to_script = {
                executor.submit(self.run_single_script, script_type, script_name): script_type
                for script_type, script_name in self.test_scripts.items()
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_script):
                script_type = future_to_script[future]
                try:
                    script_type, success, output = future.result()
                    results[script_type] = {
                        "success": success,
                        "output": output
                    }
                except Exception as e:
                    print(f"Error processing {script_type}: {str(e)}")
                    results[script_type] = {
                        "success": False,
                        "output": str(e)
                    }
        
        # Print summary of results
        print("\nTest Script Execution Summary:")
        for script_type, result in results.items():
            status = "Success" if result["success"] else "Failed"
            print(f"{script_type}: {status}")
        
        return results

    def load_analysis_files(self) -> Dict[str, Any]:
        """Load and parse all analysis files."""
        analyses = {}
        for agent_type, file_path in self.analysis_files.items():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    try:
                        # First try to parse the entire content as JSON
                        analyses[agent_type] = json.loads(content)
                    except json.JSONDecodeError:
                        # If that fails, try to find JSON content within the text
                        try:
                            # Look for JSON-like content between curly braces
                            json_match = re.search(r'\{.*\}', content, re.DOTALL)
                            if json_match:
                                json_str = json_match.group(0)
                                analyses[agent_type] = json.loads(json_str)
                            else:
                                print(f"Warning: No JSON content found in {agent_type} analysis")
                                analyses[agent_type] = {"raw_content": content}
                        except Exception as e:
                            print(f"Warning: Could not parse JSON from {agent_type} analysis: {str(e)}")
                            analyses[agent_type] = {"raw_content": content}
            except Exception as e:
                print(f"Error loading {agent_type} analysis: {str(e)}")
                analyses[agent_type] = {"error": str(e)}
        
        # Print loaded analyses for debugging
        print("\nLoaded analyses:")
        for agent_type, analysis in analyses.items():
            print(f"\n{agent_type.upper()} Analysis:")
            print(json.dumps(analysis, indent=2))
        
        return analyses

    def safe_get(self, obj: Any, key: str, default: Any = None) -> Any:
        """Safely get a value from an object that might be a string or dict."""
        if isinstance(obj, dict):
            return obj.get(key, default)
        return default

    def extract_milestones(self, analyses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and organize milestones from all analyses."""
        milestones = []
        
        # Integration milestones
        if "integration" in analyses:
            integration = analyses["integration"]
            if isinstance(integration, dict):
                if "integrations_analyse" in integration:
                    # Language integration
                    lang = self.safe_get(integration["integrations_analyse"], "sprachliche_integration", {})
                    if self.safe_get(lang, "bedarf"):
                        milestones.append({
                            "title": "Sprache & Aufenthalt klären",
                            "parallel": False,
                            "to_dos": [
                                "BAMF-Integrationskurs beantragen",
                                "Beratung bei Migrationsstelle vereinbaren"
                            ],
                            "optional": ["Online-Deutschkurs vorbereitend nutzen"]
                        })
                    
                    # Job center connection
                    jobcenter = self.safe_get(integration["integrations_analyse"], "jobcenter_anbindung", {})
                    if self.safe_get(jobcenter, "status"):
                        milestones.append({
                            "title": "Jobcenter & Finanzierung",
                            "parallel": True,
                            "to_dos": self.safe_get(jobcenter, "empfehlungen", [])
                        })
                    
                    # Financial support
                    financial = self.safe_get(integration["integrations_analyse"], "finanzielle_unterstützung", {})
                    if self.safe_get(financial, "bedarf"):
                        milestones.append({
                            "title": "Finanzielle Unterstützung",
                            "parallel": True,
                            "to_dos": self.safe_get(financial, "möglichkeiten", [])
                        })

        # Social milestones
        if "social" in analyses:
            social = analyses["social"]
            if isinstance(social, dict):
                if "soziale_analyse" in social:
                    # Single parent support
                    if "alleinerziehend" in social["soziale_analyse"]:
                        situation = self.safe_get(social["soziale_analyse"], "alleinerziehend", {})
                        if self.safe_get(situation, "situation"):
                            milestones.append({
                                "title": "Kinderbetreuung & Wohnen sichern",
                                "parallel": True,
                                "to_dos": [
                                    "Kitaplatz beantragen",
                                    "Wohngeldantrag vorbereiten"
                                ] + self.safe_get(situation, "empfehlungen", [])
                            })
                    
                    # Drug addiction
                    if "drogenabhängigkeit" in social["soziale_analyse"]:
                        situation = self.safe_get(social["soziale_analyse"], "drogenabhängigkeit", {})
                        if self.safe_get(situation, "situation"):
                            milestones.append({
                                "title": "Gesundheit & Suchtberatung",
                                "parallel": True,
                                "to_dos": self.safe_get(situation, "empfehlungen", [])
                            })
                    
                    # Housing situation
                    if "wohnverhältnisse" in social["soziale_analyse"]:
                        situation = self.safe_get(social["soziale_analyse"], "wohnverhältnisse", {})
                        if self.safe_get(situation, "situation"):
                            milestones.append({
                                "title": "Wohnsituation verbessern",
                                "parallel": True,
                                "to_dos": self.safe_get(situation, "empfehlungen", [])
                            })

        # Employment milestones
        if "employment" in analyses:
            emp = analyses["employment"]
            if isinstance(emp, dict):
                if "analysis" in emp:
                    # Employment opportunities
                    for opp in self.safe_get(emp["analysis"], "employment_opportunities", []):
                        if isinstance(opp, dict):
                            milestones.append({
                                "title": "Beruflicher Einstieg",
                                "parallel": False,
                                "to_dos": [
                                    "AVGS-Coaching starten",
                                    "Lebenslauf erstellen mit Coach"
                                ] + self.safe_get(opp, "tasks", [])
                            })
                    
                    # Skill gaps
                    for gap in self.safe_get(emp["analysis"], "skill_gaps", []):
                        if isinstance(gap, dict):
                            milestones.append({
                                "title": f"Qualifizierung: {self.safe_get(gap, 'skill', 'Skill Gap')}",
                                "parallel": True,
                                "to_dos": self.safe_get(gap, "improvement_tasks", [])
                            })
                    
                    # Recommendations
                    recommendations = self.safe_get(emp["analysis"], "recommendations", [])
                    if recommendations:
                        milestones.append({
                            "title": "Zusätzliche Empfehlungen",
                            "parallel": True,
                            "to_dos": recommendations
                        })

        return milestones

    def get_strategy_from_assistant(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Get strategy from the strategy assistant."""
        try:
            print("\nConsulting strategy assistant...")
            # Prepare input for the assistant
            input_data = {
                "content": json.dumps(analyses)
            }
            
            # Get response from assistant
            response = self.strategy_assistant.invoke(input_data)
            
            # Extract the output
            if hasattr(response, 'return_values'):
                output = response.return_values.get('output', '')
            else:
                output = str(response)
            
            # Try to parse the output as JSON
            try:
                strategy = json.loads(output)
            except json.JSONDecodeError:
                print("Warning: Could not parse assistant output as JSON")
                strategy = {"raw_output": output}
            
            return strategy
            
        except Exception as e:
            print(f"Error getting strategy from assistant: {str(e)}")
            return {"error": str(e)}

    def create_strategy(self) -> Dict[str, Any]:
        """Create a comprehensive strategy from all analyses."""
        # Run test scripts first
        self.run_test_scripts()
        
        # Load all analyses
        analyses = self.load_analysis_files()
        
        # Get strategy from assistant
        strategy = self.get_strategy_from_assistant(analyses)
        
        # Add metadata
        strategy.update({
            "strategy_version": "v1",
            "created_at": datetime.now().isoformat()
        })
        
        return strategy

    def save_strategy(self, strategy: Dict[str, Any], output_file: str = "strategy/strategy.json"):
        """Save the strategy to a JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(strategy, f, indent=2)
            print(f"Strategy saved to: {output_file}")
        except Exception as e:
            print(f"Error saving strategy: {str(e)}")

def main():
    # Initialize composer
    composer = StrategyComposer()
    
    # Create strategy
    print("Creating strategy from agent analyses...")
    strategy = composer.create_strategy()
    
    # Save strategy
    composer.save_strategy(strategy)
    
    print("Strategy creation completed!")

if __name__ == "__main__":
    main() 