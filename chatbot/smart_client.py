"""
chatbot/smart_client.py - Using CORRECT model names from your API keys
"""

from google import genai
from google.genai import types
import os
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

class SmartClient:
    """
    Intelligent API client with automatic failover using models that actually exist!
    """
    
    def __init__(self):
        print("🚀 Initializing Enhanced SmartClient with WORKING models...")
        
        # Load all available API keys
        self.api_keys = []
        key_index = 1
        
        while True:
            key = os.getenv(f"GOOGLE_API_KEY_{key_index}")
            if key:
                self.api_keys.append(key)
                key_index += 1
            else:
                break
        
        if not self.api_keys:
            raise ValueError("No Google AI API keys found in environment variables.")
        
        print(f"✅ Loaded {len(self.api_keys)} API key(s) from environment")
        
        # Use ACTUAL models that exist with your API keys!
        self.models = [
            "models/gemini-2.0-flash",      # Fast and reliable
            "models/gemini-2.5-flash",      # Newer version
            "models/gemini-2.0-flash-001",  # Stable fallback
        ]
        
        print(f"📋 Configured {len(self.models)} model(s) for rotation")
        
        # Initialize tracking
        self.combination_status = {}
        for key_idx in range(len(self.api_keys)):
            for model in self.models:
                combo_key = f"key_{key_idx+1}_{model}"
                self.combination_status[combo_key] = {
                    "status": "untested",
                    "last_success": None,
                    "last_failure": None,
                    "success_count": 0,
                    "failure_count": 0,
                    "consecutive_failures": 0
                }
        
        self.current_key_index = 0
        self.current_model_index = 0
        
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.failover_count = 0
        
        # Create client with first key
        self.client = genai.Client(api_key=self.api_keys[0])
        
        print("✅ SmartClient ready with WORKING models!")
        print(f"📊 Total available combinations: {len(self.api_keys) * len(self.models)}")
    
    def _configure_key(self, api_key: str):
        """Switch to a different API key by creating a new client."""
        self.client = genai.Client(api_key=api_key)
    
    def _get_combo_key(self, key_idx: int, model: str) -> str:
        return f"key_{key_idx+1}_{model}"
    
    def _update_combo_status(self, key_idx: int, model: str, 
                            success: bool, error_type: str = None):
        combo_key = self._get_combo_key(key_idx, model)
        status_data = self.combination_status[combo_key]
        
        if success:
            status_data["status"] = "working"
            status_data["last_success"] = datetime.now()
            status_data["success_count"] += 1
            status_data["consecutive_failures"] = 0
        else:
            status_data["last_failure"] = datetime.now()
            status_data["failure_count"] += 1
            status_data["consecutive_failures"] += 1
            
            if error_type == "quota":
                status_data["status"] = "quota_exceeded"
            elif error_type == "auth":
                status_data["status"] = "auth_error"
            else:
                status_data["status"] = "error"
    
    def _should_skip_combo(self, key_idx: int, model: str) -> bool:
        combo_key = self._get_combo_key(key_idx, model)
        status_data = self.combination_status[combo_key]
        
        if status_data["status"] == "untested":
            return False
        if status_data["status"] == "working":
            return False
        if status_data["status"] == "quota_exceeded":
            if status_data["last_failure"]:
                time_since_failure = datetime.now() - status_data["last_failure"]
                if time_since_failure > timedelta(minutes=5):
                    return False
                else:
                    return True
        if status_data["status"] == "auth_error":
            return True
        if status_data["consecutive_failures"] >= 3:
            return True
        
        return False
    
    def _find_next_combination(self) -> Optional[Tuple[int, int]]:
        attempts = 0
        max_attempts = len(self.api_keys) * len(self.models)
        
        while attempts < max_attempts:
            self.current_model_index += 1
            
            if self.current_model_index >= len(self.models):
                self.current_model_index = 0
                self.current_key_index += 1
                
                if self.current_key_index >= len(self.api_keys):
                    self.current_key_index = 0
            
            if not self._should_skip_combo(
                self.current_key_index, 
                self.models[self.current_model_index]
            ):
                self._configure_key(self.api_keys[self.current_key_index])
                return (self.current_key_index, self.current_model_index)
            
            attempts += 1
        
        return None
    
    def get_current_status(self) -> Dict:
        current_key = self.current_key_index + 1
        current_model = self.models[self.current_model_index]
        
        working_combos = sum(
            1 for status in self.combination_status.values()
            if status["status"] == "working"
        )
        
        quota_exceeded_combos = sum(
            1 for status in self.combination_status.values()
            if status["status"] == "quota_exceeded"
        )
        
        return {
            "current_key": current_key,
            "current_model": current_model,
            "total_keys": len(self.api_keys),
            "total_models": len(self.models),
            "total_combinations": len(self.api_keys) * len(self.models),
            "working_combinations": working_combos,
            "quota_exceeded_combinations": quota_exceeded_combos,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "failover_count": self.failover_count,
            "success_rate": (
                (self.successful_requests / self.total_requests * 100)
                if self.total_requests > 0 else 0
            )
        }
    
    def generate(self, prompt: str, temperature: float = 0.7, 
                 max_tokens: int = 1000) -> str:
        self.total_requests += 1
        max_failovers = len(self.api_keys) * len(self.models)
        attempt = 0
        
        while attempt < max_failovers:
            attempt += 1
            
            key_num = self.current_key_index + 1
            model_name = self.models[self.current_model_index]
            
            try:
                print(f"🔄 Attempt {attempt}: Key #{key_num} with {model_name}")
                
                # Use NEW google-genai syntax with CORRECT model names
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    )
                )
                
                self._update_combo_status(
                    self.current_key_index,
                    model_name,
                    success=True
                )
                
                self.successful_requests += 1
                print(f"✅ Success with Key #{key_num}, {model_name}")
                
                return response.text
            
            except Exception as e:
                error_msg = str(e).lower()
                
                if any(phrase in error_msg for phrase in [
                    "quota", "rate limit", "429", "resource exhausted",
                    "too many requests"
                ]):
                    error_type = "quota"
                    print(f"⚠️ Quota exceeded for Key #{key_num}, {model_name}")
                elif any(phrase in error_msg for phrase in [
                    "api key", "authentication", "unauthorized", "invalid key"
                ]):
                    error_type = "auth"
                    print(f"❌ Authentication error for Key #{key_num}")
                elif "404" in error_msg or "not found" in error_msg:
                    error_type = "model_not_found"
                    print(f"⚠️ Model not found: {model_name}")
                else:
                    error_type = "other"
                    print(f"⚠️ Error: {str(e)[:100]}")
                
                self._update_combo_status(
                    self.current_key_index,
                    model_name,
                    success=False,
                    error_type=error_type
                )
                
                if error_type == "auth":
                    raise
                
                next_combo = self._find_next_combination()
                
                if next_combo is None:
                    self.failed_requests += 1
                    raise Exception(
                        f"All {max_failovers} API key-model combinations exhausted.\n"
                        f"Try again later or add more API keys."
                    )
                
                self.failover_count += 1
        
        self.failed_requests += 1
        raise Exception("Unexpected error in SmartClient failover logic")
    
    def reset(self):
        for combo_key in self.combination_status:
            self.combination_status[combo_key] = {
                "status": "untested",
                "last_success": None,
                "last_failure": None,
                "success_count": 0,
                "failure_count": 0,
                "consecutive_failures": 0
            }
        
        self.current_key_index = 0
        self.current_model_index = 0
        self._configure_key(self.api_keys[0])
        
        print("🔄 SmartClient reset to initial state")


smart_client = SmartClient()
