import json
import requests
from datetime import datetime
from urllib.parse import quote_plus

class GitLabRepositoryInitializer:
    """Handles GitLab repository initialization with security scanning and Git flow setup."""
    
    def __init__(self, gitlab_manager):
        """Initialize with an existing GitLabManager instance."""
        self.mgr = gitlab_manager
        self.gitlab_base = gitlab_manager.gitlab_base
        self.headers = gitlab_manager.headers
        self.project_path = gitlab_manager.project_path
        self.default_branch = gitlab_manager.default_branch
        self.repo_folder = gitlab_manager.repo_folder
        self.gitlab_namespace = gitlab_manager.gitlab_namespace
        self.branch_roles = gitlab_manager.branch_roles

    def initialize_repository(self):
        print(f"🚀 Initializing repository structure for {self.gitlab_namespace}/{self.repo_folder}")
        try:
            self._enforce_main_branch()
            self._create_initial_branches()
            self._create_initial_files()
            self._setup_security_scanning()
            self._enable_cicd_features()
            self._setup_branch_protection()
            self._generate_readme()
            print("✅ Repository initialization completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Repository initialization failed: {e}")
            return False

    def _create_initial_branches(self):
        """Create the standard Git flow branches."""
        print("📝 Creating initial branches...")
        required_branches = [
            self.branch_roles["staging"],
            self.branch_roles["development"]
        ]
        for branch in required_branches:
            try:
                self.mgr.ensure_branch_exists(branch_name=branch, ref=self.default_branch)
                print(f"   ✅ Branch '{branch}' ready")
            except Exception as e:
                print(f"   ❌ Failed to create branch '{branch}': {e}")
                raise

    def _create_initial_files(self):
        print("📁 Creating initial files and folders...")
        proj = self.project_path.replace('/', '%2F')
        mapping_content = self._generate_mapping_file_content()
        self.mgr._push_file(proj, "branch_to_workspace.yaml", mapping_content, branch=self.default_branch)
        print("   ✅ Created branch_to_workspace.yaml")
        security_readme = self._generate_security_readme()
        self.mgr._push_file(proj, "SECURITY.md", security_readme, branch=self.default_branch)
        print("   ✅ Created SECURITY.md")
        config_placeholder = "# Pipeline configurations will be stored here"
        self.mgr._push_file(proj, "config/.gitkeep", config_placeholder, branch=self.default_branch)
        print("   ✅ Created config/ folder")
        code_placeholder = "# Pipeline code will be stored here"
        self.mgr._push_file(proj, "code/.gitkeep", code_placeholder, branch=self.default_branch)
        print("   ✅ Created code/ folder")

    def _setup_security_scanning(self):
        print("🔒 Setting up security scanning...")
        namespace_parts = self.gitlab_namespace.lower().split('/')
        if 'alg' in namespace_parts:
            corporate_group = 'alg'
        elif 'pin' in namespace_parts:
            corporate_group = 'pin'
        elif 'ucg' in namespace_parts:
            corporate_group = 'ucg'
        else:
            corporate_group = 'corp'
        gitlab_ci_content = self._generate_gitlab_ci_content(corporate_group)
        proj = self.project_path.replace('/', '%2F')
        self.mgr._push_file(proj, ".gitlab-ci.yml", gitlab_ci_content, branch=self.default_branch)
        print(f"   ✅ Created .gitlab-ci.yml with {corporate_group.upper()} corporate templates")
        
    def _generate_security_readme(self) -> str:
            """Generate SECURITY.md content with scanning information."""
            return """# Security Scanning

    This repository includes automated security scanning via GitLab CI/CD.

    ## Enabled Scanners

    - **SAST (Static Application Security Testing)**: Scans code for security vulnerabilities
    - **Dependency Scanning**: Checks for known vulnerabilities in dependencies
    - **Secret Detection**: Identifies committed secrets, tokens, and credentials
    - **Code Quality**: Analyzes code quality and maintainability

    ## Vulnerability Reports

    - **Repository Level**: Available in GitLab Security Dashboard
    - **JDP Tool**: http://git-scan-report.dev.is.autodatacorp.org (requires VPN)

    ## Remediation Timeline

    | Severity | Action Required |
    |----------|----------------|
    | Critical | Patch within 24hrs |
    | High | Patch within 2 weeks |
    | Medium | 45-60 days |
    | Low | 90 days |
    | Informational | Review as necessary |

    ## Security Policies

    See JDP Security Policy - Vulnerability Management Standard for complete guidelines.
    """
    
    def _generate_gitlab_ci_content(self, corporate_group: str) -> str:
        # Use configured branch names
        main = self.branch_roles["production"]
        staging = self.branch_roles["staging"]
        dev = self.branch_roles["development"]
        return f"""# GitLab CI/CD Configuration with Security Scanning
# Auto-generated by GitLabManager

include:
  - project: "{corporate_group}/pipelines/common"
    ref: "{main}"
    file:
      - "Stages.Templates.gitlab-ci.yml"
      - "Settings.gitlab-ci.yml"
      - "Basic.Templates.gitlab-ci.yml"

# Security scanning stages
stages:
  - prereq:before
  - prereq
  - prereq:after
  - bake:before
  - bake
  - bake:after
  - containerize:before
  - containerize
  - containerize:after
  - test:before
  - test
  - test:after
  - deploy:before
  - deploy
  - deploy:after
  - cleanup:before
  - cleanup
  - cleanup:after

# Security scanning jobs
sast:
  stage: test
  script:
    - echo "SAST scanning enabled via corporate templates"
  only:
    - merge_requests
    - {main}
    - {staging}

dependency_scanning:
  stage: test
  script:
    - echo "Dependency scanning enabled via corporate templates"
  only:
    - merge_requests
    - {main}
    - {staging}

secret_detection:
  stage: test
  script:
    - echo "Secret detection enabled via corporate templates"
  only:
    - merge_requests
    - {main}
    - {staging}

code_quality:
  stage: test
  script:
    - echo "Code quality scanning enabled via corporate templates"
  only:
    - merge_requests
    - {main}
    - {staging}

# Custom job for pipeline deployment
deploy_pipelines:
  stage: deploy
  script:
    - echo "Deploy AIC pipelines using GitLabManager"
    - python -c "from main import GitLabManager; print('GitLabManager deployment ready')"
  only:
    - {main}
    - {staging}
  when: manual
"""

    def _enable_cicd_features(self):
        print("⚙️  Enabling CI/CD features...")
        try:
            url = f"{self.gitlab_base}/projects/{self.project_path}"
            payload = {
                "builds_enabled": True,
                "issues_enabled": True,
                "merge_requests_enabled": True,
                "wiki_enabled": False,
                "snippets_enabled": False,
                "security_and_compliance_enabled": True,
                "container_registry_enabled": False
            }
            response = requests.put(url, headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                print("   ✅ CI/CD features enabled")
            else:
                print(f"   ⚠️  Could not enable all CI/CD features: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  Could not enable CI/CD features: {e}")

    def _generate_mapping_file_content(self) -> str:
        # Use configured branch names
        main = self.branch_roles["production"]
        staging = self.branch_roles["staging"]
        dev = self.branch_roles["development"]
        return f"""mapping:
  {main}: ProductionWorkspace
  {staging}: QAWorkspace
  {dev}: DevWorkspace
"""

    def _enforce_main_branch(self):
        # Use configured production branch
        main = self.branch_roles["production"]
        url = f"{self.gitlab_base}/projects/{self.project_path}"
        resp = requests.get(url, headers=self.headers, timeout=30)
        resp.raise_for_status()
        project = resp.json()
        current_default = project.get('default_branch', main)

        if current_default == main:
            print(f"Default branch is already '{main}'.")
        else:
            print(f"Creating '{main}' from '{current_default}'...")
            create_url = (
                f"{self.gitlab_base}/projects/{self.project_path}/repository/branches"
                f"?branch={main}&ref={current_default}"
            )
            c = requests.post(create_url, headers=self.headers, timeout=30)
            if c.status_code not in (201, 409):
                raise RuntimeError(f"Failed to create '{main}' from '{current_default}': {c.text}")
            print(f"Created '{main}' from '{current_default}'.")
            print(f"Setting '{main}' as the default branch...")
            set_default_url = f"{self.gitlab_base}/projects/{self.project_path}"
            payload = {"default_branch": main}
            r = requests.put(set_default_url, headers=self.headers, json=payload, timeout=30)
            if r.status_code != 200:
                raise RuntimeError(f"Failed to set '{main}' as default branch: {r.text}")
            print(f"Set '{main}' as the default branch.")
            print(f"Protecting '{main}' branch...")
            protect_url = f"{self.gitlab_base}/projects/{self.project_path}/protected_branches"
            payload = {
                "name": main,
                "push_access_level": 30,
                "merge_access_level": 30
            }
            p = requests.post(protect_url, headers=self.headers, json=payload, timeout=30)
            if p.status_code not in (201, 409):
                print(f"Warning: Could not protect '{main}' branch: {p.text}")
            else:
                print(f"Protected '{main}' branch.")
            print(f"Deleting original branch '{current_default}'...")
            del_url = f"{self.gitlab_base}/projects/{self.project_path}/repository/branches/{quote_plus(current_default)}"
            d = requests.delete(del_url, headers=self.headers, timeout=30)
            if d.status_code in (200, 204, 404):
                print(f"Deleted branch '{current_default}'.")
            else:
                print(f"Warning: Could not delete branch '{current_default}': {d.text}")
        self.default_branch = main

    def _setup_branch_protection(self):
        print("🛡️  Setting up branch protection...")
        protection_settings = {
            "push_access_level": 30,
            "merge_access_level": 30
        }
        for branch in [
            self.branch_roles["production"],
            self.branch_roles["staging"],
            self.branch_roles["development"]
        ]:
            try:
                url = f"{self.gitlab_base}/projects/{self.project_path}/protected_branches"
                payload = {
                    "name": branch,
                    "push_access_level": protection_settings["push_access_level"],
                    "merge_access_level": protection_settings["merge_access_level"]
                }
                response = requests.post(url, headers=self.headers, json=payload, timeout=30)
                if response.status_code in (201, 409):
                    print(f"   ✅ Protected branch '{branch}'")
            except Exception as e:
                print(f"   ⚠️  Could not protect branch '{branch}': {e}")

    def _generate_readme(self) -> bool:
        print("📝 Generating README.md...")
        project_name = self.repo_folder.replace('-', ' ').title()
        namespace_parts = self.gitlab_namespace.strip('/').split('/')
        company_name = namespace_parts[0].title() if namespace_parts else "Your Company"
        team_path = namespace_parts[1] if len(namespace_parts) > 1 else "team"
        readme_content = self._generate_readme_template(
            project_name=project_name,
            company_name=company_name,
            team_path=team_path,
            repo_folder=self.repo_folder,
            gitlab_namespace=self.gitlab_namespace,
            branch_roles=self.branch_roles
        )
        try:
            proj = self.project_path.replace('/', '%2F')
            self.mgr._push_file(proj, "README.md", readme_content, branch=self.default_branch)
            print(f"   ✅ Generated README.md for {project_name}")
            return True
        except Exception as e:
            print(f"   ❌ Failed to generate README.md: {e}")
            return False

    def _generate_readme_template(self, **kwargs) -> str:
        # Use branch_roles for table and examples
        br = kwargs['branch_roles']
        return f'''# {kwargs['project_name']} - GitLab AIC Integration

AIC pipeline management and GitLab integration for {kwargs['project_name']}

## 🚀 Quick Start

### Repository has been initialized by the `initialize_repository` command.

### 1. Edit branch_to_workspace.yaml File

- Click on File
- Click Edit -> Single File
- Replace workspace names as required 
- Commit changes

**Example:**
```yaml
mapping:
  {br["production"]}: PIN FUSION 2.0
  {br["staging"]}: PIN FUSION 2.0 QA
  {br["development"]}: PIN FUSION 2.0 DEV
```

### 2. Create Manager Instances

```python
from aic import AIC

# Set up AIC instances for different environments
aic_prod = AIC(
    api_key="your-aic-key",
    project="{kwargs['repo_folder']}",
    workspace="ProductionWorkspace",
    pipelines=['PIPELINE_1', 'PIPELINE_2']
)

aic_qa = AIC(
    api_key="your-aic-key", 
    project="{kwargs['repo_folder']}",
    workspace="QAWorkspace",
    pipelines=['PIPELINE_1', 'PIPELINE_2']
)

# Create GitLab managers
mgr_prod = GitLabManager(
    aic_instance=aic_prod,
    gitlab_token="your-gitlab-token",
    gitlab_namespace="{kwargs['gitlab_namespace']}",
    repo_folder="{kwargs['repo_folder']}"
)

mgr_qa = GitLabManager(
    aic_instance=aic_qa,
    gitlab_token="your-gitlab-token", 
    gitlab_namespace="{kwargs['gitlab_namespace']}",
    repo_folder="{kwargs['repo_folder']}"
)
```

### 3. Start initial code sync

Commence the initial workspace code sync. **NOTE:** You will be prompted for confirmation upon writing to production branches.
```python
# Push pipeline configurations to GitLab
mgr_prod.push_to_git()
```

Repeat as needed for any other workspaces.

### 4. Additional Workspaces

Any additional workspaces can be mapped to GitLab as its own branch and will not be included in the overall GIT flow. This will allow users to maintain additional environments on GIT but separate any development or deployments. i.e Creating a clone of Production for client integration testing.

These additional workspaces will map to their respective slugged workspace name and will be limited to that branch:

**Example:** `PIN FUSION 2.0 INTG TESTING` -> `pin-fusion-2-0-intg-testing` 

## 📚 Repository Structure

This repository follows the standard AIC-GitLab integration structure:

```
{kwargs['repo_folder']}/
├── README.md                      # This file
├── branch_to_workspace.yaml       # Branch-workspace mappings
├── SECURITY.md                    # Security scanning documentation
├── .gitlab-ci.yml                # CI/CD pipeline configuration
├── config/                       # Pipeline JSON configurations
│   ├── .gitkeep
│   └── *.json                    # AIC pipeline configurations
└── code/                         # Extracted code files
    ├── .gitkeep
    └── pipeline-name/
        ├── *.py                  # PySpark scripts
        └── *.sql                 # SQL queries
```

## 🌳 Git Flow

This repository uses the following branch structure:

| Branch | Purpose | AIC Workspace | Description |
|--------|---------|---------------|-------------|
| `{br["production"]}` | Production | ProductionWorkspace | Live production pipelines |
| `{br["staging"]}` | Integration | StagingWorkspace | Testing and integration |
| `{br["development"]}` | Development | DevWorkspace | Active development |
| `feature/*` | Features | DevWorkspace | New feature development |
| `release/*` | Releases | StagingWorkspace | Release preparation |
| `hotfix/*` | Hotfixes | ProductionWorkspace | Emergency fixes |

## 🔄 Common Workflows

### Feature Development

To develop a feature or new code implementation, complete all required development on the {br["development"]} workspace. Once completed, sync the changes to the {br["development"]} branch
```python
aic_qa = AIC(
    ...
    pipelines=['UPDATED_PIPELINE']
)
mgr_dev = GitLabManager(...)
mgr_dev.push_to_git()
```

Once the {br["development"]} environment has the required changes, create a feature branch:

```python
# Start new feature
mgr_dev.create_feature_branch("PINOPS-1431")
```

A feature branch has now been created (and linked to a respective ticket in JIRA) and that branch has been checked out as current branch.

Create merge request

```python
mgr_dev.create_merge_request(
    title="Add customer segmentation pipeline",
    description="New ML pipeline for customer analysis",
)
```

Once the merge request has been resolved, the {br["staging"]} branch will now have the updated code and will require deployment:

```python
mgr_qa = GitLabManager(...) #Create the object AFTER pushes/deployments to capture new changes
mgr_qa.deploy_pipelines()
```

### Release Process
Similarly for release branches, save changes to staging/qa then create the objects to capture new code
```python
aic_qa = AIC(...)
mgr_qa = GitLabManager(aic_qa, ....)
# Create release branch, checks out the branch
mgr_qa.create_release_branch("v1.2.0")

# Create production merge request, checks out original qa branch
mgr_qa.create_merge_request(...)

# Deploy in QA workspace
mgr_prod = GitLabManager(aic_prod, ...)
mgr_prod.deploy_pipelines()
```

### Hotfix Process

Hotfix process will be different than both the release and feature process. The purpose of the hotfix functionality is not to automate the deployments, but to create an audit trail of changes made to production. 

The biggest factor is that all required changes will be done **PRIOR** to any GitLabManager operations. Once production hotfix has been written, create the production AIC instance to capture this new code. If instance is created prior to the actual change being made, the AIC python instance will not have the changes stored.

```python
# Create hotfix from production
mgr_prod = GitLabManager(...)
mgr_prod.create_hotfix_branch("fix-critical-bug")

# Push the new AIC changes to the HOTFIX branch (and not prod)
mgr_prod.push_to_git()

#Create a merge request to push hotfix changes to the production branch
mgr_prod.create_merge_request(...)
```

## 🔒 Security

This repository includes automated security scanning:

- **SAST** (Static Application Security Testing)
- **Dependency Scanning** 
- **License Compliance**
- **Secret Detection**

See `SECURITY.md` for detailed security guidelines.

## 📧 Email Notifications

Configure email notifications for deployment summaries:

```python
mgr = GitLabManager(
    aic_instance=aic,
    gitlab_token="token",
    gitlab_namespace="{kwargs['gitlab_namespace']}",
    repo_folder="{kwargs['repo_folder']}",
    email_recipients=["team@{kwargs['company_name'].lower()}.com"],
    email_sender="noreply@{kwargs['company_name'].lower()}.com"
)
```

## 🐛 Troubleshooting

### Common Issues

1. **Branch mapping errors**: Check `branch_to_workspace.yaml`
2. **Token expiration**: Run `mgr.check_token_expiration()`
3. **Push restrictions**: Use proper Git flow branches
4. **Deployment failures**: Verify workspace mappings

**Maintained by Dylan Doyle** | **Last Updated**: Auto-generated on repository initialization
'''