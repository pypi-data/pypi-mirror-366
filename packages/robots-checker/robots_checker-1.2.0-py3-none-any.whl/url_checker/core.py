from typing import Dict, Union, List
from urllib.parse import urlparse
from functools import lru_cache
from protego import Protego
import pandas as pd
import importlib.resources
from datasets import load_dataset

_DEFAULT_REMOVE_USER_AGENTS = [
    "AI2Bot",  # AI2
    "Applebot-Extended",  # Apple
    "Bytespider",  # Bytedance
    "CCBot",  # Common Crawl
    "CCBot/2.0",  # Common Crawl
    "CCBot/1.0",  # Common Crawl
    "ClaudeBot",  # Anthropic
    "cohere-training-data-crawler",  # Cohere
    "Diffbot",  # Diffbot
    "FacebookBot",  # Meta
    "Meta-ExternalAgent",  # Meta
    "Google-Extended",  # Google
    "GPTBot",  # OpenAI
    "PanguBot",  # Huawei
    "*",
]

def load_robots() -> Dict[str, Union[str, bytes]]:
    # Load the dataset from Hugging Face
    ds = load_dataset("swiss-ai/fineweb-robots-txt-files-compressed", split="train")
    # Convert to pandas DataFrame
    df = ds.to_pandas()
    return {row["domain"]: row["content"] for _, row in df.iterrows()}

class RobotsTxtComplianceChecker:
    def __init__(self):
        self.robots_dict = load_robots()

    @lru_cache(maxsize=8192)
    def _get_parser(self, domain: str):
        robots_txt = self.robots_dict.get(domain)
        if not robots_txt:
            return None
        try:
            if isinstance(robots_txt, bytes):
                robots_txt = robots_txt.decode("utf-8", errors="replace")
            return Protego.parse(robots_txt)
        except Exception:
            return None

    def is_compliant(self, url: str, user_agents: List[str] = _DEFAULT_REMOVE_USER_AGENTS) -> str:
        """Check if the given URL is compliant with robots.txt for the given user agents."""
        domain = urlparse(url).netloc
        parser = self._get_parser(domain)
        if not parser:
            return "Compliant"
        for agent in user_agents:
            try:
                if not parser.can_fetch(url, agent):
                    return "NonCompliant"
            except Exception:
                continue
        return "Compliant" 


