import re
import requests
import base64
import hashlib
import json
from datetime import datetime, timezone
from urllib.parse import quote, quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from yaml import safe_load

class GitLabManager:
    branch_roles = {
        "production": "main",
        "staging": "staging",
        "development": "dev"
    }
  
        
    def __init__(
        self,
        aic_instance,
        gitlab_token,
        gitlab_namespace,
        repo_folder,
        gitlab_base_url: str = "https://git.autodatacorp.org/api/v4",
        use_hash_comparison: bool = True,
        email_recipients: list = None,
        email_sender: str = None,
        mapping_file: str = "branch_to_workspace.yaml"
    ):
        """
        Initialize GitLabManager.

        - aic_instance: instance of AIC (provides .workspace, .pipeline_configs, .pipelines, .write_config_to_pipeline, etc.)
        - gitlab_token: personal access token for GitLab
        - gitlab_namespace: e.g. "pin/pin-analytics/pin-fusion-2.0"
        - repo_folder: e.g. "jobs"
        - use_hash_comparison: whether to skip files whose content hash matches existing
        - email_recipients/email_sender: if set, summaries will be emailed (via pyspark_utils.send_email)
        - mapping_file: path to YAML file (in repo) mapping branches to workspaces
        """
        self.aic = aic_instance
        self.gitlab_base = gitlab_base_url.rstrip('/')
        self.gitlab_token = gitlab_token
        self.use_hash_comparison = use_hash_comparison
        self.headers = {
            'Private-Token': self.gitlab_token,
            'Content-Type': 'application/json'
        }
        self.gitlab_namespace = gitlab_namespace.rstrip('/')
        self.repo_folder = repo_folder

        raw = f"{self.gitlab_namespace}/{self.repo_folder}"
        self.project_path = quote(raw, safe='')

        # ── Fetch project to get default_branch, but catch 404 for "not found" ──
        try:
            resp = requests.get(
                f"{self.gitlab_base}/projects/{self.project_path}",
                headers=self.headers,
                timeout=30
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status = getattr(e.response, 'status_code', None)
            if status == 404:
                raise RuntimeError(
                    f"❌ GitLab project '{self.gitlab_namespace}/{self.repo_folder}' not found. "
                    "Please check that your namespace and repo_folder are correct."
                ) from e
            raise  # re-raise any other HTTP errors

        api_def = resp.json().get('default_branch')
        if not api_def:
            raise RuntimeError(f"GitLab returned no default_branch for project '{self.project_path}'.")
        self.default_branch = api_def

        # Build mapper (always fetch mapping file from default_branch)
        self.mapper = BranchWorkspaceMapper(self, mapping_file)

        try:
            self._branch = self.mapper.workspace_to_branch(self.aic.workspace)
        except KeyError:
            # No mapping: slugify workspace
            slug = self._slugify(self.aic.workspace)
            print(f"⚠️  No mapping for workspace '{self.aic.workspace}', using slug '{slug}'.")
            self._branch = slug

        # Ensure the chosen branch exists
        self.ensure_branch_exists(branch_name=self._branch, ref=self.default_branch)

        # Email settings
        if email_recipients:
            if not email_sender:
                raise ValueError("When specifying email_recipients, email_sender must be provided.")
        self.email_recipients = email_recipients
        self.email_sender = email_sender
        slug = self._slugify(self.aic.workspace)
        try:
            mapped = self.mapper.workspace_to_branch(self.aic.workspace)
        except KeyError:
            mapped = slug
        self._allowed_push = {slug, mapped}
        self._hotfix_prefixes = ['hotfix/']
        self.check_token_expiration()
        
        # Lock the instance at the very end
        self._initialized = True
        
    def __setattr__(self, name, value):
        """Prevent modification of attributes after initialization"""
        # During initialization, allow normal attribute setting
        if not hasattr(self, '_initialized'):
            super().__setattr__(name, value)
            return

        # Allow internal branch operation flag to be set at any time
        if name == '_in_branch_operation':
            super().__setattr__(name, value)
            return

        # After initialization, only allow specific controlled changes
        if name == '_branch' and hasattr(self, '_in_branch_operation'):
            super().__setattr__(name, value)
            return

        # Block all other attribute modifications
        raise RuntimeError(
            f"❌ Cannot modify attribute '{name}' after initialization. "
            "Use create_feature_branch(), create_release_branch(), or create_hotfix_branch() to change branches."
        )

    def _set_branch(self, new_branch: str):
        """Internal method to safely change branch during controlled operations"""
        self._in_branch_operation = True
        try:
            self._branch = new_branch
        finally:
            delattr(self, '_in_branch_operation')

    @property
    def branch(self) -> str:
        """Current branch (read-only)"""
        return self._branch

    def _slugify(self, text: str) -> str:
        """Convert text to a URL‐safe slug."""
        return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    
    def get_token_expiration_date(self):
        """
        Retrieves the expiration date of the current GitLab token.
        Returns None if expiration cannot be determined.
        """
        try:
            # First, validate the token works by getting user info
            user_url = f"{self.gitlab_base}/user"
            user_response = requests.get(user_url, headers=self.headers, timeout=30)
            user_response.raise_for_status()

            user_info = user_response.json()
            username = user_info.get('username', 'Unknown')

            # Try to get personal access tokens
            tokens_url = f"{self.gitlab_base}/personal_access_tokens"
            tokens_response = requests.get(tokens_url, headers=self.headers, timeout=30)

            if tokens_response.status_code == 200:
                tokens = tokens_response.json()

                # Find active tokens with expiration dates
                active_tokens_with_expiry = []
                for token in tokens:
                    if token.get('revoked', True):
                        continue

                    exp_str = token.get('expires_at')
                    if not exp_str:
                        continue

                    try:
                        # Handle both date formats GitLab might return
                        if 'T' in exp_str:
                            exp_date = datetime.strptime(exp_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                        else:
                            exp_date = datetime.strptime(exp_str, '%Y-%m-%d')

                        active_tokens_with_expiry.append({
                            'name': token.get('name', 'Unnamed'),
                            'expires_at': exp_date,
                            'scopes': token.get('scopes', [])
                        })
                    except ValueError as e:
                        continue

                if active_tokens_with_expiry:
                    # Sort by expiration date (soonest first)
                    active_tokens_with_expiry.sort(key=lambda x: x['expires_at'])

                    # Return the soonest expiring token
                    # (assumption: user is likely using their most recent/soon-to-expire token)
                    token_info = active_tokens_with_expiry[0]
                    print(f"Checking expiration for token: '{token_info['name']}'")
                    return token_info['expires_at']
                else:
                    print(f"✅ Token valid for user '{username}' but no expiration date found")
                    return None
            else:
                print(f"✅ Token valid for user '{username}' but cannot access token list")
                return None

        except requests.exceptions.RequestException as err:
            print(f"Error checking token: {err}")
            return None

    def check_token_expiration(self, warning_threshold_days: int = 30):
        """Checks and validates the current GitLab token."""
        exp = self.get_token_expiration_date()

        if not exp:
            print("⚠️  Token is valid but expiration date could not be determined.")
            return

        # Calculate days until expiration
        now = datetime.now(timezone.utc) if exp.tzinfo else datetime.utcnow()
        delta = exp - now
        days_left = delta.days

        if days_left < 0:
            print("❌ GitLab Token has expired!")
        elif days_left <= warning_threshold_days:
            print(f"⚠️  GitLab Token expires in {days_left} days (≤ {warning_threshold_days} day warning threshold).")
        else:
            print(f"✅ GitLab Token is valid for another {days_left} days.")

    def generate_hash(self, content):
        """MD5 hash of normalized content."""
        norm = content.strip().replace('\r\n', '\n').replace('\r', '\n')
        return hashlib.md5(norm.encode('utf-8')).hexdigest()

    def repository_exists(self, repo_path):
        """Check if a repository exists in GitLab."""
        url = f"{self.gitlab_base}/projects/{repo_path.replace('/', '%2F')}"
        r = requests.get(url, headers=self.headers, timeout=30)
        return r.status_code == 200

    def create_repository(self, repo_name):
        """Create a new repo under the configured subgroup."""
        url = f"{self.gitlab_base}/projects"
        data = {
            'name': repo_name,
            'namespace_id': self.get_subgroup_id(),
            'visibility': 'private'
        }
        r = requests.post(url, headers=self.headers, json=data, timeout=30)
        if r.status_code == 201:
            return r.json()
        print(f"Failed to create repo {repo_name}: {r.status_code} {r.text}")
        return None

    def get_existing_file_content(self, repo_name, file_name):
        """
        Fetch base64‐encoded content for file_name in repo_name.
        Checks both self._branch and self.default_branch.
        """
        repo = quote(repo_name, safe='')
        path = quote(file_name, safe='')
        for ref in (self._branch, self.default_branch):
            url = f"{self.gitlab_base}/projects/{repo}/repository/files/{path}"
            resp = requests.get(url, headers=self.headers, params={'ref': ref}, timeout=30)
            if resp.status_code == 200:
                enc = resp.json().get('content')
                return base64.b64decode(enc).decode('utf-8') if enc else None
            elif resp.status_code == 404:
                continue
            else:
                resp.raise_for_status()
        return None

    def ensure_branch_exists(self, branch_name: str = None, ref: str = None):
        """
        Create branch `branch_name` off `ref`. If branch already exists, do nothing.
        """
        branch = branch_name or self._branch
        base_ref = ref or self.default_branch

        proj = self.project_path
        enc_branch = quote(branch, safe='')
        enc_ref = quote_plus(base_ref)

        url_check = f"{self.gitlab_base}/projects/{proj}/repository/branches/{enc_branch}"
        r = requests.get(url_check, headers=self.headers, timeout=30)
        if r.status_code == 200:
            print(f"Using existing branch '{branch}'")
            return
        if r.status_code != 404:
            r.raise_for_status()

        # Branch does not exist; create it
        create_url = (
            f"{self.gitlab_base}/projects/{proj}/repository/branches"
            f"?branch={enc_branch}&ref={enc_ref}"
        )
        c = requests.post(create_url, headers=self.headers, timeout=30)
        if c.status_code in (201, 409):
            print(f"Branch '{branch}' is now present (created or already existed).")
            return

        follow = requests.get(url_check, headers=self.headers, timeout=30)
        if follow.status_code == 200:
            print(f"Branch '{branch}' is now present (post‐check).")
        else:
            raise RuntimeError(
                f"Unable to create branch '{branch}' off '{base_ref}'. "
                "Please create it manually in GitLab."
            )

    def delete_file(self, file_name, branch=None):
        """Remove a file from the specified branch."""
        branch = branch or self._branch
        proj = self.project_path.replace('/', '%2F')
        r = requests.delete(
            f"{self.gitlab_base}/projects/{proj}/repository/files/{quote(file_name, safe='')}",
            headers=self.headers,
            params={
                'branch': branch,
                'commit_message': f"Remove {file_name} – {datetime.now():%Y-%m-%d}"
            },
            timeout=30
        )
        if r.status_code == 204:
            return  # success, silently return
        elif r.status_code == 404:
            raise RuntimeError(f"404: {file_name} not found on branch '{branch}'")
        else:
            raise RuntimeError(f"Delete failed ({r.status_code}): {r.text}")

    def list_pipeline_files(self, subpath: str = None) -> list[str]:
        """
        List all .json files in the current self._branch under 'subpath'.
        Supports pagination (per_page=100).
        If the path/branch doesn't exist yet (404), returns [].
        """
        proj = self.project_path.replace('/', '%2F')
        page = 1
        per_page = 100
        all_files: list[str] = []

        while True:
            params: dict = {
                'ref': self._branch,
                'per_page': per_page,
                'page': page
            }
            if subpath:
                params['path'] = subpath

            url = f"{self.gitlab_base}/projects/{proj}/repository/tree"
            resp = requests.get(
                url,
                headers={'PRIVATE-TOKEN': self.gitlab_token},
                params=params,
                timeout=30
            )

            # If the folder or branch doesn't exist yet, just return empty
            if resp.status_code == 404:
                return []

            resp.raise_for_status()
            items = resp.json()
            if not items:
                break

            for item in items:
                if item.get('type') == 'blob' and item.get('name', '').lower().endswith('.json'):
                    all_files.append(item['name'])

            if len(items) < per_page:
                break
            page += 1

        return all_files

    def fetch_pipeline_config(self, pipeline: dict) -> dict:
        """
        Fetch the full JSON "jobConfig" for a single pipeline.

        Args:
          pipeline: a dict with keys 'name' and '$id' or 'id'.

        Returns a dict of the form:
          {
            'name': <pipeline name>,
            'id':   <pipeline id>,
            'jobConfig': <the JSON config from AIC>
          }
        """
        job_id = pipeline.get('id') or pipeline.get('$id')
        if not job_id:
            raise ValueError(f"No id found for pipeline {pipeline!r}")

        url = (
            f"{self.base_url}/projects/{self.project_id}"
            f"/workspaces/{self.workspace_id}/jobs/{job_id}"
        )
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        cfg = resp.json()

        return {
            'name': pipeline['name'],
            'id':   job_id,
            'jobConfig': cfg
        }

    def _send_email(self, subject, body, cc=None, bcc=None, attachments=None, testing=True):
        """
        If email_recipients was provided at init, send summary email via pyspark_utils.send_email.
        """
        if not self.email_recipients:
            return
        import pyspark_utils
        pyspark_utils.send_email(
            sender=self.email_sender,
            to=self.email_recipients,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            testing=testing
        )

    def _format_push_summary(self, branch, results):
        """
        Build subject and HTML body for push_pipelines summary.
        `results` is a list of tuples: (pipeline_name, status, message).
        """
        rows = ''.join([
            f"<tr><td>{name}</td><td>{status}</td><td>{msg}</td></tr>"
            for name, status, msg in results
        ])
        subject = f"[Push] GitLab Sync Results for {branch}"
        body = f"""
        <html><body>
          <h2>Pipeline Push Summary</h2>
          <p>Branch: <strong>{branch}</strong></p>
          <table border='1'>
            <tr><th>Pipeline</th><th>Status</th><th>Details</th></tr>
            {rows}
          </table>
          <p>Timestamp: {datetime.now(timezone.utc).isoformat()} UTC</p>
        </body></html>
        """
        return subject, body

    def _format_deploy_summary(self, branch, results):
        """
        Build subject and HTML body for deploy_pipelines summary.
        `results` is a list of tuples: (pipeline_name, status, message).
        """
        rows = ''.join([
            f"<tr><td>{name}</td><td>{status}</td><td>{msg}</td></tr>"
            for name, status, msg in results
        ])
        subject = f"[Deploy] GitLab Deployment Summary for {branch}"
        body = f"""
        <html><body>
          <h2>Pipeline Deploy Summary</h2>
          <p>Branch: <strong>{branch}</strong></p>
          <table border='1'>
            <tr><th>Pipeline</th><th>Status</th><th>Details</th></tr>
            {rows}
          </table>
          <p>Timestamp: {datetime.now(timezone.utc).isoformat()} UTC</p>
        </body></html>
        """
        return subject, body

    def _extract_and_push_code(self, pipeline_name: str, job_config: dict):
        """
        Scan `job_config` for any PYSPARK or SQL tasks.
        - For PYSPARK: push each .py and extract any triple-quoted blocks that look like SQL.
        - For SQL: push the raw query as a .sql.
        """
        proj = self.project_path.replace('/', '%2F')

        def _find_all_tasks(obj):
            if isinstance(obj, dict):
                if "tasks" in obj and isinstance(obj["tasks"], list):
                    for t in obj["tasks"]:
                        yield t
                for v in obj.values():
                    yield from _find_all_tasks(v)
            elif isinstance(obj, list):
                for item in obj:
                    yield from _find_all_tasks(item)

        for task in _find_all_tasks(job_config):
            if not isinstance(task, dict):
                continue

            task_type = task.get("type", "").upper()
            if task_type not in ("PYSPARK", "SQL"):
                continue

            cfg = task.get("config", {})
            task_id = task.get("id") or "unknown_id"
            base_folder = f"code/{pipeline_name}"

            if task_type == "PYSPARK":
                script = cfg.get("script")
                if not script:
                    continue

                # Push the full PySpark script
                py_filename = f"{base_folder}/{task_id}.py"
                self._push_file(proj, py_filename, script, branch=self._branch)

                # Extract triple-quoted SQL blocks
                pattern = re.compile(r"'''(.*?)'''|\"\"\"(.*?)\"\"\"", re.DOTALL)
                matches = pattern.findall(script)
                for idx, m in enumerate(matches, start=1):
                    sql_block = m[0] if m[0] else m[1]
                    stripped = sql_block.strip()
                    first_word = stripped.split(None, 1)[0].lower() if stripped else ""
                    if first_word not in {
                        "select", "insert", "update", "delete",
                        "with", "create", "drop", "alter", "merge"
                    }:
                        continue
                    sql_filename = f"{base_folder}/{task_id}_{idx}.sql"
                    self._push_file(proj, sql_filename, stripped, branch=self._branch)

            else:  # task_type == "SQL"
                sql_text = cfg.get("query") or cfg.get("script") or cfg.get("sql")
                if not sql_text:
                    continue
                sql_filename = f"{base_folder}/{task_id}.sql"
                self._push_file(proj, sql_filename, sql_text.strip(), branch=self._branch)

    def push_to_git(self):
        """
        Push pipeline JSON and code to GitLab, but prevent accidental pushes to production ('main') unless forced.
        """
        
        if self._branch == self.default_branch:
            force_push = input('⚠️  WARNING: You are attempting to overwrite the Production branch with existing AIC code. Proceed? (y/n)')
            if force_push.lower() != 'y':
                raise ValueError('Production Push refused. Exiting.')
                
        # Guard: only allow pushes on configured branches or hotfix prefixes
        if (
            self._branch not in self._allowed_push
            and not any(self._branch.startswith(pref) for pref in self._hotfix_prefixes)
        ):
            raise RuntimeError(
                f"❌ Cannot push to branch '{self._branch}'.\n"
                f"Allowed push branches: {sorted(self._allowed_push)}\n"
                f"Allowed hotfix prefixes: {self._hotfix_prefixes}\n"
            )

        # Ensure branch exists
        self.ensure_branch_exists(branch_name=self._branch, ref=self._branch)
        proj    = self.project_path.replace('/', '%2F')
        results = []

        # PASS 1: Push JSON
        for cfg in self.aic.pipeline_configs:
            name    = cfg['name']
            fn      = f"config/{name}.json"
            content = json.dumps(cfg['jobConfig'], indent=2)
            print(f"Pushing JSON for pipeline '{name}' → {fn}")
            try:
                self._push_file(proj, fn, content, branch=self._branch)
                results.append((name, 'Success', 'JSON Pushed'))
            except Exception as e:
                results.append((name, 'Failure', f"JSON push failed: {e}"))

        # PASS 2: Push code
        for cfg in self.aic.pipeline_configs:
            name   = cfg['name']
            status = next((r[1] for r in results if r[0] == name), None)
            if status != 'Success':
                continue
            try:
                self._extract_and_push_code(name, cfg['jobConfig'])
            except Exception as e:
                results.append((name, 'Failure', f"Code extraction failed: {e}"))

        # Summary email
        subj, body = self._format_push_summary(self._branch, results)
        self._send_email(subj, body, testing=False)

    def _push_file(self, proj_encoded, file_name, file_content, branch):
        """
        Create or update `file_name` on `branch`.
        """
        url = f"{self.gitlab_base}/projects/{proj_encoded}/repository/files/{quote(file_name, safe='')}"
        payload = {
            'branch': branch,
            'content': file_content,
            'commit_message': f"Sync {file_name} – {datetime.now():%Y-%m-%d}"
        }

        r = requests.post(url, headers=self.headers, json=payload, timeout=30)
        if r.status_code == 201:
            print(f"Created {file_name} on branch '{branch}'")
            return

        if r.status_code in (400, 409):
            r2 = requests.put(url, headers=self.headers, json=payload, timeout=30)
            if r2.status_code == 200:
                print(f"Updated {file_name} on branch '{branch}'")
                return

        raise RuntimeError(f"Write failed: {r.status_code} {r.text}")

    def deploy_pipelines(self):
        """
        Deploy only pipelines listed in self.aic.pipeline_configs to AIC. 
        """

        try:
            mapped_ws = self.mapper.lookup(self._branch)
        except KeyError:
            raise RuntimeError(
                f"❌ Branch '{self._branch}' is not mapped to any workspace; refusing to deploy."
            )
        if mapped_ws != self.aic.workspace:
            raise RuntimeError(
                f"❌ Branch '{self._branch}' maps to workspace '{mapped_ws}', not '{self.aic.workspace}'."
            )

        # 2) Enforce branch naming style
        slug = self._slugify(self.aic.workspace)

        # 1) Validate branch→workspace
        if mapped_ws.strip().lower() != self.aic.workspace.strip().lower():
            raise RuntimeError(
                f"❌ Branch '{self._branch}' maps to workspace '{mapped_ws}', not '{self.aic.workspace}'."
            )

        # 3) Ensure branch exists
        self.ensure_branch_exists(branch_name=self._branch, ref=self._branch)

        proj    = self.project_path.replace('/', '%2F')
        results = []

        # Always use current pipeline_configs
        for cfg in self.aic.pipeline_configs:
            name = cfg['name']
            full_path = f"config/{name}.json"
            try:
                print(f"Fetching updated JSON for pipeline '{name}' from {full_path}")
                raw = self.fetch_pipeline_file(full_path)
                new = json.loads(raw)
                old_blob = json.dumps(cfg['jobConfig'], sort_keys=True)
                new_blob = json.dumps(new, sort_keys=True)
                if self.use_hash_comparison and self.generate_hash(old_blob) == self.generate_hash(new_blob):
                    print(f"No changes detected for {name}; skipping deployment.")
                    results.append((name, 'Skipped', 'No change'))
                    continue
                cfg['jobConfig'] = new
                print(f" → Updating existing pipeline '{name}' (id={cfg['id']}) in AIC")
                self.aic.write_config_to_pipeline({
                    'name':      name,
                    'jobConfig': new,
                    'id':        cfg['id']
                })
                results.append((name, 'Success', 'Updated'))
            except Exception as e:
                print(f"❌ Failed to update '{name}': {e}")
                results.append((name, 'Failure', str(e)))

        # Summary email
        subj, body = self._format_deploy_summary(self._branch, results)
        self._send_email(subj, body, testing=False)

    def fetch_pipeline_file(self, full_path: str, ref: str = None) -> str:
        """
        Fetch raw content of a file at `full_path` (e.g. "branch_to_workspace.yaml"):

        - If `ref` is provided, only try that branch.
        - Otherwise fall back to self._branch then self.default_branch.

        Returns the file's text, or raises FileNotFoundError.
        """
        # if a single ref was specified, only try that; else try current branch then default
        refs = ( (ref,) if ref else (self._branch, self.default_branch) )

        for branch_ref in refs:
            url = (
                f"{self.gitlab_base}/projects/{self.project_path}"
                f"/repository/files/{quote(full_path, safe='')}/raw"
            )
            resp = requests.get(
                url,
                headers={ 'PRIVATE-TOKEN': self.gitlab_token },
                params={ 'ref': branch_ref },
                timeout=30
            )
            if resp.status_code == 200:
                # only log when not coming from default_branch
                if branch_ref != self.default_branch:
                    print(f"Fetched '{full_path}' from '{branch_ref}'")
                return resp.text
            elif resp.status_code == 404:
                continue
            else:
                resp.raise_for_status()

        raise FileNotFoundError(
            f"'{full_path}' not found on {', '.join(refs)}"
        )
        
    def create_release_branch(self, branch_name: str):
        """
        1) Only allow cutting a release from the staging branch.
        2) Create (if needed) a new GitLab branch named 'release/{branch_name}'
           off the staging branch.
        3) Switch self._branch to that new branch.
        4) Under 'config/', delete every JSON whose pipeline‐name is NOT in
           self.aic.pipeline_configs.  Under 'code/', delete every file under any
           "code/<PIPELINE>" folder where <PIPELINE> is not in that allowed set.
        """
        staging_branch = self.branch_roles["staging"]
        # ── 0) Enforce that current branch is the staging branch ──
        if self._branch != staging_branch:
            raise RuntimeError(
                f"❌ Release branches can only be created from '{staging_branch}' (current branch is '{self._branch}')."
            )

        # ── A) Build set of allowed pipeline names ──
        allowed_pipelines = {cfg["name"] for cfg in self.aic.pipeline_configs}

        # ── B) Derive new release branch slug ──
        release_branch = f"release/{branch_name}"
        slug = re.sub(r'[^A-Za-z0-9\-_\/]+', "-", release_branch)

        # ── C) Create or confirm the new branch off staging ──
        try:
            self.ensure_branch_exists(branch_name=slug, ref=staging_branch)
        except RuntimeError as e:
            msg = str(e).lower()
            if "already existed" in msg or ("branch" in msg and "already" in msg):
                print(f"ℹ️  Branch '{slug}' already exists; continuing.")
            else:
                raise

        # ── D) Switch self._branch to new release branch ──
        self._set_branch(slug)
        print(f'Checked out {slug} branch')
        # ── E) Figure out which config JSONs to delete ──
        to_delete = []
        for fn in self.list_pipeline_files(subpath="config"):
            pname = fn[:-5]
            if pname not in allowed_pipelines:
                to_delete.append(f"config/{fn}")

        # ── F) Figure out which code blobs to delete ──
        proj = self.project_path.replace('/', '%2F')
        tree = requests.get(
            f"{self.gitlab_base}/projects/{proj}/repository/tree",
            headers={'PRIVATE-TOKEN': self.gitlab_token},
            params={'ref': self._branch, 'path': 'code', 'per_page': 100},
            timeout=30
        ).json()

        for entry in tree:
            if isinstance(entry, dict) and entry.get('type') == "tree" and entry.get('name') not in allowed_pipelines:
                for blob in self.list_all_blobs(subpath=f"code/{entry['name']}"):
                    to_delete.append(blob)

        # ── G) Commit deletions in batches ──
        if to_delete:
            print(f"Cleaning up release branch '{slug}'…")
            self._commit_deletion_actions(
                paths_to_delete=to_delete,
                branch=self._branch,
                commit_msg_prefix=f"Remove disallowed pipelines on '{slug}'"
            )
        else:
            print(f"No disallowed files to delete on '{slug}'.")

        # ── H) Done ──

        print(f"✅ Release branch '{slug}' created. Pipelines: {sorted(allowed_pipelines)}")

    def get_subgroup_id(self):
        """
        Fetch the GitLab subgroup ID based on the namespace path.
        """
        subgroup_url = f"{self.gitlab_base}/groups/{self.gitlab_namespace.replace('/', '%2F')}"
        resp = requests.get(subgroup_url, headers=self.headers, timeout=30)
        resp.raise_for_status()
        return resp.json()['id']

    def _commit_deletion_actions(
        self,
        paths_to_delete: list[str],
        branch: str,
        commit_msg_prefix: str
    ):
        """
        Batch-delete multiple files in a single (or multiple) commit(s):
        
        - paths_to_delete: list of file paths (e.g. "config/FOO.json" or "code/PL_XYZ/foo.sql").
        - branch: the GitLab branch to apply the deletion on (e.g. "release/test5").
        - commit_msg_prefix: a prefix for the commit message; each batch appends "(batch N of M)".
        
        Splits into batches of 50 files each if needed.
        """
        if not paths_to_delete:
            return

        proj = self.project_path.replace('/', '%2F')
        BATCH_SIZE = 50
        total = len(paths_to_delete)
        num_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

        for batch_idx in range(num_batches):
            start = batch_idx * BATCH_SIZE
            end = min(start + BATCH_SIZE, total)
            batch_paths = paths_to_delete[start:end]

            actions = []
            for fpath in batch_paths:
                actions.append({
                    "action":    "delete",
                    "file_path": fpath
                })

            commit_message = f"{commit_msg_prefix} (batch {batch_idx+1} of {num_batches})"
            payload = {
                "branch":         branch,
                "commit_message": commit_message,
                "actions":        actions
            }

            url = f"{self.gitlab_base}/projects/{proj}/repository/commits"
            resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if resp.status_code not in (200, 201):
                raise RuntimeError(
                    f"Failed to commit deletions on '{branch}' "
                    f"(status {resp.status_code}): {resp.text}"
                )

    def list_all_blobs(self, subpath: str) -> list[str]:
        """
        Return a list of every blob ("file") under `subpath` on self._branch,
        using GitLab's recursive tree API.
        E.g. subpath="code/PL_XYZ" might return
        ["code/PL_XYZ/foo.sql", "code/PL_XYZ/subdir/bar.py", … ].
        """
        proj = self.project_path.replace('/', '%2F')
        page = 1
        per_page = 100
        all_blobs: list[str] = []

        while True:
            params = {
                'ref':       self._branch,
                'path':      subpath,
                'recursive': True,
                'per_page':  per_page,
                'page':      page
            }
            url = f"{self.gitlab_base}/projects/{proj}/repository/tree"
            resp = requests.get(
                url,
                headers={'PRIVATE-TOKEN': self.gitlab_token},
                params=params,
                timeout=30
            )
            resp.raise_for_status()

            items = resp.json()
            if not items:
                break

            for it in items:
                if it.get('type') == 'blob':
                    all_blobs.append(it['path'])

            if len(items) < per_page:
                break
            page += 1

        return all_blobs
    
    def create_feature_branch(self, feature_name: str):
        """
        1) Only allow creating a feature branch from the development branch.
        2) Create (if needed) a new GitLab branch named 'feature/{feature_name}'
           off the development branch.
        3) Switch self._branch to that new feature branch.
        """
        dev_branch = self.branch_roles["development"]
        # 1) Enforce that we're currently on dev
        if self._branch != dev_branch:
            raise RuntimeError(
                f"❌ Feature branches can only be created from '{dev_branch}' "
                f"(current branch is '{self._branch}')."
            )

        # 2) Slugify the new feature branch name
        raw = f"feature/{feature_name}"
        slug = re.sub(r'[^A-Za-z0-9\-_\/]+', "-", raw)

        # 3) Create (or confirm) the new branch off dev
        try:
            self.ensure_branch_exists(branch_name=slug, ref=dev_branch)
        except RuntimeError as e:
            msg = str(e).lower()
            if "already existed" in msg or ("branch" in msg and "already" in msg):
                print(f"ℹ️  Branch '{slug}' already exists; continuing.")
            else:
                raise

        # 4) Switch to the new feature branch
        self._set_branch(slug)
        print(f'Checked out {slug} branch')
        print(f"✅ Feature branch '{slug}' created off '{dev_branch}'.")

    def create_hotfix_branch(self, branch_name: str):
        """
        1) Create (if needed) a new GitLab branch named 'hotfix/{branch_name}'
           off the production branch.
        2) Switch self._branch to that hotfix branch.
        3) Under 'config/' and 'code/', delete every file that does NOT
           belong to one of the pipelines in self.aic.pipeline_configs.
        """
        # ── A) Build set of pipelines you're allowed to touch ──
        allowed = {cfg["name"] for cfg in self.aic.pipeline_configs}

        # ── B) Figure out your production branch name ──
        #    Try reverse‐mapping the production workspace to its branch key,
        #    otherwise fall back to the repo's default_branch.
        try:
            prod_workspace = self.mapper.lookup("main")  # maps key "main" → workspace name
            prod_branch = self.mapper.workspace_to_branch(prod_workspace)
        except Exception:
            prod_branch = self.default_branch

        # ── C) Compute your hotfix branch slug ──
        raw = f"hotfix/{branch_name}"
        slug = re.sub(r'[^A-Za-z0-9\-_\/]+', '-', raw)

        # ── D) Ensure it exists off production ──
        try:
            self.ensure_branch_exists(branch_name=slug, ref=prod_branch)
        except RuntimeError as e:
            msg = str(e).lower()
            if "already existed" in msg or ("branch" in msg and "already" in msg):
                print(f"ℹ️  Hotfix branch '{slug}' already existed; continuing.")
            else:
                raise

        # ── E) Switch into it ──
        self._set_branch(slug)
        print(f'Checked out {slug} branch')

        # ── F) Collect all config files not in allowed set ──
        to_delete = []
        for fn in self.list_pipeline_files(subpath="config"):
            name = fn[:-5]  # strip ".json"
            if name not in allowed:
                to_delete.append(f"config/{fn}")

        # ── G) Collect all code blobs under code/<pipeline> for
        #      pipelines not in allowed ──
        proj = self.project_path.replace('/', '%2F')
        resp = requests.get(
            f"{self.gitlab_base}/projects/{proj}/repository/tree",
            headers={'PRIVATE-TOKEN': self.gitlab_token},
            params={'ref': self._branch, 'path': 'code', 'per_page': 100},
            timeout=30
        )
        resp.raise_for_status()
        folders = [e['name'] for e in resp.json() if e.get('type') == 'tree']
        for folder in folders:
            if folder not in allowed:
                for blob in self.list_all_blobs(subpath=f"code/{folder}"):
                    to_delete.append(blob)

        # ── H) Batch‐commit the deletions ──
        if to_delete:
            print(f"🔨 Cleaning up hotfix branch '{slug}'…")
            self._commit_deletion_actions(
                paths_to_delete   = to_delete,
                branch            = self._branch,
                commit_msg_prefix = f"Remove non-hotfix pipelines on '{slug}'"
            )
        else:
            print(f"✅ No extraneous files to delete on hotfix branch '{slug}'.")

        print(f"✅ Hotfix branch '{slug}' ready; only pipelines: {sorted(allowed)}")

        
    def create_merge_request(self, title: str, description: str, target_branch: str = None, assignee_ids: list = None):
        """
        Create a GitLab merge request from the current branch into target_branch.
        If target_branch is not provided, it is determined automatically based on the current branch.
        """
        original_branch = self._branch
        # Auto-determine target branch if not provided
        if target_branch is None:
            if self._branch.startswith("feature/"):
                target_branch = "staging"
            elif self._branch.startswith(("release/", "hotfix/")) or self._branch == "staging":
                target_branch = "main"
            else:
                target_branch = "main"

        if not any(self._branch.startswith(pref) for pref in ('feature/', 'release/', 'hotfix/')):
            raise RuntimeError(
                "❌ Merge requests can only be created from feature/*, release/*, or hotfix/* branches."
            )
        url = f"{self.gitlab_base}/projects/{self.project_path}/merge_requests"
        payload = {
            'source_branch': self._branch,
            'target_branch': target_branch,
            'title': title,
            'description': description
        }
        if assignee_ids:
            payload['assignee_ids'] = assignee_ids
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        mr = response.json()
        print(f"✅ Created MR !{mr['iid']} from {self._branch} → {target_branch}")
        self._set_branch(original_branch)
        print(f'Checked out {original_branch}')
        # return mr

    # Add this class method to your GitLabManager class

   # Update the class method in GitLabManager to be simple

    @classmethod  
    def initialize_repository(
        cls,
        gitlab_token: str,
        gitlab_namespace: str,
        repo_folder: str,
        gitlab_base_url: str = "https://git.autodatacorp.org/api/v4"
    ) -> bool:
        """
        Class method to initialize a GitLab repository with proper structure.

        Creates standard branches, workspace mappings, security scanning, and README automatically.
        """
        try:
            print(f"🚀 Initializing repository: {gitlab_namespace}{repo_folder}")

            # Create temporary instance
            temp_mgr = cls.__new__(cls)
            temp_mgr._setup_for_initialization(
                gitlab_token=gitlab_token,
                gitlab_namespace=gitlab_namespace,
                repo_folder=repo_folder,
                gitlab_base_url=gitlab_base_url
            )

            # Run the initialization
            from gitlab_init import GitLabRepositoryInitializer
            initializer = GitLabRepositoryInitializer(temp_mgr)
            result = initializer.initialize_repository()

            if result:
                print("✅ Repository initialization completed successfully!")
                print("📚 README.md generated with project-specific documentation")
                print("   You can now create GitLabManager instances normally.")

            return result

        except Exception as e:
            print(f"❌ Repository initialization failed: {e}")
            return False

    def _setup_for_initialization(
        self, 
        gitlab_token: str, 
        gitlab_namespace: str, 
        repo_folder: str,
        gitlab_base_url: str
    ):
        """
        Internal method to set up minimal attributes for initialization.
        Only sets what's needed for GitLabRepositoryInitializer to work.
        """
        # Core GitLab API setup
        self.gitlab_base = gitlab_base_url.rstrip('/')
        self.gitlab_token = gitlab_token
        self.headers = {
            'Private-Token': gitlab_token,
            'Content-Type': 'application/json'
        }

        # Project path setup
        self.gitlab_namespace = gitlab_namespace.rstrip('/')
        self.repo_folder = repo_folder
        raw = f"{self.gitlab_namespace}/{self.repo_folder}"
        self.project_path = quote(raw, safe='')

        # Get default branch from GitLab
        try:
            resp = requests.get(
                f"{self.gitlab_base}/projects/{self.project_path}",
                headers=self.headers,
                timeout=30
            )
            resp.raise_for_status()

            api_def = resp.json().get('default_branch')
            if not api_def:
                raise RuntimeError(f"GitLab returned no default_branch for project '{self.project_path}'.")

            self.default_branch = api_def
            print(f"   Using default branch: '{self.default_branch}'")

        except requests.exceptions.HTTPError as e:
            status = getattr(e.response, 'status_code', None)
            if status == 404:
                raise RuntimeError(
                    f"❌ GitLab project '{self.gitlab_namespace}/{self.repo_folder}' not found. "
                    "Please check that your namespace and repo_folder are correct."
                ) from e
            raise
            
    @classmethod
    def wipe_repository(
        cls,
        gitlab_token: str,
        gitlab_namespace: str,
        repo_folder: str,
        gitlab_base_url: str = "https://git.autodatacorp.org/api/v4",
        keep_branches: list = None
    ):
        """
        Completely wipe a GitLab repository of all files and branches.
        """
        from urllib.parse import quote
        import requests

        confirm = input('Do you want to proceed with repository wipe? (y/n) ')
        if confirm.lower() != 'y':
            raise ValueError("Wipe not confirmed. Exiting.")

        if keep_branches is None:
            keep_branches = ['main']

        project_path = quote(f"{gitlab_namespace.rstrip('/')}/{repo_folder}", safe='')
        print(f"WIPING REPOSITORY: {project_path}")
        print("⚠️  This action is IRREVERSIBLE!")

        headers = {
            "Authorization": f"Bearer {gitlab_token}",
            "Content-Type": "application/json"
        }

        try:
            # Step 1: Get all branches
            url = f"{gitlab_base_url}/projects/{project_path}/repository/branches"
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            all_branches = response.json()

            print(f"Found {len(all_branches)} branches")

            # Step 2: Remove all files from each kept branch
            for branch_name in keep_branches:
                if branch_name in [b['name'] for b in all_branches]:
                    print(f"🗑️  Removing all files from branch '{branch_name}'...")
                    cls._remove_all_files_from_branch_simple_static(
                        gitlab_base_url, project_path, branch_name, headers
                    )

            # Step 3: Delete all branches except kept ones
            branches_to_delete = [b for b in all_branches if b['name'] not in keep_branches]
            print(f"Deleting {len(branches_to_delete)} branches...")

            for branch in branches_to_delete:
                cls._delete_branch_simple_static(
                    gitlab_base_url, project_path, branch['name'], headers
                )

            print("Repository wipe completed!")
            return True

        except Exception as e:
            print(f"Repository wipe failed: {e}")
            raise

    @staticmethod
    def _remove_all_files_from_branch_simple_static(gitlab_base_url, project_path, branch_name, headers):
        from urllib.parse import quote_plus
        url = f"{gitlab_base_url}/projects/{project_path}/repository/tree"
        params = {
            "ref": branch_name,
            "recursive": True,
            "per_page": 100
        }
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            tree_items = response.json()
            files = [item['path'] for item in tree_items if item['type'] == 'blob']
            print(f"   Removing {len(files)} files from '{branch_name}'...")
            for file_path in files:
                try:
                    encoded_path = quote(file_path, safe='')
                    file_url = f"{gitlab_base_url}/projects/{project_path}/repository/files/{encoded_path}"
                    payload = {
                        "branch": branch_name,
                        "commit_message": f"Remove {file_path} - Repository wipe"
                    }
                    delete_response = requests.delete(file_url, headers=headers, json=payload, timeout=30)
                    if delete_response.status_code in [200, 204, 404]:
                        print(f"Deleted {file_path}")
                    else:
                        print(f"Could not delete {file_path}: HTTP {delete_response.status_code}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
        except Exception as e:
            print(f"     Warning: Could not list files in '{branch_name}': {e}")

    @staticmethod
    def _delete_branch_simple_static(gitlab_base_url, project_path, branch_name, headers):
        from urllib.parse import quote_plus
        if branch_name in ['main', 'master']:
            print(f"     ⚠️  Skipping deletion of protected branch '{branch_name}'")
            return
        try:
            protection_url = f"{gitlab_base_url}/projects/{project_path}/protected_branches/{quote_plus(branch_name)}"
            requests.delete(protection_url, headers=headers, timeout=30)
            branch_url = f"{gitlab_base_url}/projects/{project_path}/repository/branches/{quote_plus(branch_name)}"
            response = requests.delete(branch_url, headers=headers, timeout=30)
            if response.status_code in [200, 204]:
                print(f"Deleted branch '{branch_name}'")
            elif response.status_code == 404:
                print(f"Branch '{branch_name}' already doesn't exist")
            else:
                print(f"Failed to delete branch '{branch_name}': HTTP {response.status_code}")
        except Exception as e:
            print(f"Failed to delete branch '{branch_name}': {e}")
            
            
#     def _delete_branch_simple(self, branch_name: str, headers: dict):
#         """Delete a specific branch using requests directly."""
#         if branch_name in ['main', 'master']:
#             print(f"     ⚠️  Skipping deletion of protected branch '{branch_name}'")
#             return

#         try:
#             # First remove protection if it exists
#             protection_url = f"{self.gitlab_base}/projects/{self.project_path}/protected_branches/{quote_plus(branch_name)}"
#             requests.delete(protection_url, headers=headers, timeout=30)

#             # Then delete the branch
#             branch_url = f"{self.gitlab_base}/projects/{self.project_path}/repository/branches/{quote_plus(branch_name)}"
#             response = requests.delete(branch_url, headers=headers, timeout=30)

#             if response.status_code in [200, 204]:
#                 print(f"Deleted branch '{branch_name}'")
#             elif response.status_code == 404:
#                 print(f"Branch '{branch_name}' already doesn't exist")
#             else:
#                 print(f"ailed to delete branch '{branch_name}': HTTP {response.status_code}")

#         except Exception as e:
#             print(f"Failed to delete branch '{branch_name}': {e}")


class BranchWorkspaceMapper:
    def __init__(self, git_manager, mapping_file: str = "branch_to_workspace.yaml"):
        """
        Loads YAML mapping from GitLab default branch mapping_file.
        mapping:
          main: ProductionWorkspace
          develop: QAWorkspace
          dev: DevWorkspace
        feature/* -> develop
        release/*, hotfix/* -> main
        """
        self.git = git_manager
        self.raw_mapping = {}
        self._prefix_patterns = []
        # fetch mapping_file from default branch
        try:
            raw = git_manager.fetch_pipeline_file(mapping_file, ref=git_manager.default_branch)
            data = safe_load(raw)
            if isinstance(data, dict) and "mapping" in data:
                self.raw_mapping = data["mapping"]
            else:
                print(f"'{mapping_file}' invalid or missing 'mapping' key.")
        except FileNotFoundError:
            print(f"Mapping file '{mapping_file}' not found on branch '{git_manager.default_branch}'.")
        # compile prefix patterns for exact key with /*
        for key, ws in self.raw_mapping.items():
            if key.endswith("/*"):
                prefix = key[:-2]
                rx = re.compile(rf"^{re.escape(prefix)}/")
                self._prefix_patterns.append((rx, ws))

    def lookup(self, branch: str) -> str:
        """
        Maps branch->workspace. Falls back to KeyError.
        """
        # exact
        if branch in self.raw_mapping:
            return self.raw_mapping[branch]
        # prefix
        for rx, ws in self._prefix_patterns:
            if rx.match(branch):
                return ws
        # built-in prefixes
        if branch.startswith("feature/"):
            return self.raw_mapping.get("develop")
        if branch.startswith(("release/", "hotfix/")):
            return self.raw_mapping.get("main")
        raise KeyError(f"No mapping for branch '{branch}'")

    def workspace_to_branch(self, workspace: str) -> str:
        """
        Reverse lookup workspace->branch. Falls back to slug.
        """
        for key, ws in self.raw_mapping.items():
            if ws == workspace and not key.endswith("/*"):
                return key
        slug = re.sub(r'[^a-z0-9]+', '-', workspace.lower()).strip('-')
        print(f"'{workspace}' workspace not in branch mapping; slugging to '{slug}'.")
        return slug


