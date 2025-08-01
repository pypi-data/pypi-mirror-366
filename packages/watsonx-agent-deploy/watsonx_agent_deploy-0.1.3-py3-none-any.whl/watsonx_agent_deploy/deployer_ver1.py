import os
import logging
import subprocess
import sys
from pathlib import Path
import tomlkit
from dotenv import load_dotenv

class WatsonXDeployer:
    def __init__(self, env_file='.env', config_dir='.', verbose=False):
        self.env_file = env_file
        self.config_dir = Path(config_dir).resolve()
        self.setup_logging(verbose)
        self.load_environment()
    
    def setup_logging(self, verbose):
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler('watsonx-deploy.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_environment(self):
        """Load environment variables from .env file"""
        if not Path(self.env_file).exists():
            raise FileNotFoundError(f"Environment file {self.env_file} not found")
        
        load_dotenv(self.env_file)
        self.apikey = os.getenv("WATSONX_APIKEY")
        self.url = os.getenv("WATSONX_URL") 
        self.space_id = os.getenv("SPACE_ID")
        
        if not all([self.apikey, self.url, self.space_id]):
            raise ValueError("Missing required environment variables: WATSONX_APIKEY, WATSONX_URL, SPACE_ID")
    
    def update_agent_config(self, config_path):
        """Update agent config.toml with deployment settings"""
        doc = tomlkit.parse(config_path.read_text(encoding="utf-8"))
        dep = doc.setdefault("deployment", tomlkit.table())
        dep["watsonx_apikey"] = self.apikey
        dep["watsonx_url"] = self.url
        dep["space_id"] = self.space_id
        
        online = dep.setdefault("online", tomlkit.table()).setdefault("parameters", tomlkit.table())
        online["url"] = self.url
        
        config_path.write_text(tomlkit.dumps(doc), encoding="utf-8")
        self.logger.info(f"Updated config for {config_path.parent.name}")
    
    def run_command(self, cmd, folder):
        """Execute shell command in specified folder"""
        self.logger.info(f"[{folder.name}] → {cmd}")
        
        result = subprocess.run(
            cmd, 
            cwd=folder, 
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            self.logger.info(result.stdout)
        if result.stderr:
            self.logger.warning(result.stderr)
        
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {cmd}")
    
    def deploy_agent(self, agent_dir):
        """Deploy a single agent"""
        config_path = agent_dir / "config.toml"
        if not config_path.exists():
            self.logger.warning(f"No config.toml found in {agent_dir.name}, skipping")
            return
        
        self.update_agent_config(config_path)
        
        commands = [
            "python3 -m venv .venv",
            ".venv/bin/python -m pip install --upgrade pip poetry",
            "poetry env use python3",
            "rm -rf dist",
            f"watsonx-ai service new {agent_dir.name}"
        ]
        
        for cmd in commands:
            self.run_command(cmd, agent_dir)
    
    def deploy_all(self):
        """Deploy all agent directories"""
        # Setup root environment
        self.run_command("python3 -m venv .venv", self.config_dir)
        self.run_command(".venv/bin/pip install python-dotenv ibm-watsonx-ai-cli tomlkit", self.config_dir)
        
        agent_dirs = [d for d in self.config_dir.iterdir() 
                     if d.is_dir() and d.name.endswith('agent')]
        
        if not agent_dirs:
            self.logger.warning("No agent directories found (folders ending with 'agent')")
            return
        
        self.logger.info(f"Found {len(agent_dirs)} agent directories")
        
        for agent_dir in sorted(agent_dirs):
            try:
                self.deploy_agent(agent_dir)
                self.logger.info(f"✅ Successfully deployed {agent_dir.name}")
            except Exception as e:
                self.logger.error(f"❌ Failed to deploy {agent_dir.name}: {e}")
                raise