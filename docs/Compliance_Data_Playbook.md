# Playbook: Managing Compliance Data

**Version:** 2.0
**Last Updated:** 2026-04-21

This document outlines the process for managing the municipal sign code data used by the Mustang Sage application.

## 1. Overview

The application's compliance knowledge is sourced from a central Excel file stored on a shared network drive. This allows for easy and reliable updates by non-technical experts.

The system uses two automated scripts:
- A **Change Detection Script** runs weekly to monitor official city websites for changes and flag them for review within the Excel file.
- A **Compliance Ingestion Script** runs nightly to synchronize the verified data from the Excel file into the application's database.

## 2. Configuration

- **File Path:** The location of the master Excel file is configured in `config/scale.yaml` under `compliance_source.excel_file_path`. This path **must** be accessible from the server where the scripts are run.
- **Roles:** The `Compliance Data Owner` and `Technical Contact` are defined in `config/scale.yaml` under the `governance` section.

## 3. The Update Workflow

### Step 1: Reviewing Suggested Changes

1.  The automated **Change Detection Script** monitors the city websites listed in the Excel file.
2.  If a change is detected, it will update the **`Suggested Change?`** column to `"Yes - Review Needed"` and populate the **`Before Text`** and **`After Text`** columns.
3.  The **Compliance Data Owner** should periodically open the Excel file to check for any rows flagged for review.

### Step 2: Verifying and Updating the Data

1.  For each flagged row, compare the `Before Text` and `After Text` columns.
2.  Visit the official `Source URL` to verify the change in its original context.
3.  Copy the new, correct, and exact legal text and paste it into the **`Full Text`** cell. Update other relevant cells like `Key Constraints` as needed.
4.  Change the `Suggested Change?` value back to `"No"`.
5.  Save the Excel file.

### Step 3: Automated Synchronization

1.  The automated **Compliance Ingestion Script** runs every night.
2.  It reads the content from the configured Excel file.
3.  After processing a row, it will update the **`Sync Status`** column in the Excel file with a timestamp (e.g., `✅ Synced on ...`).

## 4. Error Handling

-   If you see an error in the **`Sync Status`** column (e.g., `❌ ERROR: ...`), please check the formatting of your recent changes. If the error persists, contact the **Technical Contact**.
-   If the `Sync Status` timestamps appear to be more than 24 hours old, the **Technical Contact** will have already received an automated email alert and will be investigating.
-   If the Excel file is moved or renamed, the scripts will fail and send an alert to the **Technical Contact**.

## 5. Backups

The master Excel file should be backed up regularly as part of your organization's standard file backup procedures for shared network drives.
