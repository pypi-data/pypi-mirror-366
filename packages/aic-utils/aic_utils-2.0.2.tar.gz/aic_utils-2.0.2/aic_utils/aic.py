import requests
import json 
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import re

class AIC():
    timestamp = datetime.today().strftime('%Y%m%d')
    
    def __init__(self, api_key, project, workspace, pipelines=[], qa=False):
        self.base_url = 'https://prod.jdpower.ai/apis/core/v1' if not qa else 'https://aic.qa.jdpower.com/apis/core/v1'
        self.api_key = api_key
        self.headers = {
            'accept': '*/*',
            'api-key': api_key,
            'Content-Type': 'application/json'
        }
        self.project_id = self.get_project_id(project)
        self.workspace = workspace
        self.workspace_id = self.get_workspace_id(workspace)
        # self.get_data()
        self.pipelines = self.pop_pipelines()
        self.pipeline_configs = self.pop_pipeline_config(pipelines)

    
    def get_data(self):
        print(f'Project ID: {self.project_id}')
        print(f'Workspace ID: {self.workspace_id}')
        # print(f'Drive ID: {self.drive_id}')
    
    def list_pipeline_files(self, subpath: str = None):
        """
        List all .json files in the current env branch.
        If subpath="config", list only files under config/.
        Otherwise, list only top‐level .json.
        """
        proj = self.project_path.replace('/', '%2F')
        params = {'ref': self.branch}
        if subpath:
            params['path'] = subpath

        url = f"{self.gitlab_base}/projects/{proj}/repository/tree"
        resp = requests.get(url, headers={'PRIVATE-TOKEN': self.gitlab_token}, params=params, timeout=30)
        resp.raise_for_status()

        # Only keep “blob” entries ending in .json
        return [ item['name']
                 for item in resp.json()
                 if item['type']=='blob' and item['name'].lower().endswith('.json') ]

    
    def get_config(self):
        return self.pipeline_configs
    
    
    def get_datasets(self):
        """Fetch all datasets within the current workspace."""
        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{self.workspace_id}/datasets"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Check for errors
        return response.json()  # Return the list of datasets

    
    def get_tables(self, dataset_id):
        """Fetch all tables within the specified dataset."""
        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{self.workspace_id}/datasets/{dataset_id}/tables"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Check for errors
        return response.json()  # Return the list of tables
    
    
    def get_project_id(self, project):
        url = f"{self.base_url}/projects"
        response = requests.get(url, headers=self.headers)
        for obj in response.json():
            if obj['name'] == project:
                return obj['$id']
        raise Exception(f'No project with name {project} found')
    

    def get_workspace_id(self, workspace):
        url = f"{self.base_url}/projects/{self.project_id}/workspaces"
        response = requests.get(url, headers=self.headers)
        for obj in response.json():
            if obj['name'] == workspace:
                return obj['$id']
        raise Exception(f'No workspace with name {workspace} found')
        

    def pop_pipelines(self):
        """
        Fetch and populate pipelines from the current workspace and store them in the instance's pipelines attribute.
        """
        pipelines = []
        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{self.workspace_id}/jobs"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Check for HTTP errors

        # Extract pipeline names and IDs
        for obj in response.json().get('jobs', []):
            pipeline_name = obj.get('title', 'NO TITLE')
            pipeline_id = obj.get('$id')
            pipelines.append({'name': pipeline_name, 'id': pipeline_id})

        self.pipelines = pipelines
        print(f"Loaded {len(pipelines)} pipelines from workspace '{self.workspace}'.")

        return pipelines

    
    def fetch_pipeline_config(self, pipeline, direct=False):
        """
        Fetch a single pipeline configuration. If `direct` is False, retrieve the pipeline ID from 
        the name. If `direct` is True, assume the pipeline dictionary has an `$id` field.
        """
        if direct:
            id = pipeline['$id']
        else:
            # Search for the pipeline ID using the pipeline name
            matching_pipeline = next((p for p in self.pipelines if p['name'] == pipeline['name']), None)
            if not matching_pipeline:
                raise KeyError(f"Pipeline with name '{pipeline['name']}' not found.")
            id = matching_pipeline['id']

        name = pipeline['name']
        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{self.workspace_id}/jobs/{id}"
        print(f'Retrieving config for {name}...')

        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            return {'name': name, 'jobConfig': data['jobConfig'], 'id': data['jobConfig']['$id']}
        else:
            print(f'Failed to fetch {name}: {response.status_code}')
            return None


    
    
    def pop_pipeline_config(self, pipelines):
        """
        Fetch configurations for the given pipelines in parallel.

        Args:
          pipelines: List of pipeline names to fetch, or ['*'] to fetch every pipeline.
        """
        # 1) Decide which pipelines to fetch
        if not pipelines:
            # nothing to fetch
            return []

        # wildcard = all
        if len(pipelines) == 1 and pipelines[0] == '*':
            to_fetch = self.pipelines
            missing = set()
        else:
            names = set(pipelines)
            to_fetch = [p for p in self.pipelines if p['name'] in names]
            found_names = {p['name'] for p in to_fetch}
            missing = names - found_names
            if missing:
                print(f"Warning: pipelines not found: {missing}. Creating dummy objects.")

        # 2) Parallel fetch for found pipelines
        configs = []
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.fetch_pipeline_config, pipeline): pipeline['name']
                for pipeline in to_fetch
            }
            for future in as_completed(futures):
                result = future.result()
                if result:
                    configs.append(result)
                else:
                    print(f"Failed to fetch config for {futures[future]}")

        # 3) Add dummy configs for missing pipelines
        for name in missing:
            dummy = {
                'name': name,
                'jobConfig': {
                    'stages': [],
                    'variables': [],
                    'sourceStage': {},
                    'sinkStage': {}
                },
                'id': None  # No ID yet, will be created on deploy
            }
            configs.append(dummy)

        return configs


#     @staticmethod
#     def push_source_code(AIC_source, AIC_target, pipelines=[], push_to_branch=False, replace_placeholders=False):
#         """
#         Overwrite pipeline configurations between a specified source and target environment 
#         and only for the specified pipelines, with an option to push to a new branch.

#         Args:
#             AIC_source: Instance of AIC representing the source environment configuration.
#             AIC_target: Instance of AIC representing the target environment configuration.
#             pipelines: List of pipeline names that should be processed for pushing configurations.
#             push_to_branch: Boolean indicating whether to push to a new branch instead of the main branch.
#             replace_placeholders: Boolean indicating whether to replace placeholders in the SQL queries.
#         """
#         if not pipelines:
#             raise ValueError("List of pipelines is empty. Please specify pipelines to push source code.")

#         def replace_sql_placeholders(pipeline_config, tables_dict):
#             """Replace placeholders in the SQL query with '`$DATASET:TABLE`' format."""
#             print(f"Checking for table names in pipeline: {pipeline_config['$id']}")  # Pipeline identifier

#             replacements = []  # To log the changes made

#             for stage in pipeline_config.get('stages', []):
#                 stage_name = stage.get('description', 'Unnamed Stage')

#                 for task in stage.get('tasks', []):
#                     task_name = task.get('description', 'Unnamed Task')
#                     task_type = task.get('type', 'Unknown')

#                     if task_type == 'SQL':
#                         sql_config = task.get('config', {})
#                         sql_query = sql_config.get('query', '')

#                         if sql_query:
#                             print(f"Processing SQL query in task '{task_name}' of stage '{stage_name}'")

#                             # Find all placeholders in the SQL query
#                             placeholders_in_query = set(re.findall(r'\$\{\s*([^\}]+)\s*\}', sql_query))

#                             for placeholder in placeholders_in_query:
#                                 placeholder_lower = placeholder.strip().lower()

#                                 if placeholder_lower in tables_dict:
#                                     original_full_placeholder = f"${{{placeholder}}}"
#                                     dataset_table = tables_dict[placeholder_lower]
#                                     replacement_placeholder = f"`${dataset_table}`"
#                                     sql_query = sql_query.replace(original_full_placeholder, replacement_placeholder)
#                                     replacements.append((original_full_placeholder, replacement_placeholder))
#                                     print(f"Replaced '{original_full_placeholder}' with '{replacement_placeholder}' in task '{task_name}'")

#                             task['config']['query'] = sql_query

#             return replacements  # Return the replacements log for documentation

#         def add_documentation_task_to_source_stage(pipeline_config, replacements):
#             if not replacements:
#                 return

#             documentation_text = "\n".join([f"Replaced {old} with {new}" for old, new in replacements])
#             documentation_task = {
#                 "description": "Audit Log for Placeholder Replacements",
#                 "runType": "SOURCE",
#                 "id": "audit_log",
#                 "type": "DOCUMENTATION",
#                 "stagedId": "documentation_stage",
#                 "config": {"documentationText": documentation_text, "tables": [{"name": "AUDIT_LOG"}]}
#             }

#             source_stage = pipeline_config.get('sourceStage')
#             if source_stage:
#                 source_stage['tasks'].append(documentation_task)
#             else:
#                 pipeline_config['sourceStage'] = {
#                     "description": "SOURCE STAGE",
#                     "tasks": [documentation_task]
#                 }

#         def fetch_tables(aic_instance):
#             datasets = aic_instance.get_datasets()
#             tables_dict = {}
#             for dataset in datasets:
#                 tables = aic_instance.get_tables(dataset['$id'])
#                 for table in tables:
#                     placeholder_no_dataset = table['name'].lower()
#                     replacement = f"{dataset['name']}:{table['name']}"
#                     tables_dict[placeholder_no_dataset] = replacement
#                     tables_dict[f"{dataset['name']}.{table['name']}".lower()] = replacement
#             return tables_dict

#         tables_dict = None
#         if replace_placeholders:
#             tables_dict = fetch_tables(AIC_source)

#         # Perform the push operation for each pipeline
#         for source_pipeline in AIC_source.pipeline_configs:
#             source_name = source_pipeline['name']
#             if source_name not in pipelines:
#                 continue

#             # Look for matching pipeline in the target environment
#             target_pipeline = next((p for p in AIC_target.pipeline_configs if p['name'] == source_name), None)

#             if target_pipeline:
#                 print(f"Updating existing pipeline in target workspace: {source_name}")
#                 target_pipeline['jobConfig'] = source_pipeline['jobConfig']
#             else:
#                 print(f"Pipeline '{source_name}' not found in target workspace. Creating new pipeline.")
#                 target_pipeline = {
#                     'name': source_name,
#                     'jobConfig': source_pipeline['jobConfig']
#                 }
#                 AIC_target.create_or_update_pipeline(AIC_target.workspace_id, target_pipeline)
#                 # Reload the target pipeline configs to reflect the new addition
#                 AIC_target.pipeline_configs = AIC_target.pop_pipelines()
#                 continue  # Skip to next pipeline since this one has just been created

#             if replace_placeholders and tables_dict:
#                 replacements = replace_sql_placeholders(target_pipeline['jobConfig'], tables_dict)
#                 add_documentation_task_to_source_stage(target_pipeline['jobConfig'], replacements)

#             # Update QA flag in target if applicable
#             for variable in target_pipeline['jobConfig']['variables']:
#                 if variable['id'] == 'QA':
#                     variable['value'] = 'True' if 'qa' in AIC_target.workspace.lower() else 'False'
#                     print(f"Setting QA variable for pipeline: {source_name}")

#             if push_to_branch:
#                 branch_name = f"PUSH_{datetime.now().strftime('%Y%m%d%H%M%S')}"
#                 print(f"Creating branch {branch_name} for pipeline: {source_name}")
#                 response = AIC_target.create_pipeline_branch(target_pipeline)
#                 if response:
#                     print(f"Successfully pushed to branch: {branch_name}")
#                 else:
#                     print(f"Failed to push to branch: {branch_name}")
#             else:
#                 print(f"Updating pipeline in target workspace: {source_name}")
#                 AIC_target.write_config_to_pipeline(target_pipeline)





    def write_config_to_pipeline(self, config):
        """
        Upsert (create or update) a pipeline via POST /jobs.
        Includes $id when updating an existing job.
        """
        job_config = config['jobConfig']
        # build payload
        payload = {
            # include the pipeline id so the server knows to update, not create
            **({'$id': config['id']} if config.get('id') else {}),
            'title':      config['name'],
            'stages':     job_config.get('stages', []),
            'variables':  job_config.get('variables', []),
            'sourceStage': job_config.get('sourceStage', {}),
            'sinkStage':   job_config.get('sinkStage', {}),
        }

        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{self.workspace_id}/jobs"
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            action = "Updated" if config.get('id') else "Created"
            print(f"{action} pipeline: {config['name']}")
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error on upserting pipeline {config['name']}: {err}")
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

    def create_pipeline_branch(self, config):
        """
        Create a new branch for the given pipeline configuration using a timestamp-based name format.

        Args:
            config: Dictionary containing the pipeline configuration and name.
        """
        # Extract necessary identifiers and job configuration details
        job_id = config.get('id')
        job_config = config['jobConfig']
        name = config['name']

        # Construct the URL for creating a new branch
        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{self.workspace_id}/interactive-pipeline/{job_id}/branches"

        # Generate a branch name using the current timestamp in the format YYYYMMDDHHMMSS
        branch_name = f"PUSH_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Prepare the payload using the job configuration
        payload = {
            'name': branch_name,
            'config': job_config  # Pass the entire job config as required
        }

        try:
            # Send the request to create a new branch
            response = requests.put(url, headers=self.headers, json=payload)
            response.raise_for_status()  # Check for HTTP errors
            print(f"Successfully created a new branch for the pipeline: {name}")
        except requests.exceptions.HTTPError as err:
            print(f'HTTP error occurred while creating branch for pipeline {name}: {err}')
            print(f'Status Code: {response.status_code}')
            print(f'Response Text: {response.text}')
        except Exception as err:
            print(f'Other error occurred while creating branch for pipeline {name}: {err}')

        return response
    

    def get_pipelines(self, workspace_id):
        """
        Retrieve all pipelines in the specified original
        workspace.

        Args:
            workspace_id (str): Workspace ID to retrieve pipelines from.
        """
        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{workspace_id}/jobs"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return [{'name': obj.get('title', 'NO TITLE'), 'id': obj['$id']} for obj in response.json().get('jobs', [])]
    

    def copy_pipelines(self, target_workspace_name, pipelines_to_copy):
        """
        Copy pipelines from the current workspace to the target workspace.

        Args:
            target_workspace_name (str): Name of the target workspace.
            pipelines_to_copy (list): List of pipeline names to copy.
        """
        # Get the target workspace ID using the workspace name
        target_workspace_id = self.get_workspace_id(target_workspace_name)

        # Fetch the existing pipelines in the target workspace
        target_pipelines = self.get_pipelines(target_workspace_id)
        target_pipeline_names = {pipeline['name']: pipeline['id'] for pipeline in target_pipelines}

        for pipeline_name in pipelines_to_copy:
            # Fetch the pipeline config from the source workspace
            pipeline = next((p for p in self.pipelines if p['name'] == pipeline_name), None)
            if not pipeline:
                print(f"Pipeline '{pipeline_name}' not found in the source workspace.")
                continue

            pipeline_config = self.fetch_pipeline_config(pipeline)

            if not pipeline_config:
                print(f"Failed to fetch configuration for pipeline: {pipeline_name}")
                continue

            # Use the unified create_or_update_pipeline method
            print(f"Copying pipeline '{pipeline_name}' to target workspace '{target_workspace_name}'.")
            self.create_or_update_pipeline(target_workspace_id, pipeline_config)



    def create_or_update_pipeline(self, workspace_id, pipeline_config):
        """
        Create or update a pipeline in the specified workspace.

        Args:
            workspace_id (str): Workspace ID where the pipeline will be created or updated.
            pipeline_config (dict): Configuration of the pipeline to be created or updated.
        """
        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{workspace_id}/jobs"

        # Construct the payload
        payload = {
            'title': pipeline_config['name'],
            'stages': pipeline_config['jobConfig'].get('stages', []),
            'variables': pipeline_config['jobConfig'].get('variables', []),
            'sourceStage': pipeline_config['jobConfig'].get('sourceStage', {}),
            'sinkStage': pipeline_config['jobConfig'].get('sinkStage', {}),
            # Include any other necessary fields
        }

        print(f"Attempting to create or update pipeline '{pipeline_config['name']}'")

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            print(f"Pipeline '{pipeline_config['name']}' created or updated successfully.")
        except requests.exceptions.HTTPError as err:
            if response.status_code == 409:  # Conflict, indicating pipeline already exists
                print(f"Pipeline '{pipeline_config['name']}' exists, attempting to update.")
                self.update_pipeline(workspace_id, pipeline_config['id'], pipeline_config)
            else:
                print(f'HTTP error occurred while creating or updating pipeline {pipeline_config["name"]}: {err}')
                print(f'Status Code: {response.status_code}')
                print(f'Response Text: {response.text}')

    # ─── In your AIC class ────────────────────────────────────────────────
    def update_pipeline(self, workspace_id, pipeline_id, pipeline_config):
        """
        Update an existing pipeline in the specified workspace via PUT /jobs/{id}.
        """
        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{workspace_id}/jobs/{pipeline_id}"
        payload = {
            'title':       pipeline_config['name'],
            'stages':      pipeline_config['jobConfig'].get('stages', []),
            'variables':   pipeline_config['jobConfig'].get('variables', []),
            'sourceStage': pipeline_config['jobConfig'].get('sourceStage', {}),
            'sinkStage':   pipeline_config['jobConfig'].get('sinkStage', {}),
        }

        try:
            response = requests.put(url, headers=self.headers, json=payload)
            response.raise_for_status()
            print(f"Pipeline '{pipeline_config['name']}' updated successfully.")
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error while updating {pipeline_config['name']}: {err}")
            print(f" Status: {response.status_code}\n Body:   {response.text}")


            
    def delete_branches(self, job_names):
        """
        Delete all interactive branches for the given list of job names.

        Args:
            job_names (list): List of job names for which to delete interactive branches.
        """
        for job_name in job_names:
            # Find the job ID for the given job name
            job = next((p for p in self.pipelines if p['name'] == job_name), None)
            if not job:
                print(f"Job '{job_name}' not found in workspace '{self.workspace}'.")
                continue
            job_id = job['id']

            # Get the list of branches for this job
            url = f"{self.base_url}/projects/{self.project_id}/workspaces/{self.workspace_id}/interactive-pipeline/{job_id}/branches"
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                branches = response.json()  # This should return a list, not a dict
                if not isinstance(branches, list):
                    print(f"Unexpected response format for job '{job_name}', skipping.")
                    continue

                if not branches:
                    print(f"No interactive branches found for job '{job_name}'.")
                    continue

                # Delete each branch
                for branch in branches:
                    branch_id = branch['$id']  # Assuming 'name' is the branch identifier
                    delete_url = f"{url}/{branch_id}"
                    try:
                        del_response = requests.delete(delete_url, headers=self.headers)
                        del_response.raise_for_status()
                        print(f"Deleted branch '{branch_id}' for job '{job_name}'.")
                    except requests.exceptions.HTTPError as err:
                        print(f"Failed to delete branch '{branch['name']}' for job '{job_name}': {err}")
            except requests.exceptions.HTTPError as err:
                print(f"Failed to get branches for job '{job_name}': {err}")

                
    def backup_pipelines(self, pipelines, base_folder='.', drive_name='backups'):
        """
        Creates a dated folder in the specified drive and uploads the pipeline configuration files,
        sending the file content directly in the request body.

        Args:
            base_folder (str): The base folder path where the dated folder will be created (e.g., './backup').
            pipelines (list): List of pipeline configurations or pipeline names to upload.
            drive_name (str): The name of the drive where the folder will be created (default is 'backups').
        """
        # Step 1: Get the drive ID for the 'backups' drive
        drive_id = self.get_drive_id_by_name(drive_name)

        if not drive_id:
            print(f"Drive '{drive_name}' not found. Aborting backup process.")
            return

        # Step 2: Generate a folder name based on the current date (YYYYMMDD)
        folder_name = datetime.today().strftime('%Y%m%d')
        backup_path = f"{base_folder}/{folder_name}"

        # Step 3: Create the folder in the drive
        url_create_folder = f"{self.base_url}/projects/{self.project_id}/workspaces/{self.workspace_id}/drives/{drive_id}/create-folder"
        payload = {"path": backup_path}

        try:
            response = requests.post(url_create_folder, headers=self.headers, json=payload)
            response.raise_for_status()
            print(f"Successfully created folder '{backup_path}' in the drive '{drive_name}'.")
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred while creating folder '{backup_path}': {err}")
            return

        # Step 4: Ensure each item in pipelines is a full pipeline config, not just a string (pipeline name)
        pipeline_configs = []
        for pipeline in pipelines:
            if isinstance(pipeline, str):  # If pipeline is a string (name), fetch its config
                # Fetch the pipeline by name to get the pipeline ID
                pipeline_obj = next((p for p in self.pipelines if p['name'] == pipeline), None)
                if not pipeline_obj:
                    print(f"Pipeline '{pipeline}' not found in the workspace.")
                    continue

                # Fetch the pipeline config using the correct ID
                pipeline_config = self.fetch_pipeline_config(pipeline_obj)
                if pipeline_config:
                    pipeline_configs.append(pipeline_config)
                else:
                    print(f"Failed to fetch configuration for pipeline: {pipeline}")
            else:
                pipeline_configs.append(pipeline)  # Already a full config

        # Step 5: Upload each pipeline configuration as file content in the request body
        for pipeline_config in pipeline_configs:
            file_name = f"{pipeline_config['name']}.json"
            file_content = json.dumps(pipeline_config['jobConfig'], indent=4)  # Convert pipeline config to JSON string

            # Prepare the query parameters
            upload_params = {
                "path": backup_path,
                "fileName": file_name
            }

            # URL for the upload
            upload_url = f"{self.base_url}/projects/{self.project_id}/workspaces/{self.workspace_id}/drives/{drive_id}/upload-file"

            # Adjust headers to include only required headers
            upload_headers = self.headers.copy()
            # Remove 'Content-Type' if set, or set it to 'application/octet-stream'
            upload_headers.pop('Content-Type', None)
            # Alternatively, you can set it explicitly if needed:
            # upload_headers['Content-Type'] = 'application/octet-stream'

            try:
                # Send the request with file content as data
                response = requests.post(
                    upload_url,
                    headers=upload_headers,
                    params=upload_params,
                    data=file_content.encode('utf-8')  # Encode the string to bytes
                )
                response.raise_for_status()
                print(f"Successfully uploaded pipeline config '{file_name}' to folder '{backup_path}'.")
            except requests.exceptions.HTTPError as err:
                print(f"HTTP error occurred while uploading '{file_name}': {err}")
                print(f"Response Text: {response.text}")
                continue

                
    def get_drive_id_by_name(self, drive_name):
        """
        Retrieves the drive ID for a given drive name (default 'backups') within the workspace.

        Args:
            drive_name (str): The name of the drive to search for (default is 'backups').

        Returns:
            str: The drive ID of the drive if found, None if not found.
        """
        # API endpoint to list drives in the workspace
        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{self.workspace_id}/drives"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            drives = response.json()

            # Search for the drive with the matching name
            for drive in drives:
                if drive['name'].lower() == drive_name.lower():
                    print(f"Found drive '{drive_name}' with ID: {drive['$id']}")
                    return drive['$id']

            print(f"No drive found with the name '{drive_name}'")
            return None
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred while retrieving drives: {err}")
            return None
