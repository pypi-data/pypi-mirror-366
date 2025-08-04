import importlib
import warnings
from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List

from ..schemas import ChatMessage, LLMResponse
from ..utils import option_callback

warnings.filterwarnings("ignore", category=DeprecationWarning)


class Provider(ABC):
    """Base abstract class for LLM providers"""

    APP_NAME = "yaicli"
    APP_REFERER = "https://github.com/belingud/yaicli"

    @abstractmethod
    def completion(
        self,
        messages: List[ChatMessage],
        stream: bool = False,
    ) -> Generator[LLMResponse, None, None]:
        """
        Send a completion request to the LLM provider

        Args:
            messages: List of message objects representing the conversation
            stream: Whether to stream the response

        Returns:
            Generator yielding LLMResponse objects
        """
        pass

    @abstractmethod
    def detect_tool_role(self) -> str:
        """Return the role that should be used for tool responses"""
        pass

    def _convert_messages(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """Convert a list of ChatMessage objects to a list of OpenAI message format.

        Args:
            messages: List of ChatMessage

        Returns:
            List of OpenAI message format
        """
        converted_messages = []
        for msg in messages:
            message: Dict[str, Any] = {"role": msg.role, "content": msg.content or ""}

            if msg.name:
                message["name"] = msg.name

            if msg.role == "assistant" and msg.tool_calls:
                message["tool_calls"] = [
                    {"id": tc.id, "type": "function", "function": {"name": tc.name, "arguments": tc.arguments}}
                    for tc in msg.tool_calls
                ]

            if msg.role == "tool" and msg.tool_call_id:
                message["tool_call_id"] = msg.tool_call_id

            converted_messages.append(message)

        return converted_messages


class ProviderFactory:
    """Factory to create LLM provider instances"""

    providers_map = {
        "ai21": (".providers.ai21_provider", "AI21Provider"),
        "anthropic": (".providers.anthropic_provider", "AnthropicProvider"),
        "anthropic-bedrock": (".providers.anthropic_provider", "AnthropicBedrockProvider"),
        "anthropic-vertex": (".providers.anthropic_provider", "AnthropicVertexProvider"),
        "bailian": (".providers.bailian_provider", "BailianProvider"),
        "bailian-intl": (".providers.bailian_provider", "BailianIntlProvider"),
        "cerebras": (".providers.cerebras_provider", "CerebrasProvider"),
        "chatglm": (".providers.chatglm_provider", "ChatglmProvider"),
        "chutes": (".providers.chutes_provider", "ChutesProvider"),
        "cohere": (".providers.cohere_provider", "CohereProvider"),
        "cohere-bedrock": (".providers.cohere_provider", "CohereBadrockProvider"),
        "cohere-sagemaker": (".providers.cohere_provider", "CohereSagemakerProvider"),
        "deepseek": (".providers.deepseek_provider", "DeepSeekProvider"),
        "doubao": (".providers.doubao_provider", "DoubaoProvider"),
        "fireworks": (".providers.fireworks_provider", "FireworksProvider"),
        "gemini": (".providers.gemini_provider", "GeminiProvider"),
        "groq": (".providers.groq_provider", "GroqProvider"),
        "huggingface": (".providers.huggingface_provider", "HuggingFaceProvider"),
        "infini-ai": (".providers.infiniai_provider", "InfiniAIProvider"),
        "minimax": (".providers.minimax_provider", "MinimaxProvider"),
        "mistral": (".providers.mistral_provider", "MistralProvider"),
        "modelscope": (".providers.modelscope_provider", "ModelScopeProvider"),
        "moonshot": (".providers.moonshot_provider", "MoonshotProvider"),
        "nvida": (".providers.nvida_provider", "NvidiaProvider"),
        "ollama": (".providers.ollama_provider", "OllamaProvider"),
        "openai": (".providers.openai_provider", "OpenAIProvider"),
        "openai-azure": (".providers.openai_provider", "OpenAIAzure"),
        "openai-compatible": (".providers.openai_compatible_provider", "OpenAICompatibleProvider"),
        "openrouter": (".providers.openrouter_provider", "OpenRouterProvider"),
        "sambanova": (".providers.sambanova_provider", "SambanovaProvider"),
        "siliconflow": (".providers.siliconflow_provider", "SiliconFlowProvider"),
        "spark": (".providers.spark_provider", "SparkProvider"),
        "targon": (".providers.targon_provider", "TargonProvider"),
        "together": (".providers.together_provider", "TogetherProvider"),
        "vertexai": (".providers.vertexai_provider", "VertexAIProvider"),
        "xai": (".providers.xai_provider", "XaiProvider"),
        "yi": (".providers.yi_provider", "YiProvider"),
    }

    @classmethod
    def create_provider(cls, provider_type: str, verbose: bool = False, **kwargs) -> Provider:
        """Create a provider instance based on provider type

        Args:
            provider_type: The type of provider to create
            **kwargs: Additional parameters to pass to the provider

        Returns:
            A Provider instance
        """
        provider_type = provider_type.lower()
        if provider_type not in cls.providers_map:
            raise ValueError(f"Unknown provider: {provider_type}")

        module_path, class_name = cls.providers_map[provider_type]
        module = importlib.import_module(module_path, package="yaicli.llms")
        return getattr(module, class_name)(verbose=verbose, **kwargs)

    @classmethod
    @option_callback
    def list_providers(cls, _: Any) -> None:
        """List the available providers and exit."""
        print("Available PROVIDERS:")
        print("--------------------")
        for i in cls.providers_map:
            print(i)
        print("--------------------")
