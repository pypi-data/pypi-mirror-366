# GitLabManager & AIC Integration Guide


## 1. Executive Overview

This guide introduces a repeatable, audit-friendly methodology for managing your AIC pipelines in tandem with GitLab, bridging the gap between your workspace configurations in AIC and your version-controlled artifacts in Git.

By leveraging the aic_utils package and the GitLabManager helper library, you gain end-to-end control over:
   - Authentication & discovery
   - Configuration extraction & storage
   - Automated branch and workspace mapping
   - Safe, MR-driven promotions through Sandbox → QA → Production
   - Embedded code snippet extraction for SQL and PySpark tasks

This integration ensures that every pipeline change—from minor SQL tweak to full-scale workflow overhaul—is captured as code, reviewed via merge requests, and traceable through Git history. It enforces a strict 1:1 relationship between Git branches and AIC workspaces, preventing accidental or out-of-sync deployments. Whether you’re onboarding a new environment, back-syncing an existing workspace, or building feature-specific sandbox branches, this approach provides the guardrails and automation you need to move fast without sacrificing governance or reliability.

In the sections that follow, you’ll find:

   - aic_utils Overview – Core classes, methods, and patterns for programmatic pipeline management.
   - GitLabManager Deep-Dive – Configuration, branch mapping, and code-sync mechanics.
   - Day-to-Day Workflows – Step-by-step guides for common tasks: syncing changes, feature work, releases, and hotfixes.
   - Advanced Scenarios – Bootstrapping new workspaces, force-sync operations, and backup strategies.
   - Best Practices & Troubleshooting – Tips to avoid pitfalls and quickly resolve common issues.



### Core GitLabManager functionality:

- **Storing every pipeline** as JSON and code snippets in Git.
   - Job metadata is stored in  `config` in JSON form
   - Code snippets are saved in the respective `code` folders for corporate code scanning
- **Enforcing** clear branch naming conventions and 1:1 branch ↔ workspace mappings.
- **Automating** creation of feature, release, and hotfix branches and enforcing proper git flow
- **Preventing** inadvertent cross‑environment deployments, disruption to production, or lose of code between environments.
- **Auditing** all changes via merge requests and commit history.

---

## 2. AIC SDK (aic_utils)

The `AIC` class wraps the AIC REST API, exposing five main capability areas:

1. **Authentication & Init**  
2. **Pipeline Discovery**  
3. **Configuration Fetching**  
4. **Pipeline Upsert (CRUD)**  
5. **Workspace Artifact Management**

---

### 2.1 Authentication & Init

AIC(api_key: str,
    project: str,
    workspace: str,
    pipelines: list[str] = [],
    qa: bool = False)

- **What it does**  
  - Chooses the PROD vs QA base-URL (qa flag).  
  - Sets headers (accept, api-key, Content-Type).  
  - Resolves and stores project_id and workspace_id.  
  - Loads all pipelines into .pipelines and, if requested, their configs into .pipeline_configs.

- **Attributes**  
  - self.base_url – endpoint root  
  - self.headers – auth + content headers  
  - self.project_id, self.workspace_id (strings)  
  - self.pipelines: list[dict{name: str, id: str}]  
  - self.pipeline_configs: list[dict{name: str, jobConfig: dict, id: str}]

---

### 2.2 Pipeline Discovery

.pop_pipelines() → list[{'name': str, 'id': str}]

- **Signature**  
  def pop_pipelines(self) -> list[{'name': str, 'id': str}]
- **What it does**  
  - GET /projects/{proj}/workspaces/{ws}/jobs  
  - Parses jobs array, extracts title as name and '$id' as id.
- **Returns**  
  - A list of {'name': pipelineName, 'id': pipelineId}.
- **Side effects**  
  - Updates self.pipelines and prints “Loaded N pipelines…”.

.pop_pipeline_config(pipelines: list[str]) → list[{'name', 'jobConfig', 'id'}]

- **Signature**  
  def pop_pipeline_config(self, pipelines: list[str]) -> list[{'name', 'jobConfig', 'id'}]
- **Parameters**  
  - pipelines: names to fetch, or ['*'] for all.
- **What it does**  
  - Filters self.pipelines by name.  
  - Uses a thread pool to call fetch_pipeline_config() in parallel.
- **Returns**  
  - A list of configs: { 'name':…, 'jobConfig': <JSON>, 'id': <jobConfig.$id> }.

---

### 2.3 Configuration Fetching

.fetch_pipeline_config(pipeline: dict, direct: bool=False) → dict

- **Signature**  
  def fetch_pipeline_config(self, pipeline: {'name': str, 'id' or '$id': str}, direct: bool = False) → {'name': str, 'jobConfig': dict, 'id': str}
- **Parameters**  
  - pipeline: one entry from self.pipelines.  
  - direct: if True, uses pipeline['$id'] directly.
- **What it does**  
  - GET /projects/{proj}/workspaces/{ws}/jobs/{id}  
  - Extracts jobConfig block and its own '$id'.
- **Returns**  
  - { 'name': pipelineName, 'jobConfig': <JSON>, 'id': <jobConfig.$id> }
- **Raises**  
  - KeyError if no matching pipeline is found.

---

### 2.4 Pipeline Upsert (Create/Update)

.write_config_to_pipeline(config: dict) → None

- **Signature**  
  def write_config_to_pipeline(self, config: {'name': str, 'jobConfig': dict, 'id'?: str}) → None
- **What it does**  
  - Builds payload with title, stages, variables, sourceStage, sinkStage.  
  - POST /projects/{proj}/workspaces/{ws}/jobs (creates or updates based on id).
- **Logs**  
  - “Created pipeline…” or “Updated pipeline…”
- **Error Handling**  
  - Catches HTTP errors, prints status and response text.

.create_pipeline_branch(config: dict) → Response

- **Signature**  
  def create_pipeline_branch(self, config: {'id': str, 'jobConfig': dict, 'name': str}) → Response
- **What it does**  
  - Generates PUSH_YYYYMMDDHHMMSS branch.  
  - PUT /interactive-pipeline/{jobId}/branches.

.create_or_update_pipeline(workspace_id: str, pipeline_config: dict) → None

- **Signature**  
  def create_or_update_pipeline(self, workspace_id: str, pipeline_config: {'name': str, 'jobConfig': dict, 'id'?: str}) → None
- **What it does**  
  - POST /jobs to create. On 409 Conflict, calls update_pipeline().

.update_pipeline(workspace_id: str, pipeline_id: str, pipeline_config: dict) → None

- **Signature**  
  def update_pipeline(self, workspace_id: str, pipeline_id: str, pipeline_config: {'name': str, 'jobConfig': dict}) → None
- **What it does**  
  - PUT /projects/{proj}/workspaces/{ws}/jobs/{id} to update.

---

### 2.5 Workspace Artifact Management

**Datasets & Tables**  
.get_datasets() → list[dict]  
  - GET /datasets → list of dataset objects.  
.get_tables(dataset_id: str) → list[dict]  
  - GET /datasets/{id}/tables → list of tables.

**Interactive Branches**  
.delete_branches(job_names: list[str]) → None  
  - Deletes interactive branches via GET + DELETE.

**Backups**  
.backup_pipelines(pipelines: list[Union[str, dict]], base_folder: str='.', drive_name: str='backups') → None  
  - Creates dated folder (YYYYMMDD); uploads JSON via POST /upload-file.  
.get_drive_id_by_name(drive_name: str) → Optional[str]

---

#### Under the Hood

- Concurrency: Uses ThreadPoolExecutor.  
- Error Handling: response.raise_for_status(), prints warnings.  
- Logging: print() statements for auditability.  
- Timestamp: AIC.timestamp = instantiation date (YYYYMMDD).  

---

## 3. GitLabManager Overview

The `GitLabManager` class uses your AIC instance and the GitLab API to synchronize pipeline definitions, enforce branch/workspace governance, and automate promotions.

---

### 3.1 Initialization & Setup

GitLabManager(
    aic_instance: AIC,
    gitlab_token: str,
    gitlab_namespace: str,
    repo_folder: str,
    gitlab_base_url: str = "https://git.autodatacorp.org/api/v4",
    use_hash_comparison: bool = True,
    email_recipients: list = None,
    email_sender: str = None,
    mapping_file: str = "branch_to_workspace.yaml"
)

- **What it does**  
  - Stores references to AIC, GitLab endpoints, and auth tokens.  
  - Resolves `project_path`, retrieves `default_branch`, and loads branch→workspace mapping.  
  - Determines current branch (`self.branch`) from AIC workspace and ensures it exists.  
  - Configures optional email summary settings.

- **Key attributes**  
  - `self.aic`, `self.gitlab_base`, `self.gitlab_token`, `self.headers`  
  - `self.project_path`, `self.default_branch`, `self.branch`, `self.mapper`  
  - `self.email_recipients`, `self.email_sender`, `self.use_hash_comparison`

---

### 3.2 Repository & Branch Utilities

.repository_exists(repo_path: str) → bool  
  - **Checks**: `GET /projects/{repo_path}`  
  - **Returns**: True if HTTP 200, else False.

.create_repository(repo_name: str) → dict or None  
  - **Creates**: `POST /projects` under specified subgroup.  
  - **Returns**: Project JSON on success, else None.

.get_subgroup_id() → int  
  - **Fetches**: `GET /groups/{namespace}` to find subgroup ID.

.ensure_branch_exists(branch_name: str, ref: str) → None  
  - **Checks**: `GET /repository/branches/{branch_name}`  
  - **Creates**: If 404, `POST /repository/branches?branch={branch_name}&ref={ref}`  
  - **Logs**: Prints status of creation or existence.

._slugify(text: str) → str  
  - **Converts**: Arbitrary text to a URL-safe slug.

.check_token_expiration(warning_threshold_days: int = 30) → None  
  - **Retrieves**: Personal access tokens via `GET /personal_access_tokens`  
  - **Calculates**: Days until expiry, prints warnings if ≤ threshold.

---

### 3.3 File Operations

.get_existing_file_content(repo_name: str, file_name: str) → Optional[str]  
  - **Fetches**: Base64-encoded file via `GET /repository/files/{file_name}` on `self.branch` or `default_branch`.

.fetch_pipeline_file(full_path: str, ref: str = None) → str  
  - **Gets**: Raw content via `GET /repository/files/{full_path}/raw?ref={ref}`  
  - **Falls back**: to current branch then default branch.

.list_pipeline_files(subpath: str = None) → list[str]  
  - **Paginates**: `GET /repository/tree` (per_page=100), filters for `.json` files.

.list_all_blobs(subpath: str) → list[str]  
  - **Recursively lists**: All blobs under `subpath` via `GET /repository/tree?recursive=true`.

.delete_file(file_name: str, branch: str = None) → None  
  - **Deletes**: `DELETE /repository/files/{file_name}?branch={branch}&commit_message=...`

._commit_deletion_actions(paths_to_delete: list[str], branch: str, commit_msg_prefix: str) → None  
  - **Batches**: Up to 50 deletions per commit via `POST /repository/commits` with `actions=[{action: 'delete', file_path: ...}]`.

---

### 3.4 Pushing to Git

._push_file(proj_encoded: str, file_name: str, file_content: str, branch: str) → None  
  - **Creates**: `POST /repository/files/{file_name}` for new files.  
  - **Updates**: `PUT /repository/files/{file_name}` on 400/409 responses.

._extract_and_push_code(pipeline_name: str, job_config: dict) → None  
  - **Scans**: Recursively finds tasks of type `PYSPARK` or `SQL`.  
  - **Pushes**: Full `.py` scripts and extracted SQL blocks as `.sql` files.

.push_to_git() → None  
  - **Validates**: Current branch against slug, mapping, or feature pattern.  
  - **Pass 1**: Iterates `self.aic.pipeline_configs`, pushes JSON into `config/{name}.json`.  
  - **Pass 2**: Calls `_extract_and_push_code` to sync code under `code/{pipeline}`.  
  - **Email**: Summarizes results via `_format_push_summary` and `_send_email`.

._format_push_summary(branch: str, results: list[tuple]) → (subject: str, body: str)  
  - **Builds**: HTML email table of `(pipeline, status, message)` rows.

---

### 3.5 Deploying Pipelines

.deploy_pipelines(force_sync: bool = False) → None  
  - **Validates**: Branch→workspace via `self.mapper`.  
  - **Enforces**: Allowed branch patterns (slug, default, release/, feature/).  
  - **Force-sync**: If True, reads every `config/*.json` and upserts into AIC.  
  - **Hash-sync**: Else, compares old vs new JSON hashes, updates only changed pipelines.  
  - **Email**: Sends deployment summary via `_format_deploy_summary`.

---

### 3.6 Automated Branch Creation

.create_feature_branch(feature_name: str) → None  
  - **Requires**: Current branch is `sandbox`.  
  - **Creates**: `feature/{feature_name}` off `sandbox`, switches `self.branch`.

.create_release_branch(branch_name: str) → None  
  - **Requires**: Current branch is `develop`.  
  - **Creates**: `release/{branch_name}`, deletes any `config/` or `code/` files not in `self.aic.pipeline_configs`.

.create_hotfix_branch(branch_name: str) → None  
  - **Determines**: Production branch via mapper or default.  
  - **Creates**: `hotfix/{branch_name}` off prod, deletes pipelines not allowed.

---

### 3.7 Branch↔Workspace Mapping

BranchWorkspaceMapper(mapping_file: str = "branch_to_workspace.yaml")

- **Loads**: YAML mapping from `default_branch`.  
- **raw_mapping**: Dict of exact branch→workspace.  
- **_prefix_patterns**: Compiled regex for wildcard rules.

.lookup(branch: str) → str  
- **Exact match** in `raw_mapping`.  
- **Prefix match** for entries ending `/*`.  
- **Built-in**: `feature/` → develop, `release/` & `hotfix/` → main.

.workspace_to_branch(workspace: str) → str  
- **Reverse lookup** for a mapping key matching given workspace.  
- **Fallback slug** if none found.

---

### Under the Hood

- **Concurrency**: ThreadPoolExecutor used only in AIC, not here.  
- **Error Handling**: `response.raise_for_status()`, catch HTTPError around critical calls.  
- **Hashing**: Uses MD5 normalization to detect JSON changes.  
- **Logging**: Verbose `print()` statements for visibility during operations.  


---

## 4. User Guide

### 4.1 Repository Creation & Default Branch

1. **Create the GitLab project** under your namespace (e.g. `pin/pin-analytics/pin-fusion-2.0`).
2. **Set `main` as the default and protected branch** in _Settings → Repository → Branches_. This serves as the **Prod** branch in our mapping.
3. **Add a `branch_to_workspace.yaml`** on `main` to create a 1:1 mapping of desired workspace to designated git branches

```yaml
mapping:
  main:      PIN FUSION 2.0
  develop:   PIN FUSION 2.0 QA
  sandbox:   PIN FUSION 2.0 DEV

```
- **`mapping`**: exact branch names.

### 4.2 Preparing AIC() object
To leverage this GitLabManager, a proper AIC object needs to be created that will encapsulate the workspace in question as well as the pipelines required in the git operations. 

To obtain AIC API key, log into AIC and in the top right corner, navigate to ```User Profile -> Manage API Keys```

```python 
aic_prod = AIC(
    api_key   = "<API-KEY>",
    project   = "dylan.doyle@jdpa.com",
    workspace = "PROD TEST", 
    pipelines = ['test_job']
)
```
The correct branch will be selected or created based on the workspace passed and the branch_to_workspace.yaml file. If the file is not found or workspace is not mapped, the branch will default to a formatted string from the workspace name,

**NOTE**: Operations will be completely limited to this workspace and only the pipelines passed. Add more pipelines as desired, or pass ['*'] to load ALL pipelines. 

### 4.3 Preparing GitLabManager() object
Create a GitLabManager instance and pass the previously created AIC object so that GitLab API can speak directly to the objects in the AIC workspace.

```python
mgr = GitLabManager(
    aic_instance     = aic_prod,
    gitlab_token     = "<GIT_TOKEN>",
    gitlab_namespace = "pin/pin-analytics",
    repo_folder     = "aic-git-integration"
)
```

**TIP:** Multiple instances can be created for multiple workspaces (i.e for both Prod and QA instances). Each AIC workspace must have its own AIC instance and respective GitLabManager instance.

### 4.4 Syncing AIC code to Git

```python
mgr.push_to_git()
```

- **When**:
  - Initial branch/workspace git loads
  - When work is performed on `develop` or `sandbox` branches
  - Prior to cutting a `release` or `feature` branch
  - After creation of hotfix branch to synch changes in production workspace
- **What happens**:
  - Respective ```config/<pipeline>.json``` files are upserted via the GitLab API based on the `AIC.pipelines` list that was passed earlier.
  - Embedded PySpark/SQL code is extracted and pushed under ```code/<pipeline>/```.

- **Restrictions**:
  - Cannot push_git to `main` branch unless `force_push=True` is passed. This is to restrict production branches to release and hotfix merges primarily.
  - Cannot push_git to a branch corresponding to a different workspace
  - Cannot push_git to feature or release branches; these branches must be cut from the respective source environments which should contain updates in question.

---

### 4.5 Sandbox → Develop Push


1. **Create `sandbox` objects**
   ```python
   aic_sandbox = AIC(workspace='sandbox_workspace'...)
   mgr = GitLabManager(aic_instance=aic_sandbox, ...)
   ```
2. **Sync changes to `sandbox`**

   ```python
   mgr.push_to_git() # push current AIC state so sandbox branch captures the changes
   ```
3. **Cut a feature branch**

   ```python
   mgr.create_feature_branch("PINOPS-1831")     # sets mgr.branch to feature branch
   ```
4. **Create merge request and resolve**

   ```python
   mgr.create_merge_request(title="Demographics Module", description='Push for QA Testing', target_branch='develop')
   ```

5. **Deploy**

   ```python
   mgr.deploy_pipelines()                     # deploys merged pipelines to develop workspace
   ```
- **When**: Releasing a feature/code from `sandbox` or other similar environments. This is not a feature release to production.
- **What happens**:
  - Creates a new branch ```feature/PINOPS-1831``` off ```sandbox```.
  - Pushes all current ```config/``` and ```code/``` for the specified pipelines into that branch.
- ** Restrictions **:
   - Cannot open a feature branch from `main` or `develop` branches; feature branch creation is only for promoting code from sandbox-like environments. 
---

### 4.6 QA → Prod Release

1. **Create `develop` objects**
   ```python
   aic_qa = AIC(workspace='develop_workspace'...)
   mgr = GitLabManager(aic_instance=aic_qa, ...)
   ```
2. **Prepare QA**

   ```python
   # Starting from develop branch/workspace, ensure AIC has updated code
   mgr.push_to_git() # sync develop environment to capture new updates
   ```

3. **Cut Release Branch**

   ```python
   mgr.create_release_branch("PINOPS-1832")       # sets mgr.branch to 'release/v2.1.0'
   ```
   - Prunes any pipelines not in ```mgr.aic.pipeline_configs```.

4. **Create Merge Request and Resolve**

   ```python
   mgr.create_merge_request(
     title="Release v2.1.0",
     description="QA-approved changes for selected pipelines"
   )
   ```
   - Opens MR from ```release/v2.1.0``` → ```main```.

5. **Deploy**

   ```python
   mgr.deploy_pipelines()  # deploys merged pipelines to production workspace
   ```

- **When**: Releasing updates from develop to main
- **What happens**:
  - Creates a new branch ```release/PINOPS-1831``` off ```develop```.
  - Pushes all current ```config/``` and ```code/``` for the specified pipelines into that branch.
- ** Restrictions **:
   

---

### 4.7 Production Hotfix

1. **Diagnose & Plan**
   - Identify the pipeline(s) requiring an urgent fix.

2. **Create `main` objects**
   ```python
   aic_prod = AIC(workspace='prod_workspace', pipelines=['<PIPELINE_FROM_STEP1>'], ...)
   mgr = GitLabManager(aic_instance=aic_prod, ...)
   ```
   
2. **Create Hotfix Branch**

   ```python
   mgr.create_hotfix_branch("PINOPS-1831")
   # At this point, AIC prod environment should have the fix in place. 
   mgr.push_to_git() # Sync the updated code to the hotfix branch and NOT the production branch
   ```
   - Creates ```hotfix/PINOPS-1831``` off ```main``` and pushes the fix to hotfix branch.

3. **Prepare Hotfix branch**

   ```python
   # Starting from develop branch/workspace, ensure AIC has updated code
   mgr.push_to_git() # sync hotfix branch to current prod workspace
   ```
   **NOTE** The workflow for a Hotfix is the opposite of feature/release branches. Because the change will be made in the AIC production workspace prior, the `hotfix` branch will be updatec with `push_to_git()` while the `main` branch on the repository remains 1 commit behind. This is to ensure that fixes exclusively in production can be captured by a merge request and appropriately audited. 

4. **Open & Merge MR**

   ```python
   mgr.create_merge_request(
     title="Hotfix PINOPS-1831",
     description="Emergency fix: correct streaming timeout",
     target_branch="main"
   )
   ```

5. **Deploy & Back-merge**

   ## REVISE MEANS OF BACK-MERGING HOTFIXES

- **When**: Releasing immediate hotfixes straight from production
- **What happens**:
  - Creates a new branch ```hotfix/PINOPS-1831``` off ```develop```. 
    **The production branch will not contain the hotfix at this point.**
   - Hotfix branch gets updated with the new code additions
  - Hotfix gets merged back into production branch to synch branch to AIC workspace and contains audit trail and roll back function
- ** Restrictions **:
   - Hotfixes can only be created from `main` branch
---

## 6. Key Principles & Best Practices

1. **1:1 Branch↔Workspace**: Enforced via `branch_to_workspace.yaml`. No cross‑territory deployments.
2. **MR‑only Promotions**: `main`, `develop`, `sandbox` are protected; all changes flow via `feature/*`, `release/*`, or `hotfix/*`.
3. **Audit Trail**: Every pipeline change lives in Git; interactive branches on AIC mirror the same JSON.
4. **No CLI**: End users only call Python methods; they never need to know Git commands.
5. **Error Handling**: Guards in code refuse unsafe operations (wrong branch, unmapped workspace).

---

## 7. Further Reading & Support

- **Contact**: Dylan Doyle.

# GitLabManager & AIC Integration Guide


