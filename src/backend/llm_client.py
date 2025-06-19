import requests
from typing import List, Dict, Any
import json

class LLMClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        # Podrazumevano koristimo Mistral model
        self.model = "mistral"
    
    async def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generiše odgovor koristeći Ollama API.
        """
        try:
            # Formatiramo prompt sa system promptom
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            # Ollama API endpoint za generisanje
            url = f"{self.base_url}/api/generate"
            
            # Parametri za zahtev
            data = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False
            }
            
            # Šaljemo zahtev
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            # Parsiramo odgovor
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Greška pri komunikaciji sa Ollama: {str(e)}"
            if "Connection refused" in str(e):
                print("⚠️  Ollama nije dostupna. Koristim mock odgovor.")
                return self._generate_mock_response(prompt, system_prompt)
            raise Exception(error_msg)
        except Exception as e:
            print(f"⚠️  Neočekivana greška sa Ollama: {str(e)}. Koristim mock odgovor.")
            return self._generate_mock_response(prompt, system_prompt)
    
    def _generate_mock_response(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generiše mock odgovor kada Ollama nije dostupna.
        """
        if "zdravlje" in prompt.lower() or "medicina" in prompt.lower():
            return "Ovo je mock odgovor za medicinsko pitanje. U produkciji bi ovde bio pravi AI odgovor."
        elif "programiranje" in prompt.lower() or "kod" in prompt.lower():
            return "Ovo je mock odgovor za programersko pitanje. U produkciji bi ovde bio pravi AI odgovor."
        else:
            return "Ovo je mock odgovor. U produkciji bi ovde bio pravi AI odgovor generisan od strane Ollama modela."

# Kreiramo globalnu instancu
llm_client = LLMClient() 