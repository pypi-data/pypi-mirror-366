import logging
import os
import requests
import zipfile
import shutil
from io import BytesIO
import tempfile

logger = logging.getLogger(__name__)

class SyncLink:
    def __init__(self, githubRepo: str = None, repoFolder: str = None, syncDir: str = None):
        self.githubRepo = githubRepo
        self.repoFolder = repoFolder
        self.syncDir    = syncDir
        self.syncList   = None
        self.ghToken    = None
        self.branch     = 'master'
        self.override   = False
        self._validateConfig()

    def configLink(self, **kwargs):
        """
        Configures the SyncLink instance with required and optional parameters.
        Kwargs:
            githubRepo: str, GitHub repository in the format 'owner/repo'
            repoFolder: str, folder in the repo to sync from
            syncDir: str, local directory to sync to
            syncList: list of files to sync (default: all)
            override: bool, if True always overwrite local files (default: False)
            token: str, GitHub token for private repos (default: None)
            branch: str, Git branch (default: 'master')
        """
        if 'githubRepo' in kwargs:
            self.githubRepo = kwargs['githubRepo']
        if 'repoFolder' in kwargs:
            self.repoFolder = kwargs['repoFolder']
        if 'syncDir' in kwargs:
            self.syncDir = kwargs['syncDir']

        if 'syncList' in kwargs:
            self.syncList = kwargs['syncList']
        if 'override' in kwargs:
            self.override = kwargs['override']
        if 'token' in kwargs:
            self.ghToken = kwargs['token']
        if 'branch' in kwargs:
            self.branch = kwargs['branch']

        self._validateConfig()

    def _validateConfig(self):
        if not self.githubRepo:
            raise ValueError("GitHub repo must be specified e.g., 'TristanMcBrideSr/Sync'")
        if not self.repoFolder:
            raise ValueError("Repo folder must be specified e.g., 'your/path/Sync'")
        if not self.syncDir:
            raise ValueError("Sync dir must be specified e.g., '/your/path/sync'")

    def _syncNewFiles(self, srcDir, dstDir, syncList=None, override=False):
        onlyFiles = None
        if syncList:
            normalized = set()
            for name in syncList:
                name = name.lower()
                normalized.add(name)
                if not name.endswith(".py"):
                    normalized.add(f"{name}.py")
            onlyFiles = normalized

        for root, dirs, files in os.walk(srcDir):
            relRoot = os.path.relpath(root, srcDir)
            targetRoot = os.path.join(dstDir, relRoot) if relRoot != '.' else dstDir
            os.makedirs(targetRoot, exist_ok=True)
            for file in files:
                if onlyFiles and file.lower() not in onlyFiles:
                    continue
                srcFile = os.path.join(root, file)
                dstFile = os.path.join(targetRoot, file)
                if os.path.exists(dstFile):
                    if override:
                        shutil.copy2(srcFile, dstFile)
                        logger.info(f"Overridden {dstFile} with {srcFile}")
                    else:
                        logger.info(f"File {dstFile} already exists locally. Skipping (preserving local).")
                    continue
                shutil.copy2(srcFile, dstFile)
                logger.info(f"Copied {srcFile} to {dstFile}")

    def startSync(self, **kwargs):
        """
        Syncs files from a GitHub repo zip to local directory.
        You can use the kwargs to override class defaults.
        or set them using configLink() first.
        Kwargs:
            syncDir: str, local directory to sync to (overrides class default)
            syncList: list of files to sync (default: all)
            override: bool, if True always overwrite local (default: False)
            token: str, GitHub token for private repos (default: None)
            branch: str, Git branch (default: 'master')
        """
        dstDir   = kwargs.get('syncDir') or self.syncDir
        syncList = kwargs.get('syncList') or self.syncList
        override = kwargs.get('override', False)
        ghToken  = kwargs.get('token') or self.ghToken
        branch   = kwargs.get('branch') or self.branch

        if not dstDir:
            raise ValueError("syncDir can not be None. You must set it using configLink() or pass as parameter.")

        logger.info(f"Starting {self.repoFolder} connection...")
        zipUrl = f"https://github.com/{self.githubRepo}/archive/refs/heads/{branch}.zip"
        logger.info("Starting sync...")
        logger.info(f"Downloading {zipUrl} ...")
        headers = {"User-Agent": "Mozilla/5.0"}
        if ghToken:
            headers["Authorization"] = f"Bearer {ghToken}"

        try:
            r = requests.get(zipUrl, headers=headers)
            r.raise_for_status()
            tempDir = tempfile.mkdtemp()
            try:
                z = zipfile.ZipFile(BytesIO(r.content))
                z.extractall(tempDir)
                extractedRoot = os.path.join(tempDir, os.listdir(tempDir)[0])
                skillsSrc = os.path.join(extractedRoot, self.repoFolder)

                if not os.path.exists(skillsSrc):
                    logger.error(f"Can't find {self.repoFolder} in the repo!")
                    raise FileNotFoundError(f"Can't find {self.repoFolder} in the repo!")

                os.makedirs(dstDir, exist_ok=True)
                self._syncNewFiles(skillsSrc, dstDir, syncList, override)
                logger.info("Sync complete.")
                return True
            finally:
                shutil.rmtree(tempDir)
        except Exception as e:
            logger.error(f"Sync failed: {e}", exc_info=True)
            return False
