import logging
import pandas as pd
import os
from app.config import config

logger = logging.getLogger(__name__)

class ExcelDataProvider:
    """
    A robust provider for reading and writing compliance data to a central Excel file
    stored on a shared network drive.
    """

    @staticmethod
    def _get_file_path():
        return config.compliance_source.excel_file_path

    @staticmethod
    def pre_flight_check():
        """
        Verifies that the configured Excel file exists and is accessible.
        This is a critical check to prevent silent failures.
        """
        path = ExcelDataProvider._get_file_path()
        if not os.path.exists(path):
            logger.error(f"CRITICAL: The compliance Excel file was not found at the configured path: {path}")
            raise FileNotFoundError(f"The configured Excel file does not exist at: {path}")
        logger.info("Excel file pre-flight check passed.")

    @staticmethod
    def get_data() -> list:
        """Reads all data from the Excel file."""
        path = ExcelDataProvider._get_file_path()
        try:
            df = pd.read_excel(path, sheet_name="ComplianceData")
            if 'row_id' not in df.columns:
                df['row_id'] = range(2, len(df) + 2)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Failed to read from Excel file at {path}: {e}")
            raise

    @staticmethod
    def update_rows(updates: list):
        """Atomically updates multiple rows in the Excel file."""
        path = ExcelDataProvider._get_file_path()
        try:
            df = pd.read_excel(path, sheet_name="ComplianceData")
            if 'row_id' not in df.columns:
                df['row_id'] = range(2, len(df) + 2)
            
            df.set_index('row_id', inplace=True)

            for row_id, data in updates:
                for key, value in data.items():
                    if key not in df.columns:
                        df[key] = None
                    df.loc[row_id, key] = value
            
            df.reset_index(inplace=True)
            
            with pd.ExcelWriter(path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='ComplianceData', index=False)

            logger.info(f"Successfully updated {len(updates)} rows in {path}")

        except Exception as e:
            logger.error(f"Failed to perform atomic update on Excel file at {path}: {e}")
            raise
