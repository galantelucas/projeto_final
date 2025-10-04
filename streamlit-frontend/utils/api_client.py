import requests
import os
import streamlit as st

class APIClient:
    def __init__(self):
        # Tenta diferentes URLs possíveis
        self.possible_urls = [
            "http://fastapi-backend:8000",  # Docker network
            "http://localhost:8000",        # Localhost
            "http://127.0.0.1:8000"         # IP local
        ]
        self.base_url = self._find_working_url()
    
    def _find_working_url(self):
        """Encontra a URL que funciona"""
        for url in self.possible_urls:
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    st.sidebar.success(f"✅ API encontrada: {url}")
                    return url
            except:
                continue
        
        st.sidebar.error("❌ Nenhuma URL da API funcionou")
        return self.possible_urls[0]  # Fallback
    
    def validate_file(self, file_key: str):
        """Chama API de validação"""
        try:
            st.write(f"🔗 Conectando com API: {self.base_url}")
            response = requests.post(
                f"{self.base_url}/validate",
                json={"file_key": file_key},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"❌ API retornou erro: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            st.error("🔌 Erro de conexão - API não responde")
            return None
        except requests.exceptions.Timeout:
            st.error("⏰ Timeout - API demorou muito para responder")
            return None
        except Exception as e:
            st.error(f"🚨 Erro inesperado: {str(e)}")
            return None
    
    def health_check(self):
        """Verifica saúde da API"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

api_client = APIClient()