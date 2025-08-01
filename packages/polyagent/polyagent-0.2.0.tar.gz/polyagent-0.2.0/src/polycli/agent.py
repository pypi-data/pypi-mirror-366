#!/usr/bin/env python3
"""
A reusable Python module for a stateful AI agent that interacts with the Claude CLI
or other LLMs via OpenRouter.

This version includes:
- Fake user messages that append to existing ones
- Routing to different models via unified API
- System prompt support (default and per-run)
- Auto-skip permissions for Claude Code
- Ephemeral messages for LLM runs (not added to memory)
"""

import json
import subprocess
import os
import sys
from pathlib import Path
import shutil
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Type, Callable
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from instructor import Mode
from dotenv import load_dotenv
from .utils.serializers import default_json_serializer

# Load environment variables from .env file
load_dotenv()

class Agent:
    """
    Manages a conversation with the Claude CLI or other LLMs, handling state and session resumption.

    The agent's state is stored entirely in the `self.memory` list. When continuing
    a conversation with existing history, the agent creates a new session file with
    the conversation history and uses the --resume flag to replay it.
    """

    def __init__(self, debug=False, openrouter_api_key=None, system_prompt=None, cwd=None):
        """Initializes a new Agent.

        Args:
            debug (bool): If True, prints detailed diagnostic information.
            openrouter_api_key (str): OpenRouter API key for using non-Claude models.
                                    If not provided, uses OPENROUTER_API_KEY env var.
            system_prompt (str): Default system prompt to use for all runs unless overridden.
            cwd (str|Path): Working directory for Claude Code execution. If None, uses current directory.
        """
        self.memory = []
        self.debug = debug
        self.default_system_prompt = system_prompt
        self.cwd = str(Path(cwd)) if cwd else None
        self._claude_cmd = self._find_claude_command()
        self._claude_projects_dir = Path.home() / ".claude" / "projects"
        
        # Initialize OpenRouter client if API key is available
        api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        self.llm_client = None
        if api_key:
            try:
                self.llm_client = instructor.from_openai(
                    OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1"),
                    mode=Mode.JSON
                )
            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] Failed to initialize OpenRouter client: {e}")
                    print("[DEBUG] Continuing without OpenRouter support")

    def _find_claude_command(self):
        claude_cmd = shutil.which('claude')
        if not claude_cmd:
            raise FileNotFoundError("Claude command not found. Please ensure it's in your PATH.")
        return claude_cmd

    def _encode_path(self, path_str: str) -> str:
        """Replicates Claude's path encoding for session files."""
        if sys.platform == "win32" and ":" in path_str:
            drive, rest = path_str.split(":", 1)
            rest = rest.lstrip(os.path.sep)
            path_str = f"{drive}--{rest}"
        return path_str.replace(os.path.sep, '-')

    def load_state(self, file_path):
        """Loads conversation history from a JSONL file.
        
        Args:
            file_path (str|Path): Path to the JSONL file to load from.
        """
        self.memory = []
        path = Path(file_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.memory.append(json.loads(line))

    def save_state(self, file_path):
        """Saves conversation history to a JSONL file.
        
        Args:
            file_path (str|Path): Path to the JSONL file to save to.
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            for msg in self.memory:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')
        if self.debug:
            print(f"[DEBUG] Persisted {len(self.memory)} messages to {path}")

    def _create_user_message(self, text_content: str, session_id: str, parent_uuid: str | None) -> dict:
        """
        Creates a user message dictionary.
        Always uses list-of-dicts for content, as per ground truth examples.
        """
        now_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        message_content = [{"type": "text", "text": text_content}]
        message_body = {"role": "user", "content": message_content}

        message = {
            "parentUuid": parent_uuid, "isSidechain": False, "userType": "external",
            "cwd": self.cwd if self.cwd else os.getcwd(),
            "sessionId": session_id, "version": "1.0.64",
            "gitBranch": "", "type": "user", "message": message_body,
            "uuid": str(uuid.uuid4()), "timestamp": now_iso
        }
        return message

    def add_user_message(self, user_text: str):
        """
        Adds a user message. If the last message is already from the user,
        appends to it with a newline. Otherwise, creates a new message.
        """
        if self.memory and self.memory[-1].get('type') == 'user':
            # Last message is already a user message - append to it
            last_message = self.memory[-1]
            
            # Get the content array from the message
            content = last_message['message']['content']
            
            # Find the last text content item and append to it
            for i in range(len(content) - 1, -1, -1):
                if content[i]['type'] == 'text':
                    # Append with a newline
                    content[i]['text'] += '\n' + user_text
                    break
            else:
                # No text content found (shouldn't happen), add new text content
                content.append({"type": "text", "text": user_text})
            
            # Update timestamp to current time
            last_message['timestamp'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            
            if self.debug:
                print(f"[DEBUG] Appended to existing user message. Memory size: {len(self.memory)}")
        else:
            # Last message is not a user message or memory is empty - create new message
            last_message = self.memory[-1] if self.memory else {}
            session_id = last_message.get('sessionId') or str(uuid.uuid4())
            parent_uuid = last_message.get('uuid')
            user_message = self._create_user_message(user_text, session_id, parent_uuid)
            self.memory.append(user_message)
            if self.debug:
                print(f"[DEBUG] Created new user message. Memory size: {len(self.memory)}")

    def _extract_conversation_history(self) -> List[Dict[str, str]]:
        """Extract meaningful text content from the conversation history for LLM consumption."""
        conversation = []
        
        for entry in self.memory:
            msg_type = entry.get('type')
            message = entry.get('message', {})
            role = message.get('role')
            content_list = message.get('content', [])
            
            # Skip system messages or empty content
            if not role or not content_list:
                continue
            
            # Extract text content
            text_parts = []
            for content_item in content_list:
                if isinstance(content_item, dict) and content_item.get('type') == 'text':
                    text = content_item.get('text', '').strip()
                    if text and text != '[Request interrupted by user]':
                        text_parts.append(text)
            
            # If we have meaningful text, add to conversation
            if text_parts:
                combined_text = ' '.join(text_parts)
                conversation.append({
                    'role': role,
                    'content': combined_text
                })
        
        return conversation

    def _run_with_llm(self, prompt: str, model: str, system_prompt: Optional[str] = None, ephemeral: bool = False, schema_cls: Optional[Type[BaseModel]] = None, memory_serializer: Optional[Callable[[BaseModel], str]] = None):
        """Run the prompt using an external LLM via OpenRouter.
        
        Args:
            prompt: The prompt to send
            model: Model name to use
            system_prompt: Optional system prompt for this run
            ephemeral: If True, the prompt and response won't be added to memory
        """
        if not self.llm_client:
            raise ValueError("OpenRouter API key not provided. Cannot use external models.")
        
        if self.debug:
            print(f"[DEBUG] Running with LLM model: {model} (ephemeral: {ephemeral})")
        
        # Extract current conversation history
        history = self._extract_conversation_history()
        
        # Prepare messages for the LLM
        messages = []
        
        # Use provided system prompt, fall back to default, or use a basic one
        effective_system_prompt = system_prompt or self.default_system_prompt or \
            "You are a helpful AI assistant. The following is a conversation history. Please provide a helpful response to the latest query."
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": effective_system_prompt
        })
        
        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Add the current prompt as a user message (in messages list, not memory)
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Define response model
        class LLMResponse(BaseModel):
            response: str = Field(description="The AI assistant's response")
        
        try:
            if schema_cls:
                # Structured response path
                result = self.llm_client.chat.completions.create(
                    response_model=schema_cls,
                    model=model,
                    messages=messages
                )
                
                # Only add to memory if not ephemeral
                if not ephemeral:
                    # Add the user's prompt as a user message
                    self.add_user_message(prompt)
                    
                    # Serialize for memory
                    serializer = memory_serializer or default_json_serializer
                    mem_text = serializer(result)
                    
                    # Add the LLM's response as a user message with clear attribution
                    response_text = f"\n[Structured response ({schema_cls.__name__})]\n{mem_text}"
                    self.add_user_message(response_text)
                
                # Return structured response
                return {
                    "result": result.model_dump(),
                    "session_id": self.memory[-1].get('sessionId') if self.memory else None,
                    "model": model,
                    "ephemeral": ephemeral
                }
            else:
                # Plain text response path (existing behavior)
                # Define response model for plain text
                class LLMResponse(BaseModel):
                    response: str = Field(description="The AI assistant's response")
                
                result = self.llm_client.chat.completions.create(
                    response_model=LLMResponse,
                    model=model,
                    messages=messages
                )
                
                # Only add to memory if not ephemeral
                if not ephemeral:
                    # Add the user's prompt as a user message
                    self.add_user_message(prompt)
                    
                    # Add the LLM's response as a user message with clear attribution
                    response_text = f"\n[Following is {model}'s response]\n{result.response}"
                    self.add_user_message(response_text)
                
                # Return standardized format
                return {
                    "result": result.response,
                    "session_id": self.memory[-1].get('sessionId') if self.memory else None,
                    "model": model,
                    "ephemeral": ephemeral
                }
            
        except Exception as e:
            error_msg = f"Error calling {model}: {str(e)}"
            if self.debug:
                print(f"[DEBUG] {error_msg}")
            return {"error": error_msg}

    def _run_with_claude(self, prompt: str, system_prompt: Optional[str] = None):
        """Run the prompt using Claude Code (original implementation)."""
        if self.debug: print("\n--- AGENT RUN (Claude) ---")

        current_dir = self.cwd if self.cwd else os.getcwd()
        cwd_encoded = self._encode_path(current_dir)
        session_dir = self._claude_projects_dir / cwd_encoded
        use_shell = sys.platform == 'win32'
        
        session_file_we_made = None
        session_file_claude_made = None

        try:
            # Determine the resume ID from memory. No memory means no resume ID.
            resume_id = self.memory[-1].get('sessionId') if self.memory else None

            # Build base command with required flags
            base_cmd = [self._claude_cmd, prompt, '-p', '--output-format', 'json', '--dangerously-skip-permissions']
            
            # Add system prompt if provided (use run-specific or fall back to default)
            effective_system_prompt = system_prompt or self.default_system_prompt
            if effective_system_prompt:
                base_cmd.extend(['--system-prompt', effective_system_prompt])

            if not resume_id:
                # --- Path 1: NEW CONVERSATION ---
                if self.debug: print("[DEBUG] STRATEGY: New conversation. Letting Claude handle state.")
                cmd = base_cmd
                result = subprocess.run(cmd, capture_output=True, text=True, shell=use_shell, cwd=current_dir, check=False, encoding="utf-8")
            else:
                # --- Path 2: RESUME CONVERSATION ---
                if self.debug: print(f"[DEBUG] STRATEGY: Resuming with Session ID: {resume_id}")
                
                session_file_we_made = session_dir / f"{resume_id}.jsonl"
                session_dir.mkdir(parents=True, exist_ok=True)
                with open(session_file_we_made, 'w', encoding='utf-8') as f:
                    for msg in self.memory:
                        f.write(json.dumps(msg) + '\n')
                if self.debug: print(f"[DEBUG] Wrote {len(self.memory)} messages to temp file: {session_file_we_made}")

                cmd = base_cmd + ['--resume', resume_id]
                result = subprocess.run(cmd, capture_output=True, text=True, shell=use_shell, cwd=current_dir, check=False, encoding="utf-8")

            # --- Process Result (Same for both paths) ---
            if result.returncode == 0:
                response_data = json.loads(result.stdout)
                
                # Use the new session ID from the response to load the updated history
                new_session_id = response_data.get('session_id')
                if new_session_id:
                    session_file_claude_made = session_dir / f"{new_session_id}.jsonl"
                    if self.debug: print(f"[DEBUG] Command successful. Loading updated history from NEW session file: {session_file_claude_made}")
                    
                    # Load a new memory state from the file Claude just created
                    new_memory = []
                    if session_file_claude_made.exists():
                        with open(session_file_claude_made, 'r', encoding='utf-8') as f:
                             for line in f:
                                if line.strip(): new_memory.append(json.loads(line))
                    self.memory = new_memory
                
                # Standardize response format to match OpenRouter format
                return {
                    "result": response_data.get('result'),
                    "session_id": response_data.get('session_id'),
                    "model": "claude-code",
                    "ephemeral": False,
                    # Keep original Claude metadata for advanced users
                    "_claude_metadata": response_data
                }
            else:
                error_details = f"Exit Code: {result.returncode}\n--- STDERR ---\n{result.stderr or 'No stderr.'}\n--- STDOUT ---\n{result.stdout or 'No stdout.'}\n"
                return {"error": error_details}

        finally:
            # Clean up both temporary session files
            if session_file_we_made and session_file_we_made.exists():
                if self.debug: print(f"[DEBUG] Cleaning up temp file we made: {session_file_we_made}")
                session_file_we_made.unlink()
            if session_file_claude_made and session_file_claude_made.exists():
                if self.debug: print(f"[DEBUG] Cleaning up file Claude made: {session_file_claude_made}")
                session_file_claude_made.unlink()

    def run(self, prompt: str, model: Optional[str] = None, system_prompt: Optional[str] = None, 
            ephemeral: bool = False, memory_cutoff: Optional[int] = None, 
            schema_cls: Optional[Type[BaseModel]] = None, memory_serializer: Optional[Callable[[BaseModel], str]] = None):
        """
        Runs a prompt, automatically handling session state, and returns the result.
        
        Args:
            prompt: The prompt to run
            model: Optional model name. If not provided, uses Claude Code.
                   If provided, uses the specified model via OpenRouter.
            system_prompt: Optional system prompt for this specific run.
                          If not provided, uses the default system prompt from __init__.
            ephemeral: If True and using a non-Claude model, the interaction won't be saved to memory.
                      This parameter is ignored for Claude Code calls.
            memory_cutoff: Maximum number of items to keep in memory. When exceeded, oldest items 
                          are removed. Default is 50. Set to None to disable cutoff.
        
        Returns:
            Dictionary with the response result
        """
        # Run the prompt with the appropriate method
        if model:
            result = self._run_with_llm(prompt, model, system_prompt, ephemeral, schema_cls, memory_serializer)
        else:
            if ephemeral and self.debug:
                print("[DEBUG] Warning: ephemeral parameter ignored for Claude Code calls")
            if schema_cls and self.debug:
                print("[DEBUG] Warning: schema_cls parameter ignored for Claude Code calls")
            result = self._run_with_claude(prompt, system_prompt)
        
        # Apply memory cutoff if enabled
        if memory_cutoff is not None and len(self.memory) > memory_cutoff:
            items_to_remove = len(self.memory) - memory_cutoff
            if self.debug:
                print(f"[DEBUG] Memory cutoff reached ({len(self.memory)} > {memory_cutoff}). "
                      f"Removing {items_to_remove} oldest items.")
            self.memory = self.memory[items_to_remove:]
        
        return result

