from typing import Dict, Any
import openai as OpenAI

try:
    from google import genai
    HAS_GOOGLE = True
except ImportError:
    genai = None
    HAS_GOOGLE = False


class LanguageModel:
    """
    Represents a language model instance with provider-specific configuration.
    
    This class encapsulates the configuration needed to interact with different
    AI providers (OpenAI, Google, etc.) in a unified way.
    
    Attributes:
        provider (str): The name of the AI provider (e.g., 'openai', 'google')
        model (str): The specific model name (e.g., 'gpt-4', 'gemini-pro')
        client (any): The provider-specific client instance
        options (Dict[str, Any]): Additional provider-specific options
    """
    
    def __init__(
        self, provider: str, model: str, client: any, options: Dict[str, Any] = {}
    ):
        """
        Initialize a LanguageModel instance.
        
        Args:
            provider (str): The AI provider name
            model (str): The model identifier
            client (any): Provider-specific client instance
            options (Dict[str, Any], optional): Additional configuration options. Defaults to {}.
        """
        self.provider = provider
        self.model = model
        self.client = client
        self.options = options


def openai(model: str, **kwargs: Any) -> LanguageModel:
    """
    Create a LanguageModel instance configured for OpenAI models.
    
    This factory function initializes an OpenAI client and creates a LanguageModel
    instance ready for use with OpenAI's API.
    
    Args:
        model (str): The OpenAI model name (e.g., 'gpt-4', 'gpt-3.5-turbo')
        **kwargs: Additional options to pass to the model configuration
    
    Returns:
        LanguageModel: Configured LanguageModel instance for OpenAI
    
    Example:
        ```python
        model = openai("gpt-4", temperature=0.7, max_tokens=1000)
        ```
    
    Note:
        Requires OPENAI_API_KEY environment variable to be set.
    """
    client = OpenAI.AsyncOpenAI()
    return LanguageModel(provider="openai", model=model, client=client, options=kwargs)


def google(model: str, **kwargs: Any) -> LanguageModel:
    """
    Create a LanguageModel instance configured for Google Generative AI models.
    
    This factory function initializes a Google Generative AI client and creates a
    LanguageModel instance ready for use with Google's Gemini API.
    
    Args:
        model (str): The Google model name (e.g., 'gemini-pro', 'gemini-pro-vision')
        **kwargs: Additional options to pass to the model configuration
    
    Returns:
        LanguageModel: Configured LanguageModel instance for Google
    
    Example:
        ```python
        model = google("gemini-pro", temperature=0.7, max_output_tokens=1000)
        ```
    
    Note:
        Requires GOOGLE_API_KEY environment variable to be set.
        Requires google-genai package: pip install google-genai
    
    Raises:
        ImportError: If google-genai package is not installed
    """
    if not HAS_GOOGLE:
        raise ImportError(
            "Google Generative AI support requires the 'google-genai' package. "
            "Install it with: pip install google-genai"
        )
    
    client = genai.Client(api_key="AIzaSyBumhLp15LJmcVhx4MssSBJOi8TAZc6k64")
    return LanguageModel(provider="google", model=model, client=client, options=kwargs)
