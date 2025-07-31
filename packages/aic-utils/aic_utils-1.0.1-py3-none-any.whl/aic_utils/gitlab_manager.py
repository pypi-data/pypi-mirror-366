#!/usr/bin/env python3
import hashlib
import base64
import requests
import json
from datetime import datetime

class GitLabManager:
    """
    Manage a single GitLab project where each branch represents an environment
    and each pipeline config is stored as a separate JSON file.
    Includes GitLab token checks, file hash comparisons, subgroup handling,
    per-pipeline repo support, and deploy-from-git functionality.
    """
    def __init__(
        self,
        aic_instance,
        gitlab_token,
        gitlab_namespace,
        project_name="jobs",
        environment="production",
        gitlab_base_url="https://git.autodatacorp.org/api/v4",
        use_hash_comparison=True
    ):
        # AIC client to fetch pipeline_configs
        self.aic = aic_instance
        # GitLab API settings
        self.gitlab_base = gitlab_base_url.rstrip('/')
        self.gitlab_token = gitlab_token
        self.use_hash_comparison = use_hash_comparison
        self.headers = {
            'Private-Token': self.gitlab_token,
            'Content-Type': 'application/json'
        }
        # Namespace and project path
        self.gitlab_namespace = gitlab_namespace.rstrip('/')
        self.project_name = project_name
        # Environment branch name
        self.branch = environment.lower()
        # e.g. 'pin/pin-analytics/pin-fusion-2.0/jobs'
        self.project_path = f"{self.gitlab_namespace}/{self.project_name}"
        # Determine subgroup for legacy flows
        self.workspace_name = self.aic.workspace
        self.subgroup_id = self._ensure_correct_subgroup(self.workspace_name)

    # --- Token expiration checks ---
    def get_token_expiration_date(self):
        """Retrieves the expiration date of the GitLab token."""
        url = f"{self.gitlab_base}/personal_access_tokens"
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params={'name': 'fusion-push', 'revoked': 'false'}
            )
            response.raise_for_status()
            tokens = response.json()
            for t in tokens:
                if t.get('name') == 'fusion-push' and not t.get('revoked', True):
                    exp = t.get('expires_at')
                    fmt = '%Y-%m-%dT%H:%M:%S.%fZ' if 'T' in exp else '%Y-%m-%d'
                    return datetime.strptime(exp, fmt)
        except requests.exceptions.HTTPError as err:
            print(f"Error checking token expiration: {err}")
        return None

    def check_token_expiration(self):
        """Checks and prints days until the token expires."""
        exp = self.get_token_expiration_date()
        if exp:
            days_left = (exp - datetime.now()).days
            print(f"GitLab Token expires in {days_left} days.")
            if days_left < 7:
                print("Token is expiring soon. Consider updating it.")
        else:
            print("Could not retrieve token expiration date.")

    # --- Utility: hashing ---
    def generate_hash(self, content):
        """MD5 hash of normalized content."""
        norm = content.strip().replace('\r\n', '\n').replace('\r', '\n')
        return hashlib.md5(norm.encode('utf-8')).hexdigest()

    # --- Legacy subgroup/repo handling ---
    def _ensure_correct_subgroup(self, workspace):
        ns = self.gitlab_namespace
        if ns.endswith('/pipelines'):
            if workspace.lower().endswith('qa'):
                return f"{ns}/qa"
            return f"{ns}/production"
        return ns

    def get_subgroup_id(self):
        url = f"{self.gitlab_base}/groups/{self.subgroup_id.replace('/', '%2F')}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()['id']

    def get_namespace_id(self):
        url = f"{self.gitlab_base}/namespaces?search={self.gitlab_namespace}"
        r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            for ns in r.json():
                if ns.get('full_path') == self.gitlab_namespace:
                    return ns['id']
        return None

    # --- Per-pipeline repo support (legacy) ---
    def repository_exists(self, repo_path):
        url = f"{self.gitlab_base}/projects/{repo_path.replace('/', '%2F')}"
        r = requests.get(url, headers=self.headers)
        return r.status_code == 200

    def create_repository(self, repo_name):
        url = f"{self.gitlab_base}/projects"
        data = {
            'name': repo_name,
            'namespace_id': self.get_subgroup_id(),
            'visibility': 'private'
        }
        r = requests.post(url, headers=self.headers, json=data)
        if r.status_code == 201:
            return r.json()
        print(f"Failed to create repo {repo_name}: {r.status_code} {r.text}")
        return None

    def get_existing_file_content(self, repo_name, file_name):
        url = (f"{self.gitlab_base}/projects/"
               f"{repo_name.replace('/', '%2F')}/repository/files/{file_name}?ref=main")
        r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            enc = r.json().get('content')
            return base64.b64decode(enc).decode('utf-8') if enc else None
        return None

    def push_file_to_repo(self, repo_name, file_name, file_content):
        repo_path = f"{self.subgroup_id}/{repo_name.replace(' ', '_')}"
        if not self.repository_exists(repo_path):
            if not self.create_repository(repo_name):
                return
            self.push_new_file(repo_path, file_name, file_content)
            return
        if self.use_hash_comparison:
            old = self.get_existing_file_content(repo_path, file_name)
            if old and self.generate_hash(old) == self.generate_hash(file_content):
                print(f"No change for {file_name}")
                return
        self.push_new_file(repo_path, file_name, file_content)

    def push_new_file(self, repo_path, file_name, file_content):
        url = (f"{self.gitlab_base}/projects/"
               f"{repo_path.replace('/', '%2F')}/repository/files/{file_name}")
        data = {
            'branch': 'main',
            'content': file_content,
            'commit_message': f"Update {file_name} – {datetime.now():%Y-%m-%d}"  
        }
        resp = requests.post(url, headers=self.headers, json=data)
        if resp.status_code == 201:
            print(f"Created {file_name} in {repo_path}")
        elif resp.status_code in (400, 409):
            r2 = requests.put(url, headers=self.headers, json=data)
            print(f"Updated {file_name}" if r2.status_code == 200 else r2.text)

    # --- Unified single-project flow ---
    def ensure_branch_exists(self, branch_name=None, ref="main"):
        branch = branch_name or self.branch
        proj = self.project_path.replace('/', '%2F')
        r = requests.get(
            f"{self.gitlab_base}/projects/{proj}/repository/branches/{branch}",
            headers=self.headers
        )
        if r.status_code == 404:
            c = requests.post(
                f"{self.gitlab_base}/projects/{proj}/repository/branches"
                f"?branch={branch}&ref={ref}",
                headers=self.headers
            )
            if c.status_code != 201:
                raise RuntimeError(f"Could not create branch: {c.text}")
            print(f"Created branch '{branch}'")

    def push_pipelines(self):
        """Serialize each AIC pipeline as JSON into the env branch."""
        self.ensure_branch_exists()
        proj = self.project_path.replace('/', '%2F')
        for cfg in self.aic.pipeline_configs:
            fn = f"{cfg['name']}.json"
            content = json.dumps(cfg['jobConfig'], indent=2)
            self._push_file(proj, fn, content, branch=self.branch)

    def _push_file(self, proj_encoded, file_name, file_content, branch):
        url = (
            f"{self.gitlab_base}/projects/{proj_encoded}"
            f"/repository/files/{file_name}"
        )
        payload = {
            'branch': branch,
            'content': file_content,
            'commit_message': f"Sync {file_name} – {datetime.now():%Y-%m-%d}"  
        }
        r = requests.post(url, headers=self.headers, json=payload)
        if r.status_code == 201:
            print(f"Created {file_name} on branch '{branch}'")
            return
        if r.status_code in (400, 409):
            r2 = requests.put(url, headers=self.headers, json=payload)
            if r2.status_code == 200:
                print(f"Updated {file_name} on branch '{branch}'")
                return
        raise RuntimeError(f"Write failed: {r.status_code} {r.text}")

    def delete_file(self, file_name, branch=None):
        """Remove a file from the environment branch."""
        branch = branch or self.branch
        proj = self.project_path.replace('/', '%2F')
        r = requests.delete(
            f"{self.gitlab_base}/projects/{proj}/repository/files/{file_name}",
            headers=self.headers,
            params={
                'branch': branch,
                'commit_message': f"Remove {file_name} – {datetime.now():%Y-%m-%d}"  
            }
        )
        if r.status_code == 204:
            print(f"Deleted {file_name}")
        else:
            raise RuntimeError(f"Delete failed: {r.status_code} {r.text}")

    # --- Deploy from GitLab to AIC ---
    def list_pipeline_files(self):
        """List all .json files in the current env branch."""
        proj = self.project_path.replace('/', '%2F')
        url = f"{self.gitlab_base}/projects/{proj}/repository/tree"
        resp = requests.get(
            url, headers={'PRIVATE-TOKEN': self.gitlab_token},
            params={'ref': self.branch}
        )
        resp.raise_for_status()
        return [item['name'] for item in resp.json()
                if item['type']=='blob' and item['name'].endswith('.json')]

    def fetch_pipeline_file(self, filename):
        """Fetch raw JSON content for a single pipeline file."""
        proj = self.project_path.replace('/', '%2F')
        url = (f"{self.gitlab_base}/projects/{proj}"
               f"/repository/files/{filename.replace('/', '%2F')}/raw")
        resp = requests.get(
            url, headers={'PRIVATE-TOKEN': self.gitlab_token},
            params={'ref': self.branch}
        )
        resp.raise_for_status()
        return resp.text

    def deploy_pipelines(self):
        """Read each JSON in git and create/update pipelines in AIC."""
        for fname in self.list_pipeline_files():
            print(f"Deploying {fname} to AIC...")
            raw = self.fetch_pipeline_file(fname)
            cfg = json.loads(raw)
            name = fname.rsplit('.json',1)[0]
            pipeline_conf = {'name': name, 'jobConfig': cfg, 'id': cfg.get('$id')}
            self.aic.create_or_update_pipeline(self.aic.workspace_id, pipeline_conf)