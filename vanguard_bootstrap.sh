#!/bin/bash
# ==============================================================================
# VANGUARD BRIDGE BOOTSTRAP (UBUNTU)
# ==============================================================================
# Purpose: Recreate the Vanguard Proxy + OpenCode environment on a new machine.
# Usage:   bash vanguard_bootstrap.sh

set -e

echo "------------------------------------------------"
echo "VANGUARD BRIDGE: BOOTSTRAP SEQUENCE INITIATED"
echo "------------------------------------------------"

# 1. Directory Setup
INSTALL_DIR="vanguard-bridge-dev"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"
echo "[1/5] Created directory: $INSTALL_DIR"

# 2. Extracting Files (Heredocs)
echo "[2/5] Extracting component files..."

# --- VANGUARD PROXY ---
cat << 'EOF' > vanguard_proxy.py
import sys
import json
import http.server
import socketserver
import urllib.request
import os
import re
import time
import traceback

# --- Configuration & Routing ---

class Config:
    def __init__(self, path="vanguard_config.json"):
        self.path = path
        self.last_loaded = 0
        self.data = {}
        self.load()

    def load(self):
        try:
            if not os.path.exists(self.path): return False
            mtime = os.path.getmtime(self.path)
            if mtime > self.last_loaded:
                with open(self.path, 'r') as f:
                    config_str = f.read()
                
                # Robust env var substitution
                def inject_env(match):
                    env_var = match.group(1)
                    val = os.environ.get(env_var, f"MISSING_{env_var}")
                    return val

                config_str = re.sub(r"\$\{(\w+)\}", inject_env, config_str)
                self.data = json.loads(config_str)
                self.last_loaded = mtime
                return True
        except Exception as e:
            print(f"[ERROR] Config load failed: {e}")
        return False

    def get_active_profile(self):
        name = self.data.get("active_profile", "default")
        return self.data.get("profiles", {}).get(name, {})

GLOBAL_CONFIG = Config()

def detect_role(req_json):
    messages = req_json.get("messages", [])
    system_prompt = next((m["content"] for m in messages if m.get("role") == "system"), "")
    full_text = str(system_prompt) + " " + " ".join([m.get("content", "") for m in messages if isinstance(m.get("content"), str)])
    if "architect" in full_text.lower(): return "architect"
    if "auditor" in full_text.lower(): return "auditor"
    if "lead-dev" in full_text.lower(): return "lead-dev"
    return "default"

def resolve_route(req_json):
    GLOBAL_CONFIG.load()
    profile = GLOBAL_CONFIG.get_active_profile()
    requested_model = req_json.get("model", "claude-3-5-sonnet-latest")
    if "/" in requested_model: requested_model = requested_model.split("/")[-1]
    role = detect_role(req_json)
    
    role_overrides = profile.get("role_overrides", {})
    if role in role_overrides:
        override = role_overrides[role]
        backend_name = override["backend"]
        model_name = override["model"]
        target_model = profile.get("model_map", {}).get(model_name, model_name)
        return backend_name, target_model, f"Role Override ({role})"
    
    model_map = profile.get("model_map", {})
    if requested_model in model_map:
        target_model = model_map[requested_model]
        backend_name = "openrouter" if "/" in target_model else GLOBAL_CONFIG.data.get("routing", {}).get("default_backend", "local")
        return backend_name, target_model, "Profile Mapping"
        
    global_routing = GLOBAL_CONFIG.data.get("routing", {})
    return global_routing.get("default_backend", "local"), requested_model, "Global Default"

# --- Payload Translation ---

def anthropic_to_openai(req_json, target_model):
    openai_msgs = []
    system_prompt = req_json.get("system")
    if system_prompt:
        if isinstance(system_prompt, list):
            system_prompt = " ".join([p.get("text", "") for p in system_prompt if p.get("type") == "text"])
        openai_msgs.append({"role": "system", "content": system_prompt})

    for m in req_json.get("messages", []):
        role = m.get("role")
        content = m.get("content", "")
        if role == "system":
            openai_msgs.append({"role": "system", "content": content})
            continue

        if isinstance(content, str):
            openai_msgs.append({"role": role, "content": content})
        elif isinstance(content, list):
            text_parts = []
            tool_calls = []
            for block in content:
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    tool_calls.append({
                        "id": block["id"],
                        "type": "function",
                        "function": {"name": block["name"], "arguments": json.dumps(block["input"])}
                    })
                elif block.get("type") == "tool_result":
                    openai_msgs.append({"role": "tool", "tool_call_id": block["tool_use_id"], "content": str(block.get("content", ""))})
            
            full_text = " ".join(text_parts).strip()
            if role == "assistant":
                msg = {"role": "assistant", "content": full_text if full_text or not tool_calls else None}
                if tool_calls: msg["tool_calls"] = tool_calls
                openai_msgs.append(msg)
            elif role == "user" and full_text:
                openai_msgs.append({"role": "user", "content": full_text})
        
    openai_req = {"model": target_model, "messages": openai_msgs, "stream": req_json.get("stream", False), "temperature": req_json.get("temperature", 0.7)}
    if "tools" in req_json:
        openai_tools = []
        for tool in req_json["tools"]:
            openai_tools.append({"type": "function", "function": {"name": tool["name"], "description": tool.get("description", ""), "parameters": tool.get("input_schema", {})}})
        openai_req["tools"] = openai_tools
    return openai_req

def openai_to_anthropic(resp_json):
    choice = resp_json["choices"][0]
    message = choice["message"]
    content = []
    text_content = message.get("content") or ""
    
    # --- Robust Tool Parsing (Fix for Local Models) ---
    tools_parsed = []
    # Identify [TOOL_CALLS]Agent<SPECIAL_32>... pattern
    pattern = r"\[TOOL_CALLS\](.*?)(?=\[TOOL_CALLS\]|$)"
    matches = re.findall(pattern, text_content)
    
    for match in matches:
        try:
            # Handle the 'Agent<SPECIAL_32>' or tool name prefix
            json_str = re.sub(r"^\w+(<.*?>)?", "", match).strip()
            tool_name_match = re.match(r"^(\w+)", match)
            # Default to 'Agent' if the tag looks like 'Agent<SPECIAL_32>'
            tool_name = "Agent" if "Agent" in match else (tool_name_match.group(1) if tool_name_match else "unknown")
            
            args = json.loads(json_str)
            tools_parsed.append({
                "type": "tool_use",
                "id": "tc_txt_" + str(int(time.time() * 1000 % 100000)),
                "name": tool_name,
                "input": args
            })
            # Clean text of the tag
            text_content = text_content.replace(f"[TOOL_CALLS]{match}", "").strip()
        except: pass

    if text_content:
        content.append({"type": "text", "text": text_content})
    
    # Standard tool_calls field
    if "tool_calls" in message:
        for tc in message["tool_calls"]:
            try:
                args = json.loads(tc["function"]["arguments"])
                content.append({"type": "tool_use", "id": tc.get("id", "call_" + str(int(time.time()))), "name": tc["function"]["name"], "input": args})
            except: pass 
            
    content.extend(tools_parsed)

    return {
        "id": resp_json.get("id", "msg_local_" + str(int(time.time()))),
        "type": "message",
        "role": "assistant",
        "model": resp_json.get("model", "unknown"),
        "content": content,
        "stop_reason": "tool_use" if ("tool_calls" in message or tools_parsed) else (choice.get("finish_reason") or "end_turn"),
        "usage": {"input_tokens": resp_json.get("usage", {}).get("prompt_tokens", 0), "output_tokens": resp_json.get("usage", {}).get("completion_tokens", 0)}
    }

# --- SSE / Streaming Logic ---

def transform_openai_chunk_to_anthropic(line):
    if not line.startswith("data: "): return None
    data_str = line[6:].strip()
    if data_str == "[DONE]": return "event: message_stop\ndata: {\"type\": \"message_stop\"}\n\n"
    try:
        chunk = json.loads(data_str)
        delta = chunk["choices"][0]["delta"]
        if "content" in delta:
            return f"event: content_block_delta\ndata: {json.dumps({'type': 'content_block_delta', 'index': 0, 'delta': {'type': 'text_delta', 'text': delta['content']}})}\n\n"
        if "role" in delta:
            return f"event: message_start\ndata: {json.dumps({'type': 'message_start', 'message': {'id': chunk.get('id', 'msg_000'), 'type': 'message', 'role': 'assistant', 'model': chunk.get('model', 'unknown'), 'content': [], 'usage': {'input_tokens': 0, 'output_tokens': 0}}})}\n\n"
    except: pass
    return None

class VanguardProxy(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): print(f"[HTTP] {format % args}")
    def do_GET(self):
        if self.path.endswith("/models"):
            vanguard_models = [{"id": "anthropic/claude-3-5-sonnet-latest", "object": "model"}, {"id": "anthropic/claude-3-5-haiku-latest", "object": "model"}]
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps({"data": vanguard_models}).encode('utf-8')); return
        self.send_response(404); self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        req_json = json.loads(post_data)
        backend_name, target_model, reason = resolve_route(req_json)
        backend = GLOBAL_CONFIG.data["backends"].get(backend_name)
        
        openai_req_data = anthropic_to_openai(req_json, target_model)
        headers = {"Content-Type": "application/json", "X-Title": "Vanguard Bridge"}
        if backend.get("api_key") and "${" not in backend["api_key"]: headers["Authorization"] = f"Bearer {backend['api_key']}"

        target_url = f"{backend['url']}/chat/completions"
        req = urllib.request.Request(target_url, data=json.dumps(openai_req_data).encode('utf-8'), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                if req_json.get("stream"):
                    self.send_response(200); self.send_header('Content-Type', 'text/event-stream'); self.end_headers()
                    while True:
                        line = response.readline()
                        if not line: break
                        evt = transform_openai_chunk_to_anthropic(line.decode('utf-8'))
                        if evt: self.wfile.write(evt.encode('utf-8')); self.wfile.flush()
                else:
                    anthropic_resp = openai_to_anthropic(json.loads(response.read()))
                    self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers()
                    self.wfile.write(json.dumps(anthropic_resp).encode('utf-8'))
        except Exception as e:
            traceback.print_exc()
            self.send_response(500); self.end_headers(); self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

if __name__ == "__main__":
    PROXY_PORT = 8080
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PROXY_PORT), VanguardProxy) as httpd:
        print(f"VANGUARD BRIDGE ACTIVE ON LOCALHOST (PORT {PROXY_PORT})")
        httpd.serve_forever()
EOF

# --- VANGUARD MCP ---
cat << 'EOF' > vanguard_mcp.py
import sys, json, urllib.request, os
WINDOWS_IP = os.environ.get("WINDOWS_IP", "127.0.0.1")
ENDPOINT = f"http://{WINDOWS_IP}:1234/v1"
MODELS = {"auditor": "nemotron-cascade-2-30b-a3b-i1", "architect": "qwen/qwen3.5-35b-a3b"}
def call_local_model(model_key, prompt):
    url = f"{ENDPOINT}/chat/completions"
    data = {"model": MODELS.get(model_key), "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), method="POST")
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())['choices'][0]['message']['content']
    except Exception as e: return f"Error: {e}"
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "schema":
        schema = [{"name": "ask_auditor", "description": "Consult Auditor specialist", "input_schema": {"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]}}, {"name": "ask_architect", "description": "Consult Architect specialist", "input_schema": {"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]}}]
        print(json.dumps(schema)); return
    try:
        req = json.loads(sys.stdin.read())
        method, params = req.get("method"), req.get("params", {})
        if method == "ask_auditor": result = call_local_model("auditor", params.get("prompt"))
        elif method == "ask_architect": result = call_local_model("architect", params.get("prompt"))
        else: result = f"Unknown tool: {method}"
        print(json.dumps({"result": result}))
    except Exception as e: print(json.dumps({"error": str(e)}))
if __name__ == "__main__": main()
EOF

# --- CONFIG ---
cat << 'EOF' > vanguard_config.json
{
  "active_profile": "coding-power",
  "backends": {
    "local": { "type": "openai", "url": "http://127.0.0.1:1234/v1", "api_key": "not-needed" },
    "openrouter": { "type": "openai", "url": "https://openrouter.ai/api/v1", "api_key": "${OPENROUTER_API_KEY}" }
  },
  "profiles": {
    "coding-power": {
      "description": "Cloud-heavy coding",
      "model_map": {
        "claude-3-5-sonnet-latest": "qwen/qwen-3-coder-480b-a35b:free",
        "claude-3-5-haiku-latest": "anthropic/claude-3-5-haiku-latest"
      },
      "role_overrides": {
        "auditor": { "backend": "openrouter", "model": "claude-3-5-sonnet-latest" }
      }
    }
  },
  "tools": {
    "claude": { "command": "claude", "model_arg": "--model", "default_virtual_model": "claude-3-5-sonnet-latest" },
    "opencode": { "command": "opencode", "model_arg": "--model", "default_virtual_model": "claude-3-5-haiku-latest" }
  }
}
EOF

# --- LAUNCHER ---
cat << 'EOF' > local_launch.sh
#!/bin/bash
export ANTHROPIC_BASE_URL="http://127.0.0.1:8080"
export ANTHROPIC_API_KEY="vanguard-bridge-dev"
[ -f .env ] && export $(grep -v '^#' .env | xargs)
python3 vanguard_proxy.py &
PROXY_PID=$!
sleep 2
echo "Vanguard Bridge Running (PID: $PROXY_PID). Launching tool..."
# Default to claude if no arg provided
TOOL=${1:-claude}
claude --model claude-3-5-sonnet-latest
kill $PROXY_PID
EOF
chmod +x local_launch.sh

# 3. Environment & Dependencies
echo "[3/5] Verifying system dependencies..."
if ! command -v python3 &> /dev/null; then echo "ERROR: Python 3 not found!"; exit 1; fi
if ! command -v npm &> /dev/null; then echo "WARNING: npm not found. You may need it for Claude Code."; fi

# 4. API Key Setup
if [ ! -f .env ]; then
    echo "[4/5] Configuration Required:"
    read -p "Enter your OPENROUTER_API_KEY: " OR_KEY
    echo "OPENROUTER_API_KEY=$OR_KEY" > .env
    chmod 600 .env
    echo ".env file created with restricted permissions (chmod 600)."
fi

# 5. Success
echo "------------------------------------------------"
echo "[5/5] VANGUARD BRIDGE SETUP COMPLETE!"
echo "------------------------------------------------"
echo "To starting coding, simply run:"
echo "  ./local_launch.sh"
echo "------------------------------------------------"
