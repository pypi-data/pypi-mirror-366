#!/usr/bin/env python3
"""
GitLab Merge Request (MR) automatic code review using Gemini AI and Jira.

This script performs code reviews on merge requests using Google's Gemini AI.
It chunks large diffs, posts comments on GitLab, generates a report, and
creates a sub-task in Jira for the code review.

Environment Variables:
    GITLAB_TOKEN: GitLab API token with merge request write access.
    GEMINI_API_KEY: Google Gemini API key.
    CI_PROJECT_ID: GitLab project ID (set by GitLab CI).
    CI_MERGE_REQUEST_IID: Merge request IID (set by GitLab CI).
    CI_SERVER_URL: The base URL of the GitLab instance.
    JIRA_URL: The base URL of the Jira instance (e.g., https://jira.yourcompany.com).
    JIRA_USER: The email address for Jira authentication.
    JIRA_TOKEN: The API token for Jira authentication.
    DEBUG: Set to "1" or "true" for verbose logging.
"""

import json
import os
import re
import sys
import time
import traceback
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple

import requests
from google import generativeai as genai
from jira import JIRA, JIRAError

# --- Data Classes ---

@dataclass
class ReviewResult:
    """Aggregated review result across one or many Gemini calls."""
    approved: bool
    summary: str
    issues: List[Dict[str, str]] = field(default_factory=list)
    score: int = 0  # 0-100

# --- Service Classes ---

class GitLabService:
    """Handles all communication with the GitLab API."""

    def __init__(self, project_id: str, mr_iid: str, gitlab_token: str, gitlab_url: str):
        self.project_id = project_id
        self.mr_iid = mr_iid
        self.gitlab_url = gitlab_url
        self.headers = {"Authorization": f"Bearer {gitlab_token}", "Content-Type": "application/json"}

    def get_mr_info(self) -> Dict[str, Any]:
        """Fetches the core details of the merge request."""
        url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/merge_requests/{self.mr_iid}"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_mr_changes(self) -> List[Dict[str, Any]]:
        """Fetches the changes (diffs) for the merge request."""
        url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/merge_requests/{self.mr_iid}/changes"
        response = requests.get(url, headers=self.headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("changes", [])

    def create_mr_note(self, body: str) -> None:
        """Posts a general comment on the merge request."""
        url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/merge_requests/{self.mr_iid}/notes"
        try:
            requests.post(url, headers=self.headers, json={"body": body}, timeout=30).raise_for_status()
        except requests.RequestException as e:
            print(f"❌ Failed to post MR note: {e}")

    def _extract_position_from_note(self, note: Dict) -> Optional[Tuple[str, int]]:
        """Extracts file path and line number from a note's position data."""
        position = note.get('position', {})
        if not position:
            return None
            
        # Get file path (can be in new_path or old_path)
        file_path = position.get('new_path') or position.get('old_path')
        if not file_path:
            return None
            
        # Get line number (can be in new_line or old_line)
        line_number = position.get('new_line') or position.get('old_line')
        if not line_number:
            return None
            
        return (file_path, line_number)

    def check_and_resolve_discussions(self, current_issues: List[Dict[str, Any]]) -> None:
        """Check existing discussions and resolve those that are no longer relevant."""
        existing_discussions = self.get_mr_discussions()
        if not existing_discussions:
            return
            
        # Create a set of (file_path, line_number) for current issues
        current_issue_positions = set()
        for issue in current_issues:
            file_path, line = issue.get('file'), issue.get('line_number')
            if file_path and isinstance(line, int) and line > 0:
                current_issue_positions.add((file_path, line))
        
        # Check each discussion
        for discussion in existing_discussions:
            try:
                # Skip if not a discussion with notes or if it's already resolved
                if not discussion.get('notes') or discussion.get('resolvable') is False:
                    continue
                    
                # Get the first note that has position information
                for note in discussion['notes']:
                    position = self._extract_position_from_note(note)
                    if not position:
                        continue
                        
                    file_path, line_number = position

                    # If this issue is no longer in current issues, mark as resolved
                    if (file_path, line_number) not in current_issue_positions and not note.get('resolved'):
                        print(f"ℹ️ Issue at {file_path}:{line_number} appears to be fixed. Resolving discussion...")
                        self.resolve_discussion(discussion['id'], resolved=True)
                    
                    # Once we've processed a positioned note, move to the next discussion
                    break
                    
            except (AttributeError, KeyError) as e:
                print(f"⚠️ Error processing discussion for resolution check: {e}")
                continue

    def _get_existing_discussion_positions(self) -> Set[Tuple[str, int]]:
        """Get a set of (file_path, line_number) for all existing discussions."""
        existing_discussions = self.get_mr_discussions()
        existing_positions = set()
        
        for discussion in existing_discussions:
            try:
                # Skip if not a discussion with notes
                if not discussion.get('notes'):
                    continue
                    
                # Get the first note that has position information
                for note in discussion['notes']:
                    position = self._extract_position_from_note(note)
                    if position:
                        existing_positions.add(position)
                        break  # Only need one position per discussion
                        
            except (AttributeError, KeyError) as e:
                print(f"⚠️ Error processing existing discussion: {e}")
                continue
                
        return existing_positions

    def create_mr_discussions(self, issues: List[Dict[str, Any]], line_map: Dict, mr_details: Dict) -> None:
        """Creates discussions on the MR for each issue found, avoiding duplicates."""
        # First, check and resolve any discussions that are no longer relevant
        self.check_and_resolve_discussions(issues)
        
        # Get existing discussion positions to avoid duplicates
        existing_positions = self._get_existing_discussion_positions()
        
        if not issues:
            print("ℹ️ No issues to report.")
            return

        url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/merge_requests/{self.mr_iid}/discussions"
        successful, ignored, failed = 0, 0, 0

        # Filter out issues that already have discussions
        filtered_issues = []
        for issue in issues:
            file_path, new_line = issue.get("file"), issue.get("line_number")
            if not (file_path and isinstance(new_line, int) and new_line > 0):
                continue
                
            # Check if there's already a discussion for this position
            if (file_path, new_line) in existing_positions:
                print(f"ℹ️ Skipping duplicate issue at {file_path}:{new_line} - discussion already exists")
                continue
                
            filtered_issues.append(issue)
        
        if not filtered_issues:
            print("ℹ️ No new issues to report after filtering duplicates.")
            return
            
        print(f"ℹ️ Found {len(filtered_issues)} new issues to report (after filtering duplicates).")
        
        for idx, issue in enumerate(filtered_issues, 1):
            print(f"⏳ Processing issue {idx}/{len(filtered_issues)}...")
            file_path, new_line = issue.get("file"), issue.get("line_number")
            if not (file_path and isinstance(new_line, int) and new_line > 0):
                ignored += 1
                continue

            old_line = line_map.get(file_path, {}).get(new_line)
            if old_line is None:
                print(f"⚠️ Could not map line {new_line} in {file_path}. Skipping.")
                ignored += 1
                continue

            position_data = self._get_file_diff_position(file_path, old_line, new_line, **mr_details)
            if not position_data:
                ignored += 1
                continue

            body = f"## {issue.get('severity', 'suggestion').upper()}: {issue.get('description', '')}\n\n ```{issue.get('suggestion', '')}```"
            discussion_data = {'body': body, 'position': position_data}
            
            if self._create_discussion_with_retry(url, discussion_data):
                successful += 1
            else:
                failed += 1

        print(f"\n📊 Discussion creation summary: ✅ {successful} successful, ⚠️ {ignored} ignored, ❌ {failed} failed.")

    def approve_mr(self) -> None:
        """Approves the merge request."""
        url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/merge_requests/{self.mr_iid}/approve"
        try:
            requests.post(url, headers=self.headers, timeout=30).raise_for_status()
            print("✅ MR approved successfully.")
        except requests.RequestException as e:
            print(f"⚠️ Failed to approve MR: {e}")

    def merge_mr(self) -> bool:
        """Merges the merge request."""
        url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/merge_requests/{self.mr_iid}/merge"
        try:
            # First approve the MR if not already approved
            self.approve_mr()
            
            # Then merge the MR
            response = requests.put(
                url,
                headers=self.headers,
                params={"merge_when_pipeline_succeeds": True},
                timeout=30
            )
            response.raise_for_status()
            print("✅ MR merged successfully.")
            return True
        except requests.RequestException as e:
            print(f"⚠️ Failed to merge MR: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return False

    def _get_file_diff_position(self, file_path: str, old_line: int, new_line: int, base_sha: str, head_sha: str, start_sha: str) -> Optional[Dict]:
        """Builds the position object for a single-line diff comment."""
        if new_line <= 0:
            return None
        
        position = {"position_type": "text", "base_sha": base_sha, "start_sha": start_sha, "head_sha": head_sha, "old_path": file_path, "new_path": file_path, "new_line": new_line}
        if old_line > 0:
            position['old_line'] = old_line
        return position

    def get_mr_discussions(self) -> List[Dict]:
        """Fetches all discussions for the merge request."""
        url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/merge_requests/{self.mr_iid}/discussions"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"⚠️ Failed to fetch MR discussions: {e}")
            return []
            
    def resolve_discussion(self, discussion_id: str, resolved: bool = True) -> bool:
        """Marks a discussion as resolved or unresolved."""
        url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/merge_requests/{self.mr_iid}/discussions/{discussion_id}"
        data = {"resolved": resolved}
        try:
            response = requests.put(url, headers=self.headers, json=data, timeout=30)
            if response.status_code == 200:
                status = "resolved" if resolved else "unresolved"
                print(f"✅ Successfully marked discussion {discussion_id} as {status}")
                return True
            else:
                print(f"⚠️ Failed to mark discussion {discussion_id} as {'resolved' if resolved else 'unresolved'}: {response.text}")
                return False
        except requests.RequestException as e:
            print(f"⚠️ Error marking discussion {discussion_id} as {'resolved' if resolved else 'unresolved'}: {e}")
            return False

    def _create_discussion_with_retry(self, url: str, data: Dict, max_retries: int = 3) -> bool:
        """Creates a discussion with exponential backoff retry logic."""
        last_error = None
        for attempt in range(max_retries):
            if attempt > 0:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"  ⏳ Retry attempt {attempt + 1}/{max_retries}, waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
            try:
                response = requests.post(url, headers=self.headers, json=data, timeout=(10, 30))
                if response.status_code == 201:
                    return True
                if 400 <= response.status_code < 500:
                    last_error = f"Client error {response.status_code}: {response.text}"
                    if response.status_code == 400:
                        print(f"\n⚠️ Validation Error. Position data: {json.dumps(data.get('position', {}), indent=2)}")
                    break
                last_error = f"Server error {response.status_code}: {response.text}"
                time.sleep((2 ** attempt) + random.uniform(0, 1))
            except requests.RequestException as e:
                last_error = f"Request failed: {e}"
                time.sleep((2 ** attempt) + random.uniform(0, 1))
        print(f"❌ Failed to create discussion. Last error: {last_error}")
        return False

class GeminiService:
    """Handles all communication with the Gemini API."""

    def __init__(self, api_key: str, ignore_severity: str = "", model_name: str = "gemini-1.5-flash", language: str = "en"):
        self.model_name = model_name
        self.ignore_severity = ignore_severity
        self.language = language
        self.generation_config = {"temperature": 0.3, "top_p": 0.95, "top_k": 40, "response_mime_type": "application/json"}
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            raise ValueError(f"Failed to configure Gemini: {e}") from e

    def analyze_code_chunk(self, file_path: str, snippet: str, mr_info: Dict) -> ReviewResult:
        """Sends a single code chunk to Gemini for review."""
        prompt = self._build_code_review_prompt(file_path, snippet, mr_info)
        try:
            print(f"🤖 Sending request to Gemini for code review on {file_path}...")
            response = self.model.generate_content(prompt, generation_config=genai.types.GenerationConfig(**self.generation_config))
            
            if not hasattr(response, 'text') or not response.text:
                raise ValueError(f"Empty response from Gemini. Feedback: {getattr(response, 'prompt_feedback', 'N/A')}")
            
            data = self._extract_json_from_text(response.text)
            score = max(0, min(100, int(data.get("score", 0))))
            print(f"✅ Successfully parsed response. Score: {score}")
            filtered_issues = [issue for issue in data.get("issues", []) if issue.get("severity") not in self.ignore_severity]
            return ReviewResult(approved=bool(data.get("approved", False)), summary=str(data.get("summary", "")), issues=filtered_issues, score=score)
        
        except Exception as e:
            print(f"❌ Error during Gemini analysis: {e}")
            return ReviewResult(approved=False, summary="Failed to analyze chunk.", issues=[], score=0)

    def generate_test_plan(self, mr_info: Dict, changes_diff: str, jira_key: Optional[str]) -> Optional[str]:
        """Generates a QA test plan using Gemini."""
        print("📝 Generating QA test plan...")
        prompt = self._build_test_plan_prompt(mr_info, changes_diff, jira_key)

        try:
            generation_config = self.generation_config.copy()
            generation_config.pop('response_mime_type')
            response = self.model.generate_content(prompt, generation_config=genai.types.GenerationConfig(**generation_config))

            if not hasattr(response, 'text') or not response.text:
                raise ValueError(f"Empty response from Gemini for test plan generation. Feedback: {getattr(response, 'prompt_feedback', 'N/A')}")
            
            print("✅ QA test plan generated successfully.")
            return response.text

        except Exception as e:
            print(f"❌ Error during test plan generation: {e}")
            if os.getenv("DEBUG"):
                traceback.print_exc()
            return None

    def _build_code_review_prompt(self, file_path: str, snippet: str, mr_info: Dict) -> str:
        """Returns the full prompt for a single code chunk."""
        language_instruction = "The language for the response should be in Brazilian Portuguese (pt-BR)." if self.language == "pt-BR" else "The language for the response should be in English (en)."
        
        return f"""
# Code Review Instructions
## You are a senior code reviewer specializing in full-stack development.
## Analyze the following code changes from a merge request and provide a detailed assessment.

**IMPORTANT:** {language_instruction}

**Merge Request Information:**
* Title: {mr_info.get('title', 'N/A')}
* Description: {mr_info.get('description', 'N/A')}
* Source Branch: {mr_info.get('source_branch', 'N/A')}
* File: {file_path}
* Language: {'Português do Brasil' if self.language == 'pt-BR' else 'English'}
* **Severities to Ignore:** `{', '.join(self.ignore_severity) if self.ignore_severity else 'N/A'}`

**Code Changes:**
```diff
{snippet}
```

**Review Guidelines:**
1.  **Code Quality**: Check for code smells, anti-patterns, and potential bugs.
2.  **Security**: Identify any security vulnerabilities or concerns.
3.  **Performance**: Look for potential performance issues.
4.  **Best Practices**: Ensure the code follows language and framework best practices.
5.  **Documentation**: Check if the code is well-documented.
6.  **Tests**: Verify if tests are present and adequate.

**Issue Filtering:**
* You **MUST** follow the `Severities to Ignore` parameter.
* If a severity level (e.g., `low`, `medium`) is listed in `Severities to Ignore`, you **MUST NOT** include any issues with that severity in your final response.
* **Example 1:** If `Severities to Ignore` is `"low"`, do not report any issues with `severity: "low"`.
* **Example 2:** If `Severities to Ignore` is `"low,medium"`, do not report any issues with `severity: "low"` or `severity: "medium"`.
* If `Severities to Ignore` is empty, report all identified issues.

**Response Format (JSON):**
Your response must be a valid JSON object, enclosed in a single ```json code block.
Do not include any text outside of this block.
```json
{{
  "score": 0-100,
  "approved": true/false,
  "summary": "{'Breve resumo da revisão' if self.language == 'pt-BR' else 'Brief summary of the review'}",
  "issues": [
    {{
      "title": "Title for issue",
      "file": "{file_path or 'N/A'}",
      "severity": "low/medium/high",
      "line_number": 123,
      "description": "{'Descrição do problema' if self.language == 'pt-BR' else 'Description of the issue'}",
      "suggestion": "{'Sugestão de correção (se aplicável)' if self.language == 'pt-BR' else 'Suggested fix (if applicable)'}"
    }}
  ]
}}
```

**Approval Criteria:**
- Score >= 75: Approve
- Score 60-74: Approve with suggestions
- Score < 60: Request changes

Be strict but constructive. Focus on real issues that impact quality, security, or performance.
Always include practical code snippets for every suggested improvement.
"""

    def _build_test_plan_prompt(self, mr_info: Dict, changes_diff: str, jira_key: Optional[str]) -> str:
        """Builds the prompt for generating a QA test plan."""
        max_diff_length = 15000
        truncated_diff = changes_diff[:max_diff_length] + ("\n... (diff truncated)" if len(changes_diff) > max_diff_length else "")

        return f"""
# CONTEXT
You are a Senior Software Quality Assurance (SQA) Engineer AI assistant, integrated into a CI/CD pipeline. 
Your primary goal is to accelerate and optimize the manual testing process by providing QA analysts with a targeted and intelligent test plan.
Your communication must be technical, clear, and objective, in Brazilian Portuguese (pt-BR).

# FINAL OBJECTIVE
Generate a practical test report in Markdown format. This report should guide manual testing, focusing on the areas most impacted by the merge request's changes and ensuring assertive test coverage.

# INPUT INFORMATION
1. JIRA_TICKET_KEY: {jira_key or 'N/A'}
2. JIRA_TICKET_DESCRIPTION:
---
{mr_info.get('description', 'No description provided.')}
---
3. GIT_DIFF_CONTENT:
---
{truncated_diff}
---

# DETAILED INSTRUCTIONS
## 1. Requirements Analysis (Business Context)
- Analyze the JIRA_TICKET_DESCRIPTION to understand the main goal, business rules, and acceptance criteria. Focus on the "why" of the change.

## 2. Code Analysis (Technical Impact)
- Analyze the GIT_DIFF_CONTENT to map the technical impact.
- Identify key components changed, critical logic alterations, new dependencies, and the presence of automated tests.

## 3. Test Plan Generation (Output)
- Build a test plan in **Markdown** with these sections: `## 📝 Resumo das Alterações`, `## ✅ Cenários de Teste Focados (Caminho Feliz)`, `## ⚠️ Cenários de Teste de Borda e Negativos`, `## 🔄 Sugestões para Testes de Regressão`, and optionally `## 👨‍💻 Informações Técnicas para o QA`.
- Use the specified table format for test cases.
- **IMPORTANT**: The entire output must be a single Markdown string.

| ID | Cenário de Teste | Passos para Execução | Resultado Esperado |
| :-- | :--- | :--- | :--- |
| CT-01 | Descrever o objetivo do teste. | 1. Faça X.<br>2. Clique em Y. | O sistema deve fazer Z. |
"""
    def _extract_json_from_text(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not extract valid JSON from response substring: {e}")


class JiraIntegration:
    """Handles all communication with a Jira instance."""

    def __init__(self, server_url: str, user: str, token: str):
        try:
            self.client = JIRA(server=server_url, basic_auth=(user, token))
            self.client.server_info()
            print("✅ Successfully connected to Jira.")
        except JIRAError as e:
            raise ConnectionError(f"Failed to connect to Jira. Status: {e.status_code}, Text: {e.text}") from e

    def _format_issue_details(self, issue: Dict[str, str]) -> str:
        """Format a single issue's details for the description."""
        details = []
        if 'severity' in issue:
            details.append(f"*Severity*: {issue['severity'].title()}")
        if 'file' in issue:
            details.append(f"*File*: {issue['file']}")
        if 'line' in issue:
            details.append(f"*Line*: {issue['line']}")
        if 'suggestion' in issue:
            details.append(f"*Suggestion*: {'{code}'} {issue['suggestion']} {'{code}'}")
        return "\n".join(details)

    def create_subtask(self, parent_key: str, summary: str, issues: List[Dict], description: str, score: int, mr_url: str, language: str = "en") -> Optional[str]:
        """Creates a sub-task or task in Jira.
        
        Args:
            parent_key: The key of the parent issue
            summary: Summary/title of the new issue
            issues: List of issues found in the code
            description: Detailed description of the review
            score: Review score (0-100)
            mr_url: URL of the merge request
            language: Language for the issue content
        """
        try:
            parent_issue = self.client.issue(parent_key)
            issue_type = next((t for t in self.client.issue_types() if t.subtask), None)
            if not issue_type:
                print("❌ Could not find 'Sub-task' issue type in this Jira project.")
                return None

            # Build detailed description
            description_parts = [
                description,
                f"\n*Review Score*: {score}/100\n",
                f"*Merge Request*: {mr_url}\n"
            ]

            # Add issues section if there are any
            if issues:
                description_parts.append("\n*Issues Found* ({}):\n".format(len(issues)))
                for i, issue in enumerate(issues, 1):
                    description_parts.extend([
                        f"\n---\n",
                        f"*Issue #{i}:* {issue.get('title', 'No title')}\n",
                        f"{self._format_issue_details(issue)}\n"
                    ])
            else:
                description_parts.append("\n*No issues found in the code review.*\n")

            full_description = "\n".join(description_parts)
           
            # Prepare fields for the issue
            fields = {
                "project": {"key": parent_issue.fields.project.key},
                "summary": summary,
                "description": full_description,
                "issuetype": {"id": issue_type.id},
                "parent": {"key": parent_key}
            }

            try:
                # Create the issue
                new_issue = self.client.create_issue(fields=fields)
                print(f"✅ Successfully created Jira sub-task: {new_issue.key}")
                return new_issue.key
            except JIRAError as e:
                print(f"❌ Failed to create Jira issue: {e.response.text}")
                if e.status_code == 400 and "issuetype" in str(e.response.text.lower()):
                    print("  - The issue type might not be available for this project.")
                return None

        except JIRAError as e:
            print(f"❌ An error occurred with Jira: {e.text}")
        except Exception as e:
            print(f"❌ An unexpected error occurred during sub-task creation: {e}")
        return None

    def add_comment_to_issue(self, issue_key: str, comment: str) -> bool:
        """Adds a comment to a specific Jira issue."""
        try:
            self.client.add_comment(issue_key, comment)
            print(f"✅ Successfully added comment to Jira issue {issue_key}.")
            return True
        except JIRAError as e:
            print(f"❌ Failed to add comment to Jira issue {issue_key}. Status: {e.status_code}, Text: {e.text}")
            return False

# --- Orchestrator Class ---

class ReviewOrchestrator:
    """Orchestrates the end-to-end code review process."""

    def __init__(self, gitlab_service: GitLabService, gemini_service: GeminiService, jira_config: Optional[Dict], language: str, auto_merge: bool = False):
        self.gitlab_service = gitlab_service
        self.gemini_service = gemini_service
        self.jira_config = jira_config
        self.language = language
        self.auto_merge = auto_merge
        self.ignore_severity = set(jira_config.get('ignore_severity', set())) if jira_config else set()
        self.jira_integration: Optional[JiraIntegration] = None
        if all(self.jira_config.get(k) for k in ['url', 'user', 'token']):
            try:
                self.jira_integration = JiraIntegration(
                    server_url=self.jira_config["url"],
                    user=self.jira_config["user"],
                    token=self.jira_config["token"]
                )
            except ConnectionError as e:
                print(f"⚠️ {e}")


    def run_review(self) -> bool:
        """Runs the entire automated review and integration process."""
        print("🚀 Starting automated review process...")
        mr_info = self.gitlab_service.get_mr_info()
        
        # Skip if MR is a draft
        mr_title = mr_info.get('title', '').lower()
        if 'draft' in mr_title or 'wip' in mr_title or 'draft:' in mr_title or 'wip:' in mr_title:
            print("⏭️  MR is marked as draft/WIP. Skipping review.")
            return False
            
        changes = self.gitlab_service.get_mr_changes()
        
        if not changes:
            print("✅ No changes detected to review.")
            return True

        split_changes = self._split_diffs_by_hunks(changes)
        result = self._analyze_changes(split_changes, mr_info)

        self.gitlab_service.create_mr_note(self._format_review_comment(result))

        if result.issues:
            mr_details = self._get_mr_details(mr_info)
            if mr_details:
                line_map = self._build_line_map_from_changes(split_changes)
                self.gitlab_service.create_mr_discussions(result.issues, line_map, mr_details)
            else:
                print("❌ Cannot create discussions without MR details.")

        if result.approved:
            print(f"👍 MR approved automatically (Score: {result.score}")
            self.gitlab_service.approve_mr()
            # Try to auto-merge the MR if enabled
            if self.auto_merge:
                if not self.gitlab_service.merge_mr():
                    print("⚠️ Auto-merge failed. Please merge manually.")
        else:
            print(f"👎 MR requires attention (Score: {result.score})")

        self._write_json_report(result, mr_info)

        if self.jira_integration:
            if len(result.issues) > 0:
                print("🚀 Integrating with Jira...")
                self._handle_jira_integration(mr_info, result, split_changes)
            else:
                print("❌ No issues found to integrate with Jira.")
        else:
            print("❌ Jira integration is disabled.")

        return result.approved

    def _analyze_changes(self, changes: List[Dict], mr_info: Dict) -> ReviewResult:
        """Analyzes all code changes and aggregates the results."""
        results = []
        print(f"🔬 Analyzing {len(changes)} changed file(s).")
        for change in changes:
            for hunk in change:
                print(f"⏳ Analyzing hunk in {hunk.get('file_path')} (lines {hunk.get('start_line')}-{hunk.get('end_line')})...")
                results.append(self.gemini_service.analyze_code_chunk(hunk.get('file_path'), hunk.get('diff'), mr_info))
        
        if not results:
            return ReviewResult(approved=True, summary="No content to review.", issues=[], score=100)
        
        avg_score = int(sum(r.score for r in results) / len(results))
        approved = all(r.approved for r in results) and avg_score >= 75
        summary = "\n\n".join(r.summary for r in results if r.summary)
        issues = [issue for r in results for issue in r.issues]
        
        return ReviewResult(approved=approved, summary=summary, issues=issues, score=avg_score)

    def _handle_jira_integration(self, mr_info: Dict, review_result: ReviewResult, changes: List) -> None:
        """Handles the entire Jira integration process."""
        jira_key = self._extract_jira_key(mr_info.get("title", "") or mr_info.get("description", ""))
        if not jira_key or not self.jira_integration:
            print("ℹ️ No Jira issue key found or Jira integration not configured. Skipping Jira integration.")
            return

        try:
            # Get the Jira issue to check if it's a subtask
            issue = self.jira_integration.client.issue(jira_key)
            is_subtask = hasattr(issue.fields, 'issuetype') and issue.fields.issuetype.subtask

            # Determine the target issue key (parent if current is a subtask, otherwise use current)
            target_key = str(issue.fields.parent.key) if is_subtask else jira_key
            
            # 1. Create the review task/subtask
            if is_subtask:
                print(f"ℹ️ {jira_key} is a subtask. Creating task in parent issue {target_key}")
                summary = f"Code Review for {jira_key}"
            else:
                print(f"ℹ️ Creating subtask for {jira_key}")
                summary = "Code Review"

            # 2. Create the review task/subtask
            self.jira_integration.create_subtask(
                parent_key=target_key,
                summary=summary,
                description=review_result.summary,
                issues=review_result.issues,
                score=review_result.score,
                mr_url=mr_info.get('web_url', ''),
                language=self.language
            )

            # 3. Generate and post the QA test plan
            changes_diff = "\n".join([hunk.get("diff", "") for file_changes in changes for hunk in file_changes])
            test_plan = self.gemini_service.generate_test_plan(mr_info, changes_diff, jira_key)
            if test_plan:
                self.jira_integration.create_subtask(
                    parent_key=target_key,
                    summary="QA Test Plan",
                    description=test_plan,
                    issues=[],
                    score=0,
                    mr_url  =mr_info.get('web_url', ''),
                    language=self.language
                )
            else:
                print("⚠️ Could not generate test plan, so no comment will be added to Jira.")

        except Exception as e:
            print(f"⚠️ Failed during Jira integration process: {e}")
            if os.getenv("DEBUG"):
                traceback.print_exc()

    def _split_diffs_by_hunks(self, changes: List[Dict]) -> List[List[Dict]]:
        """Splits diffs from a list of changes into hunks."""
        return [self._split_single_diff_by_hunks(c) for c in changes]

    def _split_single_diff_by_hunks(self, diff: Dict[str, str]) -> List[Dict[str, str]]:
        """Splits a unified diff patch into a list of hunks."""
        hunks, current_hunk_lines = [], []
        start_line, end_line = None, None
        hunk_header_re = re.compile(r"^@@\s+-\d+(?:,\d+)?\s+\+(?P<start>\d+)(?:,(?P<len>\d+))?\s+@@")
        
        for line in diff.get("diff", "").splitlines():
            match = hunk_header_re.match(line)
            if match:
                if current_hunk_lines:
                    hunks.append({
                        "file_path": diff.get("new_path", diff.get("old_path")),
                        "start_line": str(start_line), 
                        "end_line": str(end_line), 
                        "diff": "\n".join(current_hunk_lines).rstrip()
                    })
                start_line = int(match.group("start"))
                length = int(match.group("len") or 1)
                end_line = start_line + length - 1
                current_hunk_lines = [line]
            elif current_hunk_lines:
                current_hunk_lines.append(line)
        
        if current_hunk_lines:
            hunks.append({
                "file_path": diff.get("new_path", diff.get("old_path")),
                "start_line": str(start_line), 
                "end_line": str(end_line), 
                "diff": "\n".join(current_hunk_lines).rstrip()
            })
        return hunks

    def _build_line_map_from_changes(self, changes: List[List[Dict]]) -> Dict[str, Dict[int, int]]:
        """Creates a map from a new_line number to its corresponding old_line number."""
        line_map = {}
        hunk_re = re.compile(r"^@@ -(\d+),?\d* \+(\d+),?\d* @@")
        for file_changes in changes:
            for hunk in file_changes:
                file_path, diff_text = hunk.get("file_path"), hunk.get("diff")
                if not (file_path and diff_text):
                    continue
                
                line_map.setdefault(file_path, {})
                current_old_line, current_new_line = 0, 0
                
                for line in diff_text.split('\n'):
                    match = hunk_re.match(line)
                    if match:
                        current_old_line, current_new_line = int(match.group(1)), int(match.group(2))
                        continue
                    if not line: continue
                    
                    char = line[0]
                    if char == ' ':
                        line_map[file_path][current_new_line] = current_old_line
                        current_old_line += 1
                        current_new_line += 1
                    elif char == '+':
                        line_map[file_path][current_new_line] = 0
                        current_new_line += 1
                    elif char == '-':
                        current_old_line += 1
        return line_map

    def _get_mr_details(self, mr_data: Dict) -> Optional[Dict]:
        """Extracts and verifies required SHAs from MR data."""
        try:
            diff_refs = mr_data.get('diff_refs', {})
            return {'base_sha': diff_refs['base_sha'], 'head_sha': diff_refs['head_sha'], 'start_sha': diff_refs['start_sha']}
        except KeyError:
            print("❌ Could not determine required SHAs from MR details.")
            return None

    def _extract_jira_key(self, text: str) -> Optional[str]:
        """Extracts a Jira issue key from text (e.g., PROJ-123)."""
        if not text: return None
        match = re.search(r'([A-Z]{2,}-\d+)', text.upper())
        return match.group(1) if match else None

    def _format_review_comment(self, res: ReviewResult) -> str:
        """Formats the main summary comment for the MR."""
        status_emoji = "✅" if res.approved else "❌"
        score_emoji = "🟢" if res.score >= 80 else "🟡" if res.score >= 60 else "🔴"
        lines = [
            f"## {status_emoji} Gemini AI Review Summary",
            f"**Score**: {score_emoji} {res.score}/100",
            f"**Status**: {'APPROVED' if res.approved else 'NEEDS ATTENTION'}",
            "\n### General Summary\n",
            res.summary or "No summary provided."
        ]
        if res.issues:
            lines.append("\n### Issues Found\n")
            lines.extend([f"- `{i.get('file')}:{i.get('line_number')}`: {i.get('description')}" for i in res.issues])
        else:
            lines.append("\nNo specific issues identified. Great work! 🎉")
        lines.append("\n---\n*This analysis was generated automatically.*")
        return "\n".join(lines)

    def _write_json_report(self, result: ReviewResult, mr_info: Dict):
        """Writes a JSON report file with the review results."""
        report_data = {
            "approved": result.approved,
            "score": result.score,
            "issues_count": len(result.issues),
            "issues": result.issues,  # Include the full list of issues
            "mr": {
                "title": mr_info.get("title"),
                "author": mr_info.get("author", {}).get("name")
            }
        }
        try:
            with open("gemini-review-report.json", "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print("📄 JSON report created successfully.")
        except IOError as e:
            print(f"❌ Could not write JSON report: {e}")

# --- Entry-Point ---

def parse_ignore_severity(severity_str: Optional[str]) -> Set[str]:
    """Parse the ignore_severity string into a set of severities to ignore."""
    if not severity_str:
        return set()
    return set(s.strip().lower() for s in severity_str.split(','))

def main():
    """Main function to run the reviewer."""
    try:
        print("🚀 Initializing merge request analysis...")

        # Parse command line arguments
        import argparse
        parser = argparse.ArgumentParser(description='GitLab Gemini Code Reviewer')
        parser.add_argument('--ignore-severity', type=str, default='',
                          help='Comma-separated list of severities to ignore (e.g., low,medium)')
        parser.add_argument('--auto-merge', action='store_true',
                          help='Automatically merge the MR if the review is approved')
        args = parser.parse_args()

        # Parse ignore severities
        ignore_severity = parse_ignore_severity(os.getenv("IGNORE_SEVERITY", args.ignore_severity))
        if ignore_severity:
            print(f"ℹ️ Ignoring issues with severity: {', '.join(ignore_severity)}")
        
        language = os.getenv("REVIEW_LANGUAGE", "pt-BR").lower()
        if language not in ["en", "pt-br"]:
            language = "en"
        elif language == "pt-br":
            language = "pt-BR"

        gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        config = {
            "gitlab_token": os.getenv("GITLAB_TOKEN"),
            "gemini_api_key": os.getenv("GEMINI_API_KEY"),
            "project_id": os.getenv("CI_PROJECT_ID"),
            "mr_iid": os.getenv("CI_MERGE_REQUEST_IID"),
            "gitlab_url": os.getenv("CI_SERVER_URL"),
            "jira_config": {
                "url": os.getenv("JIRA_URL"),
                "user": os.getenv("JIRA_USER"),
                "token": os.getenv("JIRA_TOKEN"),
            },
            "ignore_severity": ignore_severity,
            "auto_merge": args.auto_merge
        }

        required_vars = ["gitlab_token", "gemini_api_key", "project_id", "mr_iid", "gitlab_url"]
        missing_vars = [name for name, value in config.items() if name in required_vars and not value]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        gitlab_service = GitLabService(project_id=config["project_id"], mr_iid=config["mr_iid"], gitlab_token=config["gitlab_token"], gitlab_url=config["gitlab_url"])
        gemini_service = GeminiService(api_key=config["gemini_api_key"], ignore_severity=config["ignore_severity"], language=language, model_name=gemini_model)

        orchestrator = ReviewOrchestrator(
            gitlab_service=gitlab_service,
            gemini_service=gemini_service,
            jira_config=config["jira_config"],
            language=language,
            auto_merge=config["auto_merge"]
        )
        orchestrator.run_review()
        sys.exit(0)
    except (ValueError, requests.RequestException, ConnectionError) as e:
        print(f"❌ Configuration or API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected fatal error occurred: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()