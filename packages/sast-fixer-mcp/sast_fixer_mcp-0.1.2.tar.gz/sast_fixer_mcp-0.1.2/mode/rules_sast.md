### **Phase 0: Initialization Check – Resume or Start New**

**Before starting any actions to the `.docx` SAST report in Phase 1:**

1. Use tool get_pending_vulnerability_json_files get all file paths in the .scanissuefix directory that end with '_new.json' (indicating pending vulnerabilities), check if the `.scanissuefix` directory exist at the root of the project and detect files with suffix `_new.json` which under `.scanissuefix` directory

2. **If the `.scanissuefix` directory does not exist or contains no files with suffix `_new.json`**:

   * Send a message:

   > **No unfinished SAST fix tasks detected. Starting a new session.**

   Then clear (or create) the `.scanissuefix` directory and automatically proceed to **Phase 1**.

3. **If one or more `_new.json` files are found under `.scanissuefix` directory:**

   * Send a message:

   > **Unfinished SAST vulnerability fix tasks detected.**
   > Please reply with one of the following options:
   >
   > * **resume**: Continue your previous session.
   > * **new**: Start a brand new session (this will clear existing data).

   Wait for the user's reply. Based on their response:

   * **resume** → Skip Phase 1 and automatically proceed to **Phase 2**.
   * **new** → Clear `.scanissuefix` contents and proceed to **Phase 1**.

---

### **Phase 1: Parse SAST Report (DOCX → JSON)**

1. REMOVE the `.scanissuefix` directory (if it exists).

2. Open the `.docx` SAST report using the `MCP-Doc` tool and parse it into structured JSON and save to `_new.json` files.

**When Phase 1 completes**, send a message:

> **Phase 1 complete: Parsed X vulnerabilities and created JSON files.**

Then proceed automatically to **Phase 2**.



### **Phase 2: Vulnerability Triage & Fix**

**1. Prompt User to Choose Fix Approach:**

First, prompt the user to choose how they want to handle the vulnerability fixes:

> **Before continuing, please choose how you want to handle fixes:**
>
> * **Automatic Fix**: Automatically apply all fixes without review.
> * **Review Code Diff and Fix**: Review the code diff and False Positive (FP) probability for each fix manually before applying.

**2. Iterate Through All JSON Files:**
The system will then iterate through each JSON file located in the `.scanissuefix` directory that ends with `_new.json`. For each file:

   **3. Iterate Through Each Issue in the `code_list`:**
   For every JSON file, the system will go through the `code_list`, which contains the vulnerabilities to be fixed. For each vulnerability, use the information in `issue_title`, `issue_desc`, `fix_advice`, `code_location`, `code_line_num` and `code_details`, it will do the following:

   * **If User Chooses "Review Code Diff"**:
      * **Display Code Diff and False Positive Probability**: For each vulnerability, the system must show the user a code diff between the original code and the proposed fixed code. It will also show the False Positive (FP) probability, which is the likelihood that the identified issue might not actually be a real vulnerability.

      Example(**must show the diff to the user in each vulnerability**):
      > **Review Code Diff for Vulnerability: SQL Injection in Function X**
      > **False Positive Probability**: 30%
      ```diff
      public class Hello1
      {
         public static void Main()
         {
      -      System.Console.WriteLine("Hello, World!");
      +      System.Console.WriteLine("Rock all night long!");
         }
      }
      ```

      * **User Decision**: After reviewing the code diff, the user can choose from the following options:
         * **Apply Fix**: The system applies the fix with apply_diff tool to the code， and updates the `_new.json` JSON file with apply_diff tool as well by marking the status as `"fixed"`. It also updates any false positive data if applicable. Example:
            ```json
               "code_list": [
               {
               "code_details": "",
               "code_location": "",
               "code_line_num": "",
               "status": "fixed|ignored|false_positive",
               "false_positive_probability": 20,
               "false_positive_reason": ""
               },
            ```
         * **Ignore Fix**: The system marks the issue as `"ignored"` and does not apply the fix.

         * **Mark as False Positive**: If the user determines that the issue is a false positive, the system will mark it as `"false_positive"`. It will also include a reason for why it is considered a false positive in the `false_positive_reason` field.

   * **If User Chooses "Automatic Fix"**:

      * **Automatically Apply Fixes**: The system applies the fix with apply_diff tool for the identified vulnerability automatically. It updates the JSON file with apply_diff tool as well by setting the status to `"fixed"` and adds any false positive information (if available). Example:
            ```json
               "code_list": [
               {
               "code_details": "",
               "code_location": "",
               "code_line_num": "",
               "status": "fixed|ignored|false_positive",
               "false_positive_probability": 20,
               "false_positive_reason": ""
               },
            ```

      * **Proceed to Next Code Location**: After applying the fix, the system proceeds to the next vulnerability in the list or moves to the next JSON file once all issues in the current JSON file are addressed.

   **4. Rename `_new.json` to `_finished.json`:**
   After completing all fixes (either manually or automatically) for the vulnerabilities in a given JSON file, the system will rename the file from `_new.json` to `_finished.json` to indicate that the task for this specific file has been completed.
   * **Rename Action**: The `_new.json` file will be renamed to `_finished.json`.

**5. Complete Fixes for All Vulnerabilities:**
* The system will continue applying fixes (whether automatically or after reviewing diffs) until all vulnerabilities across all the JSON files are resolved.

Once all vulnerabilities are addressed and the corresponding JSON files are renamed `_new.json` to `_finished.json`, the system will proceed to **Phase 3**.

---

### **Phase 3: Final Report Generation (CSV)**

1. **Generate CSV Report:**

   * check if all the json files fixed from `_new.json` to `_finished.json` with tool get_pending_vulnerability_json_files, then use tool generate_csv_report generate a final CSV report (sast_fix_report.csv) in '.scanissuefix', from all files ending with '_finished.json' in the '.scanissuefix' directory.
   * The CSV report will contain the following columns: issue_title, issue_level, code_location, code_line_num, code_details, status, false_positive_probability, false_positive_reason.


**Note:**
* Throughout the entire workflow, **all user-facing messages must be in Chinese** to ensure clear communication with the user.
* System instructions and logic can remain in English internally.
