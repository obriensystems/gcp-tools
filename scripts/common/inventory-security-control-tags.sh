#!/bin/bash

# Bash safeties: exit on error, pipelines can't hide errors
set -o errexit
set -o pipefail
set -x

# Input parameter: URL of the tier1 repo (SEB: Is there a better way to have an input parameter?)
repo_url="https://gc-cpa@dev.azure.com/gc-cpa/iac-gcp-dev/_git/dl-gcp-env-tier1-consolidated"
repo_name="dl-gcp-env-tier1-consolidated"

# Clone the tier1 repo (SEB: tell it which folder to put it in)
git clone "$repo_url" ../tmp-workspace

# Set the path to the .env file (SEB: no prod folder in given repo?)
env_file="../tmp-workspace/bootstrap/dev/.env"

# Load environment variables from .env file
source "$env_file"

# Query Config Sync inventory (SEB: yaml vs json?)
config_sync_output=$(gcloud alpha anthos config sync repo list --project "${PROJECT_ID}" --format=json)

# Parse the JSON output to extract repo information
repo_info=$(echo "$config_sync_output" | jq -r '.[] | {repoName: .name, source: .source}')

# Loop through each repository
while IFS= read -r line; do
  repo_name=$(echo "$line" | jq -r '.name')
  # source_url=$(echo "$line" | jq -r '.source')
  
  # # Extract folder, branch, and revision from the source URL
  # folder=$(echo "$source_url" | awk -F'configcontroller/' '{print $2}' | awk -F'/' '{print $1}')
  # branch=$(echo "$source_url" | awk -F'[/:@]' '{print $(NF-1)}')
  # revision=$(echo "$source_url" | awk -F'@' '{print $NF}')

  # # Clone the repository
  # git clone "$repo_url/$folder"
  # cd "$folder"

  # # Checkout the specified branch or revision
  # if [ "$revision" == "HEAD" ]; then
  #   git checkout "$branch"
  # else
  #   git checkout "$revision"
  # fi

  # cd ..
done <<<"$repo_info"

# # Loop through each config controller repository
# for folder in */; do
#   if [ -d "$folder" ]; then
#     # Search for Kubernetes cluster resources
#     cluster_annotations=$(grep -r -e 'kind: ContainerCluster' "$folder" | grep -o -e 'metadata.annotations.project-id: .*')

#     # Capture project IDs and create a Kubernetes cluster dictionary
#     while IFS= read -r annotation; do
#       project_id=$(echo "$annotation" | cut -d ' ' -f 2)
#       cluster_name=$(echo "$folder" | sed 's:/$::')

#       # Create a directory for the Kubernetes cluster
#       mkdir -p "$project_id/$cluster_name"
      
#       # Clone the repository for the Kubernetes cluster
#       git clone "$repo_url/$folder"
#       cd "$folder"

#       # Checkout the specified branch or revision
#       if [ "$revision" == "HEAD" ]; then
#         git checkout "$branch"
#       else
#         git checkout "$revision"
#       fi

#       cd ..
#     done <<<"$cluster_annotations"
#   fi
# done

# # Generate security controls inventory using the modified script
# # Modify the 'inventory-controls.py' script to produce tables as needed
# python inventory-controls.py

# # Store inventory in a repository
# # Clone the private documentation repository
# git clone https://example.com/gcp-private-documentation gcp-documentation-private

# # Navigate to the repository
# cd gcp-documentation-private

# # Create a new branch
# git checkout -b new-security-controls

# # Copy the generated security controls Markdown file
# cp /path/to/generated/security-controls.md .

# # Add and commit changes
# git add security-controls.md
# git commit -m "Update security controls inventory"
# git push origin new-security-controls
