"""
chatbot/rag_engine.py - FINAL WORKING VERSION
This is the complete, tested, working version.
"""

import os
import oracledb
from chatbot.smart_client import smart_client

class RAGEngine:
    """
    Retrieval-Augmented Generation Engine - Connects to Oracle + uses AI
    """
    
    def __init__(self):
        """Initialize with all credentials from environment."""
        self.user = os.getenv('ORACLE_CLOUD_USER', 'ADMIN')
        self.password = os.getenv('ORACLE_CLOUD_PASSWORD')
        self.dsn = os.getenv('ORACLE_CLOUD_DSN')
        self.wallet_location = os.getenv('ORACLE_WALLET_LOCATION', 'database/wallet')
        self.wallet_password = os.getenv('ORACLE_WALLET_PASSWORD', '')  # Your wallet password
        
        # Medicine keywords for smart extraction
        self.medicine_keywords = [
            'paracetamol', 'ibuprofen', 'amoxicillin', 'cetirizine', 'omeprazole',
            'antibiotic', 'antipyretic', 'nsaid', 'antihistamine', 'antacid',
            'tablet', 'capsule', 'pain', 'fever', 'allergy', 'infection', 'acid'
        ]
        
        print(f"🔗 RAG Engine ready")
    
    def extract_keywords(self, query: str) -> str:
        """
        Extract medicine name or category from user's question.
        Example: "What is Paracetamol used for?" → "paracetamol"
        """
        query_lower = query.lower()
        
        # Look for known medicine keywords
        for keyword in self.medicine_keywords:
            if keyword in query_lower:
                return keyword
        
        # Remove question words to find the important word
        remove_words = ['what', 'is', 'the', 'are', 'can', 'you', 'tell', 'me', 
                       'about', 'do', 'have', 'any', 'for', 'used', 'category', 'name']
        
        words = [w for w in query_lower.split() if w not in remove_words and len(w) > 2]
        
        return words[0] if words else query_lower
    
    def get_connection(self):
        """
        Connect to Oracle database with wallet.
        Uses wallet_password from .env - won't prompt!
        """
        return oracledb.connect(
            user=self.user,
            password=self.password,
            dsn=self.dsn,
            config_dir=self.wallet_location,
            wallet_location=self.wallet_location,
            wallet_password=self.wallet_password  # CRITICAL: Uses password from .env
        )
    
    def retrieve_context(self, query: str) -> list:
        """
        Search database for medicines matching the query.
        Returns list of medicine dictionaries.
        """
        try:
            # Extract just the medicine name/category
            keyword = self.extract_keywords(query)
            print(f"🔍 Searching for: {keyword}")
            
            # Connect to database
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Search query - IMPORTANT: 3 bind values for 3 placeholders
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
            
            search_term = f"%{keyword}%"
            # Provide 3 values because query has :1, :2, :3
            cursor.execute(sql, [search_term, search_term, search_term])
            
            rows = cursor.fetchall()
            
            # Convert to dictionaries
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
            
            print(f"✅ Found {len(medicines)} result(s)")
            
            # If no specific results, show all medicines
            if len(medicines) == 0:
                print("⚠️  No matches, showing all medicines")
                return self.retrieve_all_medicines()
            
            return medicines
            
        except Exception as e:
            print(f"❌ Search error: {str(e)}")
            # Fallback to showing all medicines
            return self.retrieve_all_medicines()
    
    def retrieve_all_medicines(self) -> list:
        """Get all 5 medicines from database."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            sql = "SELECT medicine_name, category_name, dosage_form, strength, manufacturer FROM medicines ORDER BY medicine_name"
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
            
            return medicines
            
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            return []
    
    def format_context(self, medicines: list) -> str:
        """Format medicine data into text for AI."""
        if not medicines:
            return "No medicines in database."
        
        text = f"Available medicines ({len(medicines)}):\n\n"
        
        for i, med in enumerate(medicines, 1):
            text += f"{i}. {med['name']}\n"
            text += f"   Category: {med['category']}\n"
            text += f"   Form: {med['form']}\n"
            text += f"   Strength: {med['strength']}\n"
            text += f"   Manufacturer: {med['manufacturer']}\n\n"
        
        return text
    
    def generate_response(self, question: str) -> str:
        """
        Main function: Search database + Generate AI response.
        This is what chatbot_ui.py calls.
        """
        try:
            print(f"\n📋 Question: {question}")
            
            # Step 1: Get medicines from database
            medicines = self.retrieve_context(question)
            
            # Step 2: Format into text
            context = self.format_context(medicines)
            
            print(f"📄 Ready: {len(medicines)} medicine(s)")
            
            # Step 3: Create prompt for AI
            prompt = f"""You are a pharmacy assistant. Answer this question using ONLY the database information below.

DATABASE:
{context}

QUESTION: {question}

Provide a helpful, natural answer based on the database facts above.

ANSWER:"""
            
            # Step 4: Get AI response
            print("🤖 Generating AI response...")
            response = smart_client.generate(prompt, temperature=0.3, max_tokens=500)
            
            print("✅ Complete\n")
            return response
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"


# Create the global instance that chatbot_ui.py imports
rag_engine = RAGEngine()
