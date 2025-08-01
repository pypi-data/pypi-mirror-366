import requests
import json 
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class DatasetConverter:
    
    def __init__(self, api_key, project, workspace, target_workspace=None, qa=False):
        self.base_url = 'https://prod.jdpower.ai/apis/core/v1' if not qa else 'https://aic.qa.jdpower.com/apis/core/v1'
        self.api_key = api_key
        self.headers = {
            'accept': '*/*',
            'api-key': api_key,
            'Content-Type': 'application/json'
        }
        self.project = project
        self.workspace = workspace
        self.project_id = self.get_project_id(project)
        self.workspace_id = self.get_workspace_id()
        if target_workspace:
            self.target_workspace = target_workspace
            self.target_workspace_id = self.get_target_workspace_id()
            print(f'TARGET WORKSPACE INITIATED. POPULATING TABLE LIST FROM {target_workspace}')
        self.tables = pd.DataFrame()
        self.pop_tables(self.target_workspace_id if target_workspace else self.workspace_id)
    
    def get_project_id(self, project_name):
        url = f"{self.base_url}/projects"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        for obj in response.json():
            if obj['name'] == project_name:
                return obj['$id']
        print(f'Projects found: {" ,".join([project["name"] for project in response.json()])}')
        raise Exception(f'No project with name {project_name} found')

    def get_workspace_id(self):
        url = f"{self.base_url}/projects/{self.project_id}/workspaces"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        for obj in response.json():
            if obj['name'] == self.workspace:
                return obj['$id']
        print(f'Workspaces found: {" ,".join([workspace["name"] for workspace in response.json()])}')
        raise Exception(f'No workspace with name {self.workspace} found')
    
    def get_target_workspace_id(self):
        url = f"{self.base_url}/projects/{self.project_id}/workspaces"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        for obj in response.json():
            if obj['name'] == self.target_workspace:
                return obj['$id']
        print(f'Workspaces found: {" ,".join([workspace["name"] for workspace in response.json()])}')
        raise Exception(f'No workspace with name {self.target_workspace} found')
        
    def get_datasets(self, workspace_id):
        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{workspace_id}/datasets"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        datasets = [{'name': obj.get('name', ''), 'id': obj.get('$id', '')} for obj in response.json()]
        return datasets

    def get_tables(self, dataset, workspace_id):
        table_list = []
        dataset_id = dataset['id']
        dataset_name = dataset['name']
        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{workspace_id}/datasets/{dataset_id}/tables"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        for obj in response.json():
            name = obj['name']
            id = obj['$id']
            table_list.append({'dataset_name': dataset_name, 'dataset_id': dataset_id, 'table_name': name})
        return table_list
    
    def pop_tables(self, workspace_id):
        master_list = []
        datasets = self.get_datasets(workspace_id)

        # Use ThreadPoolExecutor to fetch tables concurrently
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.get_tables, dataset, workspace_id): dataset['name'] for dataset in datasets}
            for future in as_completed(futures):
                dataset_name = futures[future]
                try:
                    table_list = future.result()
                    master_list.extend(table_list)
                except Exception as e:
                    print(f"Error fetching tables for dataset {dataset_name}: {e}")
        
        self.tables = pd.DataFrame(master_list)
    
    def fetch_pipeline_config(self, pipeline_name):
        pipeline = next((p for p in self.get_pipelines() if p['name'] == pipeline_name), None)
        if not pipeline:
            print(f"Pipeline {pipeline_name} not found.")
            return None
        
        id = pipeline['id']
        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{self.workspace_id}/jobs/{id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            return {'name': pipeline_name, 'jobConfig': data['jobConfig'], 'id': data['jobConfig']['$id']}
        else:
            print(f'Failed to fetch {pipeline_name}: {response.status_code}')
            return None
    
    def get_pipelines(self):
        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{self.workspace_id}/jobs"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return [{'name': obj.get('title', 'NO TITLE'), 'id': obj['$id']} for obj in response.json().get('jobs', [])]

    def create_pipeline_branch(self, config):
        job_id = config.get('id')
        job_config = config['jobConfig']
        name = config['name']
        url = f"{self.base_url}/projects/{self.project_id}/workspaces/{self.workspace_id}/interactive-pipeline/{job_id}/branches"
        branch_name = f"CONVERTED_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        payload = {
            'name': branch_name,
            'config': job_config
        }

        try:
            response = requests.put(url, headers=self.headers, json=payload)
            response.raise_for_status()
            print(f"Successfully created a new branch for the pipeline: {name}")
        except requests.exceptions.HTTPError as err:
            print(f'HTTP error occurred while creating branch for pipeline {name}: {err}')
            print(f'Status Code: {response.status_code}')
            print(f'Response Text: {response.text}')
        except Exception as err:
            print(f'Other error occurred while creating branch for pipeline {name}: {err}')
        return response

    def convert(self, pipelines):
        """
        Process and update pipelines by fetching their configuration, replacing placeholders, 
        and pushing the updated configuration to a new branch.
        """
        for pipeline_name in pipelines:
            pipeline_config = self.fetch_pipeline_config(pipeline_name)
            if pipeline_config:
                print(f"Processing pipeline: {pipeline_name}")
                processed_config = self.replace_placeholders(pipeline_config)
                processed_config = self.replace_source_stages_with_documentation(processed_config)
                self.create_pipeline_branch(processed_config)
            else:
                print(f"Failed to fetch pipeline: {pipeline_name}")

    def replace_placeholders(self, config):
        """
        Replace placeholders in the given configuration with actual table names.
        """
        audit_log = []

        def replace_in_value(value):
            """
            Replace a placeholder value with the full table name if it matches one in the master table.
            """
            if isinstance(value, str) and value in self.tables['table_name'].values:
                dataset_name = self.tables.loc[self.tables['table_name'] == value, 'dataset_name'].values[0]
                full_table_name = f"${{{dataset_name}.{value}}}"
                audit_log.append(f"- Replaced placeholder `{value}` with `{full_table_name}`.")
                return full_table_name
            return value

        def recursive_replace(data):
            """
            Recursively replace placeholders in dictionaries or lists.
            """
            if isinstance(data, dict):
                return {key: recursive_replace(replace_in_value(value)) for key, value in data.items()}
            elif isinstance(data, list):
                return [recursive_replace(replace_in_value(item)) for item in data]
            else:
                return replace_in_value(data)

        updated_config = recursive_replace(config)
        self.audit_log = "\n".join(audit_log)  # Store the audit log in markdown format
        return updated_config

    def replace_source_stages_with_documentation(self, config):
        """
        Replace source stages within jobConfig with a documentation task summarizing the changes made.
        """
        documentation_task = {
            "description": "Documentation Task",
            "tasks": [{
                "runType": "SOURCE",
                "description": "Summary of Placeholder Replacements",
                "id": "DOC_TASK",
                "type": "DOCUMENTATION",
                "config": {
                    "tables":[{
                        "name":"DOC_TASK"
                    }],
                    "documentationText": f"# Audit Log of Replacements\n\n{self.audit_log}"
                }
            }],
            "stageId": "DOC_STAGE"
        }

        # Navigate into jobConfig to replace source stages
        if "jobConfig" in config:
            job_config = config["jobConfig"]
            
            if "sourceStage" in job_config:
                # Filter out only 'DATASET' type source tasks and keep others intact
                job_config["sourceStage"]["tasks"] = [task for task in job_config["sourceStage"]["tasks"] if task['type'] != 'DATASET']
                
                # Add documentation task if any dataset tasks were removed
                if job_config["sourceStage"]["tasks"] != documentation_task["tasks"]:
                    print("Adding documentation task for replacements in source stages.")
                    job_config["sourceStage"]["tasks"].append(documentation_task['tasks'][0])
            elif "stages" in job_config:
                for stage in job_config["stages"]:
                    if stage.get("runType") == "SOURCE" and any(task['type'] == 'DATASET' for task in stage.get('tasks', [])):
                        print(f"Modifying source stage: {stage.get('stageId')}")
                        # Retain non-DATASET tasks
                        stage["tasks"] = [task for task in stage["tasks"] if task['type'] != 'DATASET']
                        # Append the documentation task
                        stage["tasks"].append(documentation_task['tasks'][0])
        else:
            print("No jobConfig found in the provided configuration.")
        
        return config
