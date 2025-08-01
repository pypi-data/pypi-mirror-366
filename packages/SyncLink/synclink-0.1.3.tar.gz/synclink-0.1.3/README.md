
---

# SyncLink

**SyncLink** is a flexible Python utility for syncing code files (skills, scripts, or any directory content) from a folder in a GitHub repository to your local directory.
Supports public and private repos, selective file syncing, local-over-remote file protection, and easy integration.

---

## Features

* **Sync entire folders** or select specific files.
* **Skip or override** existing local files.
* **Supports private repos** (via GitHub token).
* **Branch selection**—sync from any branch, not just master/main.
* **Simple, readable code**—ready to drop into any project.
* **Preserves your local changes** by default.

---

## Installation

Simply copy `SyncLink` into your project, or package as you like.

Dependencies:

* Python 3.10+
* `requests`

---

## Usage

### **1. Basic Example (Sync All Files)**

```python
from SyncLink import SyncLink

syncer = SyncLink(
    githubRepo='TristanMcBrideSr/SkillForge',
    repoFolder='SkillForge',
    syncDir='./skills'
)
syncer.startSync()
```

### **2. Sync Only Specific Files**

```python
syncer = SyncLink(
    githubRepo='your-username/your-repo',
    repoFolder='MySkills',
    syncDir='./skills'
)
# Only sync 'weather.py' and 'research.py'
syncer.startSync(syncList=['weather', 'research'])
```

### **3. Override Existing Local Files**

```python
syncer = SyncLink(
    githubRepo='TristanMcBrideSr/SkillForge',
    repoFolder='SkillForge',
    syncDir='./skills'
)
# Force override any local file with the downloaded version
syncer.startSync(override=True)
```

### **4. Sync From a Private Repo**

```python
syncer = SyncLink(
    githubRepo='your-username/private-repo',
    repoFolder='MySkills',
    syncDir='./skills'
)
# Provide a GitHub token (classic or fine-grained with repo read access)
syncer.startSync(githubToken='YOUR_GITHUB_TOKEN')
```

### **5. Sync From a Different Branch**

```python
syncer = SyncLink(
    githubRepo='TristanMcBrideSr/SkillForge',
    repoFolder='SkillForge',
    syncDir='./skills'
)
syncer.startSync(branch='dev')  # Sync from 'dev' branch
```

---

## Parameters

### `SyncLink` constructor

* **githubRepo**: GitHub repo in the form `"owner/repo"` (required)
* **repoFolder**: Folder inside the repo to sync from (required)
* **syncDir**: Local directory to sync files to (required)

### `startSync(**kwargs)`

* **skillList** (`list`): Only these files will be synced (by name, `.py` optional).
* **override** (`bool`): If `True`, always overwrite existing local files.
* **githubToken** (`str`): Personal GitHub token for private repo access.
* **branch** (`str`): Branch to sync from (default `"master"`).

---

## How It Works

* Downloads a zip of the specified repo+branch.
* Extracts just the folder you specify.
* Copies each file:

  * **By default:** only new files are copied (existing files are untouched).
  * **With `override=True`:** always overwrites local files.
* Lets you pick which files to sync, or sync all.

---

## Error Handling

* Raises if folders/files are missing.
* Logs sync actions and errors to Python logger.
* Skips files that already exist locally, unless `override` is set.

---

## Example: Complete Workflow

```python
syncer = SyncLink(
    githubRepo='my-org/myrepo',
    repoFolder='skills',
    syncDir='./skills'
)
syncer.startSync(
    syncList=['my_skill', 'other_skill.py'],
    override=False,
    githubToken=os.getenv('GITHUB_TOKEN'), # If syncing from a private repo else you can omit this
    branch='main'
)
```

---

## Code Examples

You can find code examples on my [GitHub repository](https://github.com/TristanMcBrideSr/TechBook).

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).
Copyright 2025 Tristan McBride Sr.

---

## Acknowledgements

Project by:
- Tristan McBride Sr.
- Sybil

