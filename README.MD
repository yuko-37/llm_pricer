# Description


### 1. Create conda environment
Create the project’s conda environment using the provided `environment.yml` file:<br/>
```bash
conda env create -f environment.yml
```
use the command below to update environment
```bash
conda env update --name llm_pricer --file=environment.yml --prune
```
Activate the environment:<br/>
```bash
conda activate llm_pricer
```
Start jupyter lab:<br/>
```bash
jupyter lab
```

# For Development
Install dev tool on your dev environment
```commandline
pip install ruff black pre-commit
```
Run the following command to create git hooks
```commandline
pre-commit install --hook-type pre-commit --hook-type pre-push
```
