from openai import OpenAI
import os
from typing import List, Dict, Any, Union
from types import SimpleNamespace
from azllm.base import UNIClient
from azllm.utils import StructuredOutput
from pydantic import ValidationError
import json
import time 
import random
from dotenv import load_dotenv
load_dotenv()


DEFAULT_CONFIG = {'model': 'claude-3-7-sonnet-20250219',
                  'system_message': 'You are an advanced AI assistant.',
                  'temperature': 1,
                  'max_tokens': 4096,
                  'frequency_penalty': 0,
                  'presence_penalty': 0,
                  'kwargs': {}}

structuredoutput = StructuredOutput()

class AnthropicClient:
    """
    A client for interacting with the Anthropic API (e.g., Claude models).

    This class allows you to send prompts to the Anthropic API and receive generated text in return.
    You can customize parameters such as temperature, system message, and penalties.

    Attributes:
        model (str): The model to be used for text generation (default: 'claude-3-7-sonnet-20250219').
        system_message (str): The system message that provides context for the assistant's behavior.
        temperature (float): Controls the randomness of the generated responses.
        max_tokens (int): The maximum number of tokens to generate in a response.
        frequency_penalty (float): Controls the frequency of repeated tokens in the generated text.
        presence_penalty (float): Controls the model's tendency to introduce new topics.
        kwargs (dict): Additional settings for the model.
    """
    def __init__(self, config: Dict[str, Any]= None):
        """
        Initializes the AnthropicClient with the provided configuration or default settings.

        Args:
            config (dict, optional): A dictionary containing user-defined settings for the client.
        """
        
        config = config or {}
        self.api_key: str = None
        self.client = None

        self.model = config.get('model', DEFAULT_CONFIG['model']) 
        self.parameters = config.get('parameters', {}) 
        self.system_message = self.parameters.get('system_message', DEFAULT_CONFIG['system_message']) 
        self.temperature = self.parameters.get('temperature', DEFAULT_CONFIG['temperature']) 
        self.max_tokens = self.parameters.get('max_tokens', DEFAULT_CONFIG['max_tokens']) 
        self.frequency_penalty = self.parameters.get('frequency_penalty', DEFAULT_CONFIG['frequency_penalty']) 
        self.presence_penalty = self.parameters.get('presence_penalty', DEFAULT_CONFIG['presence_penalty']) 
        self.kwargs = self.parameters.get('kwargs', DEFAULT_CONFIG['kwargs'])
    
    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """
        Returns the default configuration for the AnthropicClient.

        Returns:
            dict: The default configuration settings.
        """
        return DEFAULT_CONFIG
        
    def get_api_key(self) -> str:
        """
        Loads the API key for Anthropic from the environment file.

        Returns:
            str: The Anthropic API key.

        Raises:
            ValueError: If the API key is not found in the environment file.
        """
        if not self.api_key:
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("A valid API Key for Anthropic is missing. Please set it in the .env file")
        return self.api_key
    
    def get_client(self):  
        """
        Initializes the OpenAI-compatible client for Anthropic (lazy initialization).

        Returns:
            OpenAI: The client configured for Anthropic API interactions.
        """
        if self.client is None:
            self.client = OpenAI(api_key=self.get_api_key(), base_url="https://api.anthropic.com/v1/")
        return self.client
    
    def generate_text(self, prompt: str, kwargs:dict = None, parse: bool = False) -> Union[str, SimpleNamespace]:
        """
        Generates text based on a single prompt using the Anthropic API.

        Args:
            prompt (str): The input prompt to send to the model.
            kwargs (dict, optional): Additional configurations to override the default parameters.
            parse (bool, optional): If True, attempts to parse the model's response (not supported by Anthropic).

        Returns:
            Union[str, SimpleNamespace]: Generated text or parsed structured output with metadata.

        Raises:
            RuntimeError: If there is an error during text generation.
        """
        client = self.get_client()

        kwargs = kwargs or {}

        # Temporary override (default behavior)
        system_message = kwargs.pop("system_message", self.system_message)

        if parse:
            response_format = kwargs.pop("response_format", None)
            if response_format is None:
                raise ValueError("response_format must be provided when parse=True")

            formatted_system_message = structuredoutput.format_system_message(response_format= response_format,
                                                                    user_system_prompt= system_message)
            user_message = {"role": "user", "content": prompt}
            messages = [formatted_system_message] + [user_message]
        else:
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}]

        base_params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty
        }
    
        base_params.update(self.kwargs)
        base_params.update(kwargs)

        try:
            if parse:
                max_retries = 3
                response = None
                for attempt in range(1, max_retries + 1):
                    try:
                        response = client.chat.completions.create(**base_params)
                        content = response.choices[0].message.content.strip()
                        json_content = structuredoutput.extract_json(content)
                        parsed = response_format.model_validate(json_content)
                        return SimpleNamespace(raw = response, parsed = parsed)
                    except (json.JSONDecodeError, ValidationError, ValueError) as e:
                        if attempt == max_retries:
                            return SimpleNamespace(raw=response, parsed=None, error=str(e))
                        wait = random.uniform(1,2)
                        time.sleep(wait)
            
            else:
                response = client.chat.completions.create(**base_params)
                return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Error generating text: {str(e)}")
    
    def batch_generate(self, prompts: List[str], kwargs: List[dict] = None, parse: List[bool] = None) -> List[str]:
        """
        Generate responses for multiple prompts in sequence.

        Args:
            prompts (List[str]): List of input prompts.
            kwargs (List[dict], optional): Optional list of parameter overrides per prompt.
            parse (List[bool], optional): Optional list indicating whether to use `parse` per prompt.

        Returns:
            List[str]: List of generated message contents or error messages.
        
        Raises:
            ValueError: If input list lengths are mismatched.
        """
        responses = []

        kwargs = kwargs if kwargs is not None else [{}] * len(prompts)
        parse = parse if parse is not None else [False] * len(prompts)

        if len(kwargs) != len(prompts):
            raise ValueError("The length of kwargs dictionaries must match the number of prompts.")
        if len(parse) != len(prompts):
            raise ValueError("The length of parse list must match the number of prompts.")
        
        for idx, prompt in enumerate(prompts):
            try:
                response = self.generate_text(prompt, kwargs[idx], parse[idx]) 
                responses.append(response)
            except Exception as e:
                responses.append(f"Error: {str(e)}")
        return responses
__all__ = []