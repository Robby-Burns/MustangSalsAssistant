import logging

logger = logging.getLogger(__name__)

class MarginValidator:
    """Enforces minimum project margins.
    # See mustang_whisper_system_prompt.md (Guardrails on Minimum 35% Margin).
    """
    @staticmethod
    def validate(margin_decimal: float) -> bool:
        if margin_decimal < 0.35:
            logger.error(f"MARGIN ERROR: Proposed margin {margin_decimal*100:.1f}% is below 35% floor.")
            return False
        
        logger.info(f"Margin validated: {margin_decimal*100:.1f}%")
        return True
