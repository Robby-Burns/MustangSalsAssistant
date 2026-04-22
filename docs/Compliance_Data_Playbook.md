# Playbook: How to Update Compliance Data

**Version:** 3.0
**Last Updated:** 2026-04-22

This guide explains how to update the municipal sign code data used by the Mustang Sage bot.

## 1. Your Tool: The Central Excel File

All compliance data is managed in a single Excel file stored on the company's shared network drive. This is the **single source of truth**.

-   **File Location:** The exact location of this file is configured by your IT team. Please ask your manager for the shortcut to the `compliance_data.xlsx` file.
-   **Your Role:** As the **Compliance Data Owner**, your responsibility is to keep the content of this file accurate and up-to-date.

## 2. The Update Process: A Simple Checklist

Follow these steps to update the compliance data.

### ✅ Step 1: Check for Automated Suggestions

The system has a "watchdog" that automatically checks the city websites for any text changes.

1.  Open the `compliance_data.xlsx` file from the shared drive.
2.  Look at the **`Suggested Change?`** column.
3.  If you see any rows marked **"Yes - Review Needed"**, it means the system has detected a change on the official website for that rule.

### ✅ Step 2: Review and Verify the Change

For each row that needs a review:

1.  The **`Before Text`** and **`After Text`** columns will show you what the system found. Compare these two columns to see what was added or removed.
2.  Go to the official website using the link in the **`Source URL`** column to see the change in its official context.
3.  Use your expert judgment to decide if the change is relevant and needs to be incorporated.

### ✅ Step 3: Update the Official Text

1.  If the change is important, copy the new, correct, and exact legal text from the city's website.
2.  Paste this text into the **`Full Text`** cell for that row.
3.  Update the **`Key Constraints`** cell with a short, simple summary of the main rules (e.g., "Max Height: 12ft").
4.  Once you are finished, change the value in the **`Suggested Change?`** column from "Yes - Review Needed" back to **"No"**.
5.  **Save the Excel file.**

### ✅ Step 4: Let the System Do the Rest

You are done. The system will take care of the rest automatically.

-   Overnight, an automated script will read your changes from the Excel file and update the bot's knowledge base.
-   The next morning, you can check the **`Sync Status`** column. It will be updated with a timestamp (e.g., `✅ Synced on...`) to confirm your changes are live.

## 3. What to Do If You See an Error

-   **If you see an `❌ ERROR` message in the `Sync Status` column:** This means there might be a formatting issue with the text you entered. Please double-check your work. If you can't find the problem, contact the **Technical Contact** for assistance.
-   **If the file is missing or you can't access it:** Contact the **Technical Contact** immediately.

*(To find the current Technical Contact, please ask your manager or refer to the project's internal configuration documents.)*
