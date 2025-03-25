from typing import Dict, Any, Optional, List
import logging
from agents import OpenAIChatCompletionsModel, OpenAIResponsesModel, ModelSettings
import openai

logger = logging.getLogger(__name__)

class ModelManagementError(Exception):
    """Base exception for model management errors."""
    pass

class InvalidAPIKeyError(ModelManagementError):
    """Exception raised when the API key is invalid."""
    pass

class UnsupportedModelError(ModelManagementError):
    """Exception raised when the requested model is not supported."""
    pass

class ModelManagementService:
    """Service for managing OpenAI models for use with agents."""
    
    # List of supported models
    SUPPORTED_MODELS = [
        "gpt-4", 
        "gpt-4-turbo", 
        "gpt-3.5-turbo",
        "gpt-4o"
    ]
    
    def _validate_api_key(self, api_key: str) -> bool:
        """
        Validate that the API key is properly formatted.
        This is a basic check - real validation happens when using the key with OpenAI.
        """
        if not isinstance(api_key, str):
            return False
        
        # OpenAI API keys typically start with "sk-" and have a specific length
        if not api_key.startswith("sk-") or len(api_key) < 20:
            return False
            
        return True
    
    def create_model_settings(
        self,
        temperature: float = 0.7,
        top_p: float = 1.0,
        max_tokens: Optional[int] = None,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> ModelSettings:
        """
        Create model settings with the specified parameters.
        
        Args:
            temperature: Controls randomness. Higher values make output more random.
            top_p: Controls diversity via nucleus sampling.
            max_tokens: Maximum number of tokens to generate.
            presence_penalty: Penalizes new tokens based on presence in text so far.
            frequency_penalty: Penalizes new tokens based on frequency in text so far.
            stop: A list of strings that will stop generation.
            **kwargs: Additional model settings parameters.
            
        Returns:
            A ModelSettings instance
        """
        settings_dict = {
            "temperature": temperature,
            "top_p": top_p,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            **kwargs
        }
        
        if max_tokens is not None:
            settings_dict["max_tokens"] = max_tokens
            
        if stop is not None:
            settings_dict["stop"] = stop
            
        return ModelSettings(**settings_dict)
    
    def create_model(
        self,
        api_key: str,
        model_name: str = "gpt-4o",
        settings: Optional[ModelSettings] = None,
        use_chat_completions: bool = False
    ) -> OpenAIResponsesModel:
        """
        Create an OpenAI model instance.
        
        Args:
            api_key: The OpenAI API key to use
            model_name: The name of the model to use
            settings: Optional model settings
            use_chat_completions: If True, use OpenAIChatCompletionsModel instead of OpenAIResponsesModel
            
        Returns:
            An OpenAI model instance (OpenAIResponsesModel by default)
            
        Raises:
            InvalidAPIKeyError: If the API key is invalid
            UnsupportedModelError: If the model is not supported
        """
        if not self._validate_api_key(api_key):
            raise InvalidAPIKeyError("Invalid API key format")
            
        if model_name not in self.SUPPORTED_MODELS:
            raise UnsupportedModelError(f"Model {model_name} is not supported. Supported models: {', '.join(self.SUPPORTED_MODELS)}")
        
        try:
            # Create OpenAI client
            client = openai.AsyncOpenAI(api_key=api_key)
            
            # Create model with client - use OpenAIResponsesModel by default
            if use_chat_completions:
                logger.info(f"Creating OpenAIChatCompletionsModel with model {model_name}")
                model = OpenAIChatCompletionsModel(
                    model=model_name,
                    openai_client=client
                )
            else:
                logger.info(f"Creating OpenAIResponsesModel with model {model_name}")
                model = OpenAIResponsesModel(
                    model=model_name,
                    openai_client=client
                )
            
            # Apply settings if provided
            if settings:
                model.model_settings = settings
                
            return model
            
        except Exception as e:
            logger.error(f"Error creating model: {str(e)}")
            raise ModelManagementError(f"Error creating model: {str(e)}") 