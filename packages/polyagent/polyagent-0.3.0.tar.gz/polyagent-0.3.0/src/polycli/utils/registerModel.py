
import litellm   # or: from litellm.utils import register_model

litellm.register_model(           # <- adds an entry to litellm.model_cost at runtime
    {
        "z-ai/glm-4.5": {
            "litellm_provider": "openrouter",
            "mode": "chat",            # or "completion" / "embedding"
            "max_tokens": 131072,
            "input_cost_per_token": 0.0,
            "output_cost_per_token": 0.0,
        }
    }
)

