"""
utils/model_checker.py
────────────────────────────────────────────────────────────────────
Model Checker Utility - Standalone Status Monitor

This utility provides a comprehensive view of your Google AI API keys
and models. Run it anytime to check which keys are working, which have
hit quota limits, and get recommendations on what to do next.

How to use this utility:
  1. Open command prompt in the project folder
  2. Run: python utils/model_checker.py
  3. See detailed status of all your API keys and models
  4. Get recommendations for next steps

This is useful when you want to check your API status without running
the full chatbot, or when you're troubleshooting quota issues.
"""

import sys
import os

# Add parent directory to path so we can import chatbot modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.smart_client import smart_client
from datetime import datetime
import time


def print_header():
    """Print a nice header for the utility."""
    print("\n" + "="*70)
    print(" "*15 + "GOOGLE AI MODEL CHECKER UTILITY")
    print("="*70 + "\n")


def print_section(title):
    """Print a section divider."""
    print("\n" + "-"*70)
    print(f" {title}")
    print("-"*70)


def check_api_connectivity():
    """
    Test if we can connect to Google AI API at all.
    
    This makes a simple test call to verify that at least one of your
    API keys is working and can communicate with Google's servers.
    """
    print_section("API CONNECTIVITY TEST")
    
    try:
        test_prompt = "Say 'API connection successful' and nothing else."
        print("Testing API connection with a simple request...")
        print("Prompt: " + test_prompt)
        
        response = smart_client.generate(test_prompt, max_tokens=20)
        
        print(f"\n✅ API Response: {response}")
        print("✅ Connection to Google AI is working!")
        return True
    
    except Exception as e:
        print(f"\n❌ API Connection Failed!")
        print(f"Error: {str(e)}")
        print("\nPossible reasons:")
        print("- All API keys have hit quota limits")
        print("- API keys are invalid or incorrectly configured")
        print("- No internet connection")
        print("- Google AI service is temporarily down")
        return False


def display_detailed_status():
    """
    Display detailed status of all key-model combinations.
    
    This shows you exactly which combinations are working, which have
    hit quota limits, and which have errors. This is the most useful
    information for managing your API quota.
    """
    print_section("DETAILED KEY-MODEL STATUS")
    
    # Get all combination statuses
    combos = smart_client.combination_status
    
    # Group by key
    for key_idx in range(len(smart_client.api_keys)):
        key_num = key_idx + 1
        print(f"\n🔑 API Key #{key_num}:")
        
        for model in smart_client.models:
            combo_key = smart_client._get_combo_key(key_idx, model)
            status_data = combos[combo_key]
            
            # Format status with color indicators
            status = status_data["status"]
            if status == "working":
                status_icon = "✅"
                status_text = "WORKING"
            elif status == "quota_exceeded":
                status_icon = "⚠️"
                status_text = "QUOTA EXCEEDED"
            elif status == "auth_error":
                status_icon = "❌"
                status_text = "AUTH ERROR"
            elif status == "untested":
                status_icon = "❓"
                status_text = "UNTESTED"
            else:
                status_icon = "⚠️"
                status_text = "ERROR"
            
            print(f"  {status_icon} {model}: {status_text}")
            
            # Show additional details if available
            if status_data["success_count"] > 0:
                print(f"     Successes: {status_data['success_count']}")
            
            if status_data["failure_count"] > 0:
                print(f"     Failures: {status_data['failure_count']}")
            
            if status_data["last_success"]:
                time_ago = datetime.now() - status_data["last_success"]
                print(f"     Last success: {int(time_ago.total_seconds() / 60)} minutes ago")
            
            if status_data["last_failure"]:
                time_ago = datetime.now() - status_data["last_failure"]
                print(f"     Last failure: {int(time_ago.total_seconds() / 60)} minutes ago")


def display_summary_statistics():
    """
    Display overall statistics about API usage.
    
    This gives you a high-level view of how well the SmartClient is
    performing - how many requests succeeded, how many failed, and
    what the overall success rate is.
    """
    print_section("OVERALL STATISTICS")
    
    status = smart_client.get_current_status()
    
    print(f"\n📊 Current Configuration:")
    print(f"  Total API Keys: {status['total_keys']}")
    print(f"  Models per Key: {status['total_models']}")
    print(f"  Total Combinations: {status['total_combinations']}")
    
    print(f"\n📈 Usage Statistics:")
    print(f"  Total Requests: {status['total_requests']}")
    print(f"  Successful: {status['successful_requests']} ✅")
    print(f"  Failed: {status['failed_requests']} ❌")
    
    if status['total_requests'] > 0:
        print(f"  Success Rate: {status['success_rate']:.1f}%")
    
    print(f"  Failovers: {status['failover_count']}")
    
    print(f"\n💡 Current Status:")
    print(f"  Active Key: #{status['current_key']}")
    print(f"  Active Model: {status['current_model']}")
    print(f"  Working Combinations: {status['working_combinations']}/{status['total_combinations']}")
    print(f"  Quota-Exceeded: {status['quota_exceeded_combinations']}/{status['total_combinations']}")


def provide_recommendations():
    """
    Provide actionable recommendations based on current status.
    
    This analyzes the status data and tells you what actions you
    should take - whether you need to wait for quota reset, add more
    keys, or if everything is working fine.
    """
    print_section("RECOMMENDATIONS")
    
    status = smart_client.get_current_status()
    combos = smart_client.combination_status
    
    # Count different statuses
    working = sum(1 for s in combos.values() if s["status"] == "working")
    quota_exceeded = sum(1 for s in combos.values() if s["status"] == "quota_exceeded")
    errors = sum(1 for s in combos.values() if s["status"] not in ["working", "untested", "quota_exceeded"])
    
    total = len(combos)
    
    print("")
    
    # Provide specific recommendations
    if working == 0 and quota_exceeded == total:
        print("🔴 CRITICAL: All API key-model combinations have hit quota limits!")
        print("\nRECOMMENDED ACTIONS:")
        print("1. Wait for quota reset (usually hourly or daily)")
        print("2. Add more API keys from Google AI Studio")
        print("3. Check quota limits at https://makersuite.google.com")
        print("\nYou can continue working in about 1-2 hours when quotas reset.")
    
    elif working == 0 and errors > 0:
        print("🔴 CRITICAL: No working combinations available!")
        print("\nRECOMMENDED ACTIONS:")
        print("1. Check your API keys are valid")
        print("2. Verify internet connection")
        print("3. Check Google AI Studio for service status")
        print("4. Review error messages above for specific issues")
    
    elif working > 0 and working < total * 0.3:
        print(f"🟡 WARNING: Only {working}/{total} combinations working")
        print("\nRECOMMENDED ACTIONS:")
        print("1. Consider adding more API keys for better availability")
        print(f"2. You have {quota_exceeded} quota-exceeded combinations")
        print("3. These will auto-retry after cooldown period")
        print("4. Current working combinations will continue to be used")
    
    elif working >= total * 0.3:
        print(f"🟢 GOOD: {working}/{total} combinations are working")
        print("\nYour SmartClient is operating well!")
        print("Continue using the chatbot normally.")
        
        if quota_exceeded > 0:
            print(f"\nNote: {quota_exceeded} combinations have hit quotas but will")
            print("auto-retry after cooldown periods.")
    
    # Suggest adding keys if total is low
    if status['total_keys'] < 4:
        print(f"\n💡 TIP: You have {status['total_keys']} API keys configured.")
        print("Consider adding more free keys from Google AI Studio for")
        print("better availability during development and testing.")


def main():
    """
    Main function that runs all checks and displays results.
    """
    print_header()
    
    print("Checking your Google AI API configuration...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all checks
    check_api_connectivity()
    display_summary_statistics()
    display_detailed_status()
    provide_recommendations()
    
    # Footer
    print("\n" + "="*70)
    print("\n💡 To update your API keys:")
    print("   Edit config/.env file and restart your application")
    print("\n💡 To reset all status tracking:")
    print("   Run: smart_client.reset() in your Python code")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # This runs when you execute: python utils/model_checker.py
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCheck cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        print("\nPlease check your configuration and try again.")
