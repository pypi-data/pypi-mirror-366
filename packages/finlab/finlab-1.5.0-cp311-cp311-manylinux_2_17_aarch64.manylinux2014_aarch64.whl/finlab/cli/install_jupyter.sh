#!/bin/sh

# Function to check the success of each step
check_success() {
    if [ $? -ne 0 ]; then
        echo "An error occurred during the last step. Exiting."
        exit 1
    fi
}


# Step 2: Install JupyterLab Language Server Protocol (LSP) and Python LSP Server
conda install -c conda-forge jupyterlab --upgrade
conda update jupyterlab
check_success

conda install -c conda-forge jupyterlab-lsp -y
check_success

conda install -c conda-forge python-lsp-server -y
check_success

conda install -c conda-forge jupyter-ai
check_success

# Function to get JupyterLab user settings directory
get_jupyter_settings_dir() {
    # Get the Jupyter paths
    # jupyter_paths=$(jupyter --paths | grep -A 1 'user' | tail -n 1 | sed 's/^[ \t]*//')
    jupyter_paths=$(jupyter --paths | grep -A 1 'jupyter' | head -n 1 | sed 's/^[ \t]*//')

    # Append the lab/user-settings path to the user directory
    settings_dir="${jupyter_paths}/lab/user-settings/@jupyterlab/notebook-extension"
    echo $settings_dir
}

# Define the settings directory
settings_dir=$(get_jupyter_settings_dir)

# Define the settings file path
settings_file="$settings_dir/tracker.jupyterlab-settings"

# Create the settings directory if it doesn't exist
mkdir -p "$settings_dir"

# Define the JSON content
json_content='{
    "codeCellConfig": {
        "lineNumbers": true,
        "lineWrap": true,
        "autoClosingBrackets": true
    },
    "markdownCellConfig": {
        "lineNumbers": true,
        "matchBrackets": true,
        "autoClosingBrackets": true
    },
    "rawCellConfig": {
        "lineNumbers": true,
        "matchBrackets": true,
        "autoClosingBrackets": true
    }
}'

# Write the JSON content to the settings file
echo "$json_content" > "$settings_file"
check_success


echo "JupyterLab configuration updated successfully!"

