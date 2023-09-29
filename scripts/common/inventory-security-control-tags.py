import os
import subprocess
import json
import yaml
import tempfile

def search_yaml_files(folder):
    yaml_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".yaml"):
                yaml_files.append(os.path.join(root, file))
    return yaml_files

def parse_yaml_file(file, kind):
    resources = []
    cluster_resources = []
    with open(file, "r") as f:
        yaml_data = f.read()

    resources = yaml_data.split('---\n')
    for resource in resources:
      if len(resource) == 0:
          continue

      # Parse the resource into a dictionary
      resource_dict = yaml.safe_load(resource)
      if resource_dict is None:
          continue

      if 'apiVersion' not in resource_dict:
        print("---no api version")
        continue

      # Ignore resources that have a key managed-by-cnrm inside the metadata.annotations dictionary
      if resource_dict["kind"] == kind:
        print("-----------------------------------------------")
        print("---found resource that is a " + kind)
        print(resource)
        cluster_resources.append(resource)
      else:
        continue

    return cluster_resources

# Input parameters
tier1_repo_url = input("Enter tier 1 repo url: ")

#temp_folder = tempfile.TemporaryDirectory()
temp_folder = "/tmp/testing"
#print('created temporary directory ', temp_folder.name)

# Clone tier1 repo
# subprocess.run(["git", "clone", tier1_repo_url, temp_folder + "/dl-gcp-env-tier1-consolidated"])

project_id = input("Enter tier 1 repo project id: ") # TODO: not hardcoded. get it from bootstrap .env automatically

# Query config sync inventory
config_sync_output = subprocess.check_output(
    ["gcloud", "alpha", "anthos", "config", "sync", "repo", "list", "--project", project_id, "--format=json"]
)

# Parse config sync output and create a dictionary of config controllers
kcc_config_syncs = json.loads(config_sync_output.decode("utf-8"))

#sebremove
formatted_json = json.dumps(kcc_config_syncs, indent=4)
print(formatted_json)
#sebremove/

# Loop through config controllers
for kcc_config_sync in kcc_config_syncs:
    # Add repo_name, repo_url, folder, branch and revision fields to kcc_config_syncs dictionary
    kcc_config_sync.update({'repo_name': kcc_config_sync["source"].split("_git/")[1].split("//")[0] })
    kcc_config_sync.update({'repo_url': kcc_config_sync["source"].split(kcc_config_sync["repo_name"])[0]+kcc_config_sync["repo_name"] })
    kcc_config_sync.update({'folder': kcc_config_sync["source"].split(kcc_config_sync["repo_name"] + "/")[1].split("@")[0] })
    kcc_config_sync.update({'branch': kcc_config_sync["source"].split(kcc_config_sync["folder"] + "@")[1].split(":")[0] })
    kcc_config_sync.update({'revision': kcc_config_sync["source"].split("@"+kcc_config_sync["branch"]+":")[1] })
 
    # Clone the repo + cd to it
    path = temp_folder + "/configcontroller/" + kcc_config_sync["namespace"] + "/" + kcc_config_sync["name"] + "/" + kcc_config_sync["repo_name"]
    subprocess.run(["git", "clone", kcc_config_sync["repo_url"], path])
    os.chdir(path)

    # Check out the specified revision/branch 
    if kcc_config_sync["revision"] == "HEAD": #sebnotes: I think that every repo from dl-consolidated-mgmt are HEAD. Will need to test later with another repo that has different revisions such as gcp-env-tier-1
        subprocess.run(["git", "checkout", kcc_config_sync["branch"]])
    else:
        subprocess.run(["git", "checkout", kcc_config_sync["revision"]])

#sebremove
formatted_json = json.dumps(kcc_config_syncs, indent=4)
print(formatted_json)
#sebremove/

# List for Kubernetes clusters
k8s_clusters_raw = []

# For each configcontroller repo in my dictionary: 
# search in config controller folder for resource "kind: ContainerCluster"
for kcc_config_sync in kcc_config_syncs:
    # Search for YAML files in the specified folder
    path = temp_folder + "/configcontroller/" + kcc_config_sync["namespace"] + "/" + kcc_config_sync["name"] + "/" + kcc_config_sync["repo_name"] + kcc_config_sync["folder"]
    print(path)
    yaml_files = search_yaml_files(path)

    # Parse each YAML file and store matching clusters
    for yaml_file in yaml_files:
        k8s_clusters_raw.extend(parse_yaml_file(yaml_file, "ContainerCluster"))

print("k8s_clusters_raw lenght: " + str(len(k8s_clusters_raw)))

k8s_clusters = []
for k8s_cluster_raw in k8s_clusters_raw:
    k8s_clusters.append(yaml.safe_load(k8s_cluster_raw))


for k8s_cluster in k8s_clusters:
    print(k8s_cluster["metadata"]["annotations"]["cnrm.cloud.google.com/project-id"])

    # gcloud alpha container fleet config-management status --project=${Kubernetes cluster.project-id} –format=yaml (or json if you find it easier)
    # subprocess.run(["gcloud", "alpha", "container", "fleet", "config-management", "status", "--project=", k8s_cluster["metadata"]["annotations"]["cnrm.cloud.google.com/project-id"], "--format=json"])
    config_sync_output = subprocess.check_output(
        ["gcloud", "alpha", "container", "fleet", "config-management", "status", "--project=" + k8s_cluster["metadata"]["annotations"]["cnrm.cloud.google.com/project-id"], "--format=json"] # Note: command does not give us enough data... we want the list of config sync
    )
    k8s_config_syncs = json.loads(config_sync_output.decode("utf-8"))
    # dave
    # gcloud alpha anthos config sync repo list --project 
    #sebremove
    formatted_json = json.dumps(k8s_config_syncs, indent=4)
    print(formatted_json)
    #sebremove/

    # mkdir kubernetes cluster.project_id/cluster-name
    # Extract from source the following values repoName, folder,  branch, revision and create a config controller dictionnary (sebnote: another cc dict?)
    # Git clone repo
    # cd repo
    # if revision = HEAD ? git checkout branch : git checkout revision


# Inventory of security control tags

# sebremove: Useless user input to prevent script from ending (for debug)
completeScript = input("Enter something to complete the script: ")
# sebremove/

#temp_folder.cleanup()