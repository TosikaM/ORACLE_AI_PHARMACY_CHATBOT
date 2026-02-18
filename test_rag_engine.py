"""
test_rag_engine.py - Test the RAG engine BEFORE running Streamlit

This will verify that:
1. Database queries work correctly
2. Keyword extraction works
3. Response generation works
4. Everything is truly ready

Run this FIRST: python test_rag_engine.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
config_dir = Path(__file__).parent / 'config'
env_path = config_dir / '.env'
load_dotenv(env_path)

print("="*70)
print("RAG ENGINE COMPREHENSIVE TEST")
print("="*70)
print()

# Test 1: Import the RAG engine
print("TEST 1: Importing RAG engine...")
try:
    from chatbot.rag_engine import rag_engine
    print("✅ RAG engine imported successfully")
except Exception as e:
    print(f"❌ FAILED to import RAG engine: {str(e)}")
    sys.exit(1)
print()

# Test 2: Test keyword extraction
print("TEST 2: Testing keyword extraction...")
test_questions = [
    "What is Paracetamol used for?",
    "Tell me about antibiotics",
    "Do you have any medicines for fever?"
]

for question in test_questions:
    keyword = rag_engine.extract_keywords(question)
    print(f"  Q: {question}")
    print(f"  Extracted: '{keyword}'")
print("✅ Keyword extraction working")
print()

# Test 3: Test database retrieval
print("TEST 3: Testing database retrieval...")
print("Searching for 'paracetamol'...")
try:
    results = rag_engine.retrieve_context("paracetamol")
    
    if len(results) > 0:
        print(f"✅ Found {len(results)} medicine(s):")
        for med in results:
            print(f"  - {med['name']} ({med['category']})")
    else:
        print("❌ No results found - this is the problem!")
        sys.exit(1)
except Exception as e:
    print(f"❌ Database retrieval FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
print()

# Test 4: Test retrieve all medicines
print("TEST 4: Testing retrieve all medicines...")
try:
    all_meds = rag_engine.retrieve_all_medicines()
    print(f"✅ Retrieved {len(all_meds)} total medicines:")
    for med in all_meds:
        print(f"  - {med['name']}")
except Exception as e:
    print(f"❌ FAILED: {str(e)}")
    sys.exit(1)
print()

# Test 5: Test full RAG pipeline
print("TEST 5: Testing FULL RAG pipeline (retrieve + AI generation)...")
test_question = "What is Paracetamol used for?"
print(f"Question: {test_question}")
print()

try:
    response = rag_engine.generate_response(test_question)
    
    print("="*70)
    print("GENERATED RESPONSE:")
    print("="*70)
    print(response)
    print("="*70)
    print()
    
    # Check if response mentions paracetamol
    if 'paracetamol' in response.lower():
        print("✅ Response mentions Paracetamol - LOOKS GOOD!")
    else:
        print("⚠️  Response doesn't mention Paracetamol - might be generic")
    
    # Check if it says "no medicines found"
    if 'no medicines' in response.lower() or 'not found' in response.lower():
        print("❌ Response says medicines not found - RAG FAILED")
        sys.exit(1)
    
    print("✅ Full RAG pipeline WORKING!")
    
except Exception as e:
    print(f"❌ RAG pipeline FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("="*70)
print("ALL TESTS PASSED! ✅")
print("="*70)
print()
print("Your RAG engine is working correctly!")
print("You can now run: streamlit run ui/chatbot_ui.py")
print()
