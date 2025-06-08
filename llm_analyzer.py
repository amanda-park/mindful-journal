"""
LLM Analyzer for emotional content analysis and cognitive distortion identification
"""

import json
import os
import ollama

class LLMAnalyzer:
    def __init__(self, model_name=None):
        """Initialize the LLM analyzer with Ollama"""
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "gemma3")
        self.client = None
        
        if ollama is None:
            raise ImportError("Ollama package not available. Please install with: pip install ollama")
        
        # Test connection
        try:
            self.client = ollama.Client()
            # Test if model is available
            models = self.client.list()
            available_models = [model.model for model in ollama.list()["models"]] 
            
            if self.model_name not in available_models:
                # Try common model names
                for common_model in ['llama3', 'deepseek', 'gemma3', 'llama2:7b']:
                    if common_model in available_models:
                        self.model_name = common_model
                        break
                else:
                    if available_models:
                        self.model_name = available_models[0]
                    else:
                        raise Exception("No models available in Ollama")
                        
        except Exception as e:
            raise Exception(f"Failed to connect to Ollama: {str(e)}. Please ensure Ollama is running and has models installed.")

    def analyze_entry(self, journal_entry):
        """Analyze journal entry for emotional content and cognitive distortions"""
        
        system_prompt = """You are a compassionate AI assistant trained in cognitive behavioral therapy principles. Your role is to help users identify emotional patterns and cognitive distortions in their journal entries, then provide supportive guidance.

When analyzing a journal entry, provide:
1. **Emotional Summary**: Key emotions and feelings expressed
2. **Cognitive Patterns**: Any cognitive distortions you notice (like all-or-nothing thinking, catastrophizing, mind reading, etc.)
3. **Reframing Suggestions**: Gentle, realistic alternative perspectives
4. **Supportive Questions**: Questions that encourage self-reflection

Be warm, non-judgmental, and focus on growth rather than criticism. Use a supportive tone throughout."""

        user_prompt = f"""Please analyze this journal entry:

"{journal_entry}"

Provide a thoughtful analysis following the format requested. Focus on being helpful and supportive rather than clinical or detached."""

        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            raise Exception(f"Error analyzing entry with Ollama: {str(e)}")

    def continue_conversation(self, conversation_history, user_question):
        """Continue the therapeutic conversation based on history and new question"""
        
        system_prompt = """You are continuing a supportive conversation about someone's journal entry. You've already provided an initial analysis. Now the user has a follow-up question or wants to explore something deeper.

Maintain the same compassionate, growth-oriented approach. Build on what you've already discussed while addressing their new question directly. Provide practical insights and continue to encourage self-reflection."""

        # Build context from conversation history
        context = "Previous conversation:\n"
        for message in conversation_history:
            if message['type'] == 'user_entry':
                context += f"User's journal entry: {message['content']}\n\n"
            elif message['type'] == 'analysis':
                context += f"Your previous analysis: {message['content']}\n\n"
            elif message['type'] == 'user_question':
                context += f"User asked: {message['content']}\n"
            elif message['type'] == 'ai_response':
                context += f"You responded: {message['content']}\n\n"

        user_prompt = f"""{context}

The user now asks or shares: "{user_question}"

Please respond thoughtfully, building on your previous analysis while directly addressing their new question or concern."""

        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            raise Exception(f"Error continuing conversation with Ollama: {str(e)}")

    def get_available_models(self):
        """Get list of available models in Ollama"""
        try:
            return [model.model for model in ollama.list()["models"]] 
        except Exception:
            return []
