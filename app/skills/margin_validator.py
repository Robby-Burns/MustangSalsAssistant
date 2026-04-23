import logging
from app.config import config

logger = logging.getLogger(__name__)

class MarginValidator:
    """Enforces minimum project margins.
    # See mustang_whisper_system_prompt.md (Guardrails on Minimum 35% Margin).
    """
    @staticmethod
    def validate(margin_decimal: float) -> bool:
        margin_floor = config.business_rules.margin_floor
        if margin_decimal < margin_floor:
            logger.error(f"MARGIN ERROR: Proposed margin {margin_decimal*100:.1f}% is below {margin_floor*100:.0f}% floor.")
            return False
        
        logger.info(f"Margin validated: {margin_decimal*100:.1f}%")
        return True
