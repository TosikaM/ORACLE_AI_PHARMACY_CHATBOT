"""
chatbot/rag_engine.py - FIXED version with correct Oracle bind values
"""

import os
import oracledb
from chatbot.smart_client import smart_client

class RAGEngine:
    """
    Retrieval-Augmented Generation Engine - WORKING VERSION
    """
    
    def __init__(self):
        """Initialize with database credentials."""
        self.user = os.getenv('ORACLE_CLOUD_USER', 'ADMIN')
        self.password = os.getenv('ORACLE_CLOUD_PASSWORD')
        self.dsn = os.getenv('ORACLE_CLOUD_DSN')
        self.wallet_location = os.getenv('ORACLE_WALLET_LOCATION', 'database/wallet')
        
        # Common medicine-related keywords
        self.medicine_keywords = [
            'paracetamol', 'ibuprofen', 'amoxicillin', 'cetirizine', 'omeprazole',
            'antibiotic', 'antipyretic', 'nsaid', 'antihistamine', 'antacid',
            'tablet', 'capsule', 'pain', 'fever', 'allergy', 'infection', 'acid'
        ]
        
        print(f"🔗 RAG Engine initialized")
    
    def extract_keywords(self, query: str) -> str:
        """Extract relevant medicine keywords from the question."""
        query_lower = query.lower()
        
        # Check for known medicine names
        for keyword in self.medicine_keywords:
            if keyword in query_lower:
                print(f"🔍 Extracted keyword: '{keyword}'")
                return keyword
        
        # Remove common question words
        words_to_remove = [
            'what', 'is', 'the', 'are', 'can', 'you', 'tell', 'me', 'about',
            'do', 'have', 'any', 'for', 'used', 'category', 'name', 'medicine'
        ]
        
        words = query_lower.split()
        keywords = [w for w in words if w not in words_to_remove and len(w) > 2]
        
        if keywords:
            result = keywords[0]
            print(f"🔍 Extracted keyword: '{result}'")
            return result
        
        print(f"🔍 Using full query")
        return query_lower
    
    def get_connection(self):
        """Get a direct database connection."""
        return oracledb.connect(
            user=self.user,
            password=self.password,
            dsn=self.dsn,
            config_dir=self.wallet_location,
            wallet_location=self.wallet_location
        )
    
    def retrieve_context(self, query: str, max_results: int = 5) -> list:
        """
        Search the medicines database.
        """
        try:
            keywords = self.extract_keywords(query)
            print(f"🔍 Searching database for: '{keywords}'")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # FIXED: Oracle query with correct number of bind values
            # Each :1, :2, :3 gets its own value
            sql = """
                SELECT 
                    medicine_name,
                    category_name,
                    dosage_form,
                    strength,
                    manufacturer
                FROM medicines
                WHERE 
                    LOWER(medicine_name) LIKE :1
                    OR LOWER(category_name) LIKE :2
                    OR LOWER(dosage_form) LIKE :3
                ORDER BY medicine_name
                FETCH FIRST 5 ROWS ONLY
            """
            
            # Provide THREE values for THREE bind variables
            search_term = f"%{keywords}%"
            cursor.execute(sql, [search_term, search_term, search_term])
            
            rows = cursor.fetchall()
            
            medicines = []
            for row in rows:
                medicines.append({
                    'name': row[0],
                    'category': row[1],
                    'form': row[2],
                    'strength': row[3],
                    'manufacturer': row[4]
                })
            
            cursor.close()
            conn.close()
            
            print(f"✅ Found {len(medicines)} medicine(s)")
            
            # If nothing found, get all medicines
            if len(medicines) == 0:
                print(f"⚠️  No specific results, showing all medicines")
                return self.retrieve_all_medicines()
            
            return medicines
            
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            import traceback
            traceback.print_exc()
            return self.retrieve_all_medicines()
    
    def retrieve_all_medicines(self) -> list:
        """Get all medicines from database."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            sql = """
                SELECT 
                    medicine_name,
                    category_name,
                    dosage_form,
                    strength,
                    manufacturer
                FROM medicines
                ORDER BY medicine_name
            """
            
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            medicines = []
            for row in rows:
                medicines.append({
                    'name': row[0],
                    'category': row[1],
                    'form': row[2],
                    'strength': row[3],
                    'manufacturer': row[4]
                })
            
            cursor.close()
            conn.close()
            
            print(f"✅ Retrieved all {len(medicines)} medicines")
            return medicines
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return []
    
    def format_context(self, context_items: list) -> str:
        """Format medicines into readable text."""
        if not context_items:
            return "No medicines found."
        
        context_text = f"Found {len(context_items)} medicine(s):\n\n"
        
        for i, med in enumerate(context_items, 1):
            context_text += f"{i}. {med['name']}\n"
            context_text += f"   - Category: {med['category']}\n"
            context_text += f"   - Form: {med['form']}\n"
            context_text += f"   - Strength: {med['strength']}\n"
            context_text += f"   - Manufacturer: {med['manufacturer']}\n\n"
        
        return context_text
    
    def generate_response(self, question: str) -> str:
        """
        Complete RAG flow: retrieve data and generate response.
        """
        try:
            print(f"\n📋 Question: {question}")
            
            context_items = self.retrieve_context(question)
            context_text = self.format_context(context_items)
            
            print(f"📄 Context: {len(context_items)} items")
            
            prompt = f"""You are a helpful pharmacy assistant. Answer based on this database information:

{context_text}

USER QUESTION: {question}

Answer naturally and professionally.

ANSWER:"""
            
            print("🤖 Calling AI...")
            response = smart_client.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            print("✅ Done\n")
            return response
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return f"Error: {str(e)}"


# Create global instance
rag_engine = RAGEngine()
