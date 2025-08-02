import re
import abc
import dataclasses
import shutil
from json import loads, dump
import logging
import os
from shutil import rmtree, move
from subprocess import run, CalledProcessError
import sys
from typing import Any, cast
from urllib import request
from urllib.error import URLError, HTTPError
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from databricks.labs.blueprint.installation import Installation, JsonValue
from databricks.labs.blueprint.installation import SerdeError
from databricks.labs.blueprint.installer import InstallState
from databricks.labs.blueprint.tui import Prompts
from databricks.labs.blueprint.wheels import ProductInfo
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import NotFound, PermissionDenied

from databricks.labs.lakebridge.config import (
    TranspileConfig,
    ReconcileConfig,
    DatabaseConfig,
    LakebridgeConfiguration,
    ReconcileMetadataConfig,
)
from databricks.labs.lakebridge.deployment.configurator import ResourceConfigurator
from databricks.labs.lakebridge.deployment.installation import WorkspaceInstallation
from databricks.labs.lakebridge.helpers.file_utils import chdir
from databricks.labs.lakebridge.reconcile.constants import ReconReportType, ReconSourceType
from databricks.labs.lakebridge.transpiler.repository import TranspilerRepository

logger = logging.getLogger(__name__)

TRANSPILER_WAREHOUSE_PREFIX = "Lakebridge Transpiler Validation"


class TranspilerInstaller(abc.ABC):
    def __init__(self, repository: TranspilerRepository) -> None:
        self._repository = repository

    _version_pattern = re.compile(r"[_-](\d+(?:[.\-_]\w*\d+)+)")

    @classmethod
    def get_local_artifact_version(cls, artifact: Path) -> str | None:
        # TODO: Get the version from the metadata inside the artifact rather than relying on the filename.
        match = cls._version_pattern.search(artifact.stem)
        if not match:
            return None
        group = match.group(0)
        if not group:
            return None
        # TODO: Update the regex to take care of these trimming scenarios.
        if group.startswith('-'):
            group = group[1:]
        if group.endswith("-py3"):
            group = group[:-4]
        return group

    @classmethod
    def _store_product_state(cls, product_path: Path, version: str) -> None:
        state_path = product_path / "state"
        state_path.mkdir()
        version_data = {"version": f"v{version}", "date": datetime.now(timezone.utc).isoformat()}
        version_path = state_path / "version.json"
        with version_path.open("w", encoding="utf-8") as f:
            dump(version_data, f)
            f.write("\n")


class WheelInstaller(TranspilerInstaller):

    @classmethod
    def get_latest_artifact_version_from_pypi(cls, product_name: str) -> str | None:
        try:
            with request.urlopen(f"https://pypi.org/pypi/{product_name}/json") as server:
                text: bytes = server.read()
            data: dict[str, Any] = loads(text)
            return data.get("info", {}).get('version', None)
        except HTTPError as e:
            logger.error(f"Error while fetching PyPI metadata: {product_name}", exc_info=e)
            return None

    def __init__(
        self,
        repository: TranspilerRepository,
        product_name: str,
        pypi_name: str,
        artifact: Path | None = None,
    ) -> None:
        super().__init__(repository)
        self._product_name = product_name
        self._pypi_name = pypi_name
        self._artifact = artifact

    def install(self) -> Path | None:
        return self._install_checking_versions()

    def _install_checking_versions(self) -> Path | None:
        latest_version = (
            self.get_local_artifact_version(self._artifact)
            if self._artifact
            else self.get_latest_artifact_version_from_pypi(self._pypi_name)
        )
        if latest_version is None:
            logger.warning(f"Could not determine the latest version of {self._pypi_name}")
            logger.error(f"Failed to install transpiler: {self._product_name}")
            return None
        installed_version = self._repository.get_installed_version(self._product_name)
        if installed_version == latest_version:
            logger.info(f"{self._pypi_name} v{latest_version} already installed")
            return None
        return self._install_latest_version(latest_version)

    def _install_latest_version(self, version: str) -> Path | None:
        logger.info(f"Installing Databricks {self._product_name} transpiler v{version}")
        self._product_path = self._repository.transpilers_path() / self._product_name
        backup_path = Path(f"{self._product_path!s}-saved")
        if self._product_path.exists():
            os.rename(self._product_path, backup_path)
        self._install_path = self._product_path / "lib"
        self._install_path.mkdir(parents=True, exist_ok=True)
        try:
            result = self._unsafe_install_latest_version(version)
            logger.info(f"Successfully installed {self._pypi_name} v{version}")
            if backup_path.exists():
                rmtree(backup_path)
            return result
        except (CalledProcessError, ValueError) as e:
            logger.error(f"Failed to install {self._pypi_name} v{version}", exc_info=e)
            rmtree(self._product_path)
            if backup_path.exists():
                os.rename(backup_path, self._product_path)
            return None

    def _unsafe_install_latest_version(self, version: str) -> Path | None:
        self._create_venv()
        self._install_with_pip()
        self._copy_lsp_resources()
        return self._post_install(version)

    def _create_venv(self) -> None:
        with chdir(self._install_path):
            self._unsafe_create_venv()

    def _unsafe_create_venv(self) -> None:
        # using the venv module doesn't work (maybe it's not possible to create a venv from a venv ?)
        # so falling back to something that works
        # for some reason this requires shell=True, so pass full cmd line
        cmd_line = f"{sys.executable} -m venv .venv"
        completed = run(cmd_line, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, shell=True, check=False)
        if completed.returncode:
            logger.error(f"Failed to create venv, error code: {completed.returncode}")
            if completed.stdout:
                for line in completed.stdout:
                    logger.error(line)
            if completed.stderr:
                for line in completed.stderr:
                    logger.error(line)
        completed.check_returncode()
        self._venv = self._install_path / ".venv"
        self._site_packages = self._locate_site_packages()

    def _locate_site_packages(self) -> Path:
        # can't use sysconfig because it only works for currently running python
        if sys.platform == "win32":
            return self._locate_site_packages_windows()
        return self._locate_site_packages_linux_or_macos()

    def _locate_site_packages_windows(self) -> Path:
        packages = self._venv / "Lib" / "site-packages"
        if packages.exists():
            return packages
        raise ValueError(f"Could not locate 'site-packages' for {self._venv!s}")

    def _locate_site_packages_linux_or_macos(self) -> Path:
        lib = self._venv / "lib"
        for dir_ in os.listdir(lib):
            if dir_.startswith("python"):
                packages = lib / dir_ / "site-packages"
                if packages.exists():
                    return packages
        raise ValueError(f"Could not locate 'site-packages' for {self._venv!s}")

    def _install_with_pip(self) -> None:
        with chdir(self._install_path):
            # the way to call pip from python is highly sensitive to os and source type
            if self._artifact:
                self._install_local_artifact()
            else:
                self._install_remote_artifact()

    def _install_local_artifact(self) -> None:
        pip = self._locate_pip()
        pip = pip.relative_to(self._install_path)
        target = self._site_packages
        target = target.relative_to(self._install_path)
        if sys.platform == "win32":
            command = f"{pip!s} install {self._artifact!s} -t {target!s}"
            completed = run(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, shell=False, check=False)
        else:
            command = f"'{pip!s}' install '{self._artifact!s}' -t '{target!s}'"
            completed = run(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, shell=True, check=False)
        # checking return code later makes debugging easier
        completed.check_returncode()

    def _install_remote_artifact(self) -> None:
        pip = self._locate_pip()
        pip = pip.relative_to(self._install_path)
        target = self._site_packages
        target = target.relative_to(self._install_path)
        if sys.platform == "win32":
            args = [str(pip), "install", self._pypi_name, "-t", str(target)]
            completed = run(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, shell=False, check=False)
        else:
            command = f"'{pip!s}' install {self._pypi_name} -t '{target!s}'"
            completed = run(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, shell=True, check=False)
        # checking return code later makes debugging easier
        completed.check_returncode()

    def _locate_pip(self) -> Path:
        return self._venv / "Scripts" / "pip3.exe" if sys.platform == "win32" else self._venv / "bin" / "pip3"

    def _copy_lsp_resources(self):
        lsp = self._site_packages / "lsp"
        if not lsp.exists():
            raise ValueError("Installed transpiler is missing a 'lsp' folder")
        shutil.copytree(lsp, self._install_path, dirs_exist_ok=True)

    def _post_install(self, version: str) -> Path | None:
        config = self._install_path / "config.yml"
        if not config.exists():
            raise ValueError("Installed transpiler is missing a 'config.yml' file in its 'lsp' folder")
        install_ext = "ps1" if sys.platform == "win32" else "sh"
        install_script = f"installer.{install_ext}"
        installer = self._install_path / install_script
        if installer.exists():
            self._run_custom_installer(installer)
        self._store_product_state(product_path=self._product_path, version=version)
        return self._install_path

    def _run_custom_installer(self, installer):
        args = [str(installer)]
        run(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, cwd=str(self._install_path), check=True)


class MavenInstaller(TranspilerInstaller):
    # Maven Central, base URL.
    _maven_central_repo: str = "https://repo.maven.apache.org/maven2/"

    @classmethod
    def _artifact_base_url(cls, group_id: str, artifact_id: str) -> str:
        """Construct the base URL for a Maven artifact."""
        # Reference: https://maven.apache.org/repositories/layout.html
        group_path = group_id.replace(".", "/")
        return f"{cls._maven_central_repo}{group_path}/{artifact_id}/"

    @classmethod
    def artifact_metadata_url(cls, group_id: str, artifact_id: str) -> str:
        """Get the metadata URL for a Maven artifact."""
        # TODO: Unit test this method.
        return f"{cls._artifact_base_url(group_id, artifact_id)}maven-metadata.xml"

    @classmethod
    def artifact_url(
        cls, group_id: str, artifact_id: str, version: str, classifier: str | None = None, extension: str = "jar"
    ) -> str:
        """Get the URL for a versioned Maven artifact."""
        # TODO: Unit test this method, including classifier and extension.
        _classifier = f"-{classifier}" if classifier else ""
        artifact_base_url = cls._artifact_base_url(group_id, artifact_id)
        return f"{artifact_base_url}{version}/{artifact_id}-{version}{_classifier}.{extension}"

    @classmethod
    def get_current_maven_artifact_version(cls, group_id: str, artifact_id: str) -> str | None:
        url = cls.artifact_metadata_url(group_id, artifact_id)
        try:
            with request.urlopen(url) as server:
                text = server.read()
        except HTTPError as e:
            logger.error(f"Error while fetching maven metadata: {group_id}:{artifact_id}", exc_info=e)
            return None
        logger.debug(f"Maven metadata for {group_id}:{artifact_id}: {text}")
        return cls._extract_latest_release_version(text)

    @classmethod
    def _extract_latest_release_version(cls, maven_metadata: str) -> str | None:
        """Extract the latest release version from Maven metadata."""
        # Reference: https://maven.apache.org/repositories/metadata.html#The_A_Level_Metadata
        # TODO: Unit test this method, to verify the sequence of things it checks for.
        root = ET.fromstring(maven_metadata)
        for label in ("release", "latest"):
            version = root.findtext(f"./versioning/{label}")
            if version is not None:
                return version
        return root.findtext("./versioning/versions/version[last()]")

    @classmethod
    def download_artifact_from_maven(
        cls,
        group_id: str,
        artifact_id: str,
        version: str,
        target: Path,
        classifier: str | None = None,
        extension: str = "jar",
    ) -> bool:
        if target.exists():
            logger.warning(f"Skipping download of {group_id}:{artifact_id}:{version}; target already exists: {target}")
            return True
        url = cls.artifact_url(group_id, artifact_id, version, classifier, extension)
        try:
            path, _ = request.urlretrieve(url)
            logger.debug(f"Downloaded maven artefact from {url} to {path}")
        except URLError as e:
            logger.error(f"Unable to download maven artefact: {group_id}:{artifact_id}:{version}", exc_info=e)
            return False
        logger.debug(f"Moving {path} to {target}")
        move(path, target)
        logger.info(f"Successfully installed: {group_id}:{artifact_id}:{version}")
        return True

    def __init__(
        self,
        repository: TranspilerRepository,
        product_name: str,
        group_id: str,
        artifact_id: str,
        artifact: Path | None = None,
    ) -> None:
        super().__init__(repository)
        self._product_name = product_name
        self._group_id = group_id
        self._artifact_id = artifact_id
        self._artifact = artifact

    def install(self) -> Path | None:
        return self._install_checking_versions()

    def _install_checking_versions(self) -> Path | None:
        if self._artifact:
            latest_version = self.get_local_artifact_version(self._artifact)
        else:
            latest_version = self.get_current_maven_artifact_version(self._group_id, self._artifact_id)
        if latest_version is None:
            logger.warning(f"Could not determine the latest version of Databricks {self._product_name} transpiler")
            logger.error("Failed to install transpiler: Databricks {self._product_name} transpiler")
            return None
        installed_version = self._repository.get_installed_version(self._product_name)
        if installed_version == latest_version:
            logger.info(f"Databricks {self._product_name} transpiler v{latest_version} already installed")
            return None
        return self._install_version(latest_version)

    def _install_version(self, version: str) -> Path | None:
        logger.info(f"Installing Databricks {self._product_name} transpiler v{version}")
        self._product_path = self._repository.transpilers_path() / self._product_name
        backup_path = Path(f"{self._product_path!s}-saved")
        if backup_path.exists():
            rmtree(backup_path)
        if self._product_path.exists():
            os.rename(self._product_path, backup_path)
        self._product_path.mkdir(parents=True)
        self._install_path = self._product_path / "lib"
        self._install_path.mkdir()
        try:
            if self._unsafe_install_version(version):
                logger.info(f"Successfully installed {self._product_name} v{version}")
                self._store_product_state(self._product_path, version)
                if backup_path.exists():
                    rmtree(backup_path)
                return self._product_path
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to install Databricks {self._product_name} transpiler v{version}", exc_info=e)
        rmtree(self._product_path)
        if backup_path.exists():
            os.rename(backup_path, self._product_path)
        return None

    def _unsafe_install_version(self, version: str) -> bool:
        jar_file_path = self._install_path / f"{self._artifact_id}.jar"
        if self._artifact:
            logger.debug(f"Copying '{self._artifact!s}' to '{jar_file_path!s}'")
            shutil.copyfile(self._artifact, jar_file_path)
        elif not self.download_artifact_from_maven(self._group_id, self._artifact_id, version, jar_file_path):
            logger.error(f"Failed to install Databricks {self._product_name} transpiler v{version}")
            return False
        self._copy_lsp_config(jar_file_path)
        return True

    def _copy_lsp_config(self, jar_file_path: Path) -> None:
        with ZipFile(jar_file_path) as zip_file:
            zip_file.extract("lsp/config.yml", self._install_path)
        shutil.move(self._install_path / "lsp" / "config.yml", self._install_path / "config.yml")
        os.rmdir(self._install_path / "lsp")


class WorkspaceInstaller:
    def __init__(
        self,
        ws: WorkspaceClient,
        prompts: Prompts,
        installation: Installation,
        install_state: InstallState,
        product_info: ProductInfo,
        resource_configurator: ResourceConfigurator,
        workspace_installation: WorkspaceInstallation,
        environ: dict[str, str] | None = None,
        transpiler_repository: TranspilerRepository = TranspilerRepository.user_home(),
    ):
        self._ws = ws
        self._prompts = prompts
        self._installation = installation
        self._install_state = install_state
        self._product_info = product_info
        self._resource_configurator = resource_configurator
        self._ws_installation = workspace_installation
        self._transpiler_repository = transpiler_repository

        if not environ:
            environ = dict(os.environ.items())

        if "DATABRICKS_RUNTIME_VERSION" in environ:
            msg = "WorkspaceInstaller is not supposed to be executed in Databricks Runtime"
            raise SystemExit(msg)

    def run(
        self, module: str, config: LakebridgeConfiguration | None = None, artifact: str | None = None
    ) -> LakebridgeConfiguration:
        logger.debug(f"Initializing workspace installation for module: {module} (config: {config})")
        if module == "transpile" and artifact:
            self.install_artifact(artifact)
        elif module in {"transpile", "all"}:
            self.install_bladebridge()
            self.install_morpheus()
        if not config:
            config = self.configure(module)
        if self._is_testing():
            return config
        self._ws_installation.install(config)
        logger.info("Installation completed successfully! Please refer to the documentation for the next steps.")
        return config

    def install_bladebridge(self, artifact: Path | None = None) -> None:
        local_name = "bladebridge"
        pypi_name = "databricks-bb-plugin"
        wheel_installer = WheelInstaller(self._transpiler_repository, local_name, pypi_name, artifact)
        wheel_installer.install()

    def install_morpheus(self, artifact: Path | None = None) -> None:
        if not self.is_java_version_okay():
            logger.error(
                "The morpheus transpiler requires Java 11 or above. Please install Java and re-run 'install-transpile'."
            )
            return
        product_name = "databricks-morph-plugin"
        group_id = "com.databricks.labs"
        artifact_id = product_name
        maven_installer = MavenInstaller(self._transpiler_repository, product_name, group_id, artifact_id, artifact)
        maven_installer.install()

    @classmethod
    def is_java_version_okay(cls) -> bool:
        detected_java = cls.find_java()
        match detected_java:
            case None:
                logger.warning("No Java executable found in the system PATH.")
                return False
            case (java_executable, None):
                logger.warning(f"Java found, but could not determine the version: {java_executable}.")
                return False
            case (java_executable, bytes(raw_version)):
                logger.warning(f"Java found ({java_executable}), but could not parse the version:\n{raw_version}")
                return False
            case (java_executable, tuple(old_version)) if old_version < (11, 0, 0, 0):
                version_str = ".".join(str(v) for v in old_version)
                logger.warning(f"Java found ({java_executable}), but version {version_str} is too old.")
                return False
            case _:
                return True

    def install_artifact(self, artifact: str):
        path = Path(artifact)
        if not path.exists():
            logger.error(f"Could not locate artifact {artifact}")
            return
        if "databricks-morph-plugin" in path.name:
            self.install_morpheus(path)
        elif "databricks_bb_plugin" in path.name:
            self.install_bladebridge(path)
        else:
            logger.fatal(f"Cannot install unsupported artifact: {artifact}")

    @classmethod
    def find_java(cls) -> tuple[Path, tuple[int, int, int, int] | bytes | None] | None:
        """Locate Java and return its version, as reported by `java -version`.

        The java executable is currently located by searching the system PATH. Its version is parsed from the output of
        the `java -version` command, which has been standardized since Java 10.

        Returns:
            a tuple of its path and the version as a tuple of integers (feature, interim, update, patch), if the java
            executable could be located. If the version cannot be parsed, instead the raw version information is
            returned, or `None` as a last resort. When no java executable is found, `None` is returned instead of a
            tuple.
        """
        # Platform-independent way to reliably locate the java executable.
        # Reference: https://docs.python.org/3.10/library/subprocess.html#popen-constructor
        java_executable = shutil.which("java")
        if java_executable is None:
            return None
        java_executable_path = Path(java_executable)
        logger.debug(f"Using java executable: {java_executable_path!r}")
        try:
            completed = run([str(java_executable_path), "-version"], shell=False, capture_output=True, check=True)
        except CalledProcessError as e:
            logger.debug(
                f"Failed to run {e.args!r} (exit-code={e.returncode}, stdout={e.stdout!r}, stderr={e.stderr!r})",
                exc_info=e,
            )
            return java_executable_path, None
        # It might not be ascii, but the bits we care about are so this will never fail.
        raw_output = completed.stderr
        java_version_output = raw_output.decode("ascii", errors="ignore")
        java_version = cls._parse_java_version(java_version_output)
        if java_version is None:
            return java_executable_path, raw_output.strip()
        logger.debug(f"Detected java version: {java_version}")
        return java_executable_path, java_version

    # Pattern to match a Java version string, compiled at import time to ensure it's valid.
    # Ref: https://docs.oracle.com/en/java/javase/11/install/version-string-format.html
    _java_version_pattern = re.compile(
        r' version "(?P<feature>\d+)(?:\.(?P<interim>\d+)(?:\.(?P<update>\d+)(?:\.(?P<patch>\d+))?)?)?"'
    )

    @classmethod
    def _parse_java_version(cls, version: str) -> tuple[int, int, int, int] | None:
        """Locate and parse the Java version in the output of `java -version`."""
        # Output looks like this:
        #   openjdk version "24.0.1" 2025-04-15
        #   OpenJDK Runtime Environment Temurin-24.0.1+9 (build 24.0.1+9)
        #   OpenJDK 64-Bit Server VM Temurin-24.0.1+9 (build 24.0.1+9, mixed mode)
        match = cls._java_version_pattern.search(version)
        if not match:
            logger.debug(f"Could not parse java version: {version!r}")
            return None
        feature = int(match["feature"])
        interim = int(match["interim"] or 0)
        update = int(match["update"] or 0)
        patch = int(match["patch"] or 0)
        return feature, interim, update, patch

    def configure(self, module: str) -> LakebridgeConfiguration:
        match module:
            case "transpile":
                logger.info("Configuring lakebridge `transpile`.")
                return LakebridgeConfiguration(self._configure_transpile(), None)
            case "reconcile":
                logger.info("Configuring lakebridge `reconcile`.")
                return LakebridgeConfiguration(None, self._configure_reconcile())
            case "all":
                logger.info("Configuring lakebridge `transpile` and `reconcile`.")
                return LakebridgeConfiguration(
                    self._configure_transpile(),
                    self._configure_reconcile(),
                )
            case _:
                raise ValueError(f"Invalid input: {module}")

    def _is_testing(self):
        return self._product_info.product_name() != "lakebridge"

    def _configure_transpile(self) -> TranspileConfig:
        try:
            config = self._installation.load(TranspileConfig)
            logger.info("Lakebridge `transpile` is already installed on this workspace.")
            if not self._prompts.confirm("Do you want to override the existing installation?"):
                return config
        except NotFound:
            logger.info("Couldn't find existing `transpile` installation")
        except (PermissionDenied, SerdeError, ValueError, AttributeError):
            install_dir = self._installation.install_folder()
            logger.warning(
                f"Existing `transpile` installation at {install_dir} is corrupted. Continuing new installation..."
            )

        config = self._configure_new_transpile_installation()
        logger.info("Finished configuring lakebridge `transpile`.")
        return config

    def _configure_new_transpile_installation(self) -> TranspileConfig:
        default_config = self._prompt_for_new_transpile_installation()
        runtime_config = None
        catalog_name = "remorph"
        schema_name = "transpiler"
        if not default_config.skip_validation:
            catalog_name = self._configure_catalog()
            schema_name = self._configure_schema(catalog_name, "transpile")
            self._has_necessary_access(catalog_name, schema_name)
            warehouse_id = self._resource_configurator.prompt_for_warehouse_setup(TRANSPILER_WAREHOUSE_PREFIX)
            runtime_config = {"warehouse_id": warehouse_id}

        config = dataclasses.replace(
            default_config,
            catalog_name=catalog_name,
            schema_name=schema_name,
            sdk_config=runtime_config,
        )
        self._save_config(config)
        return config

    def _all_installed_dialects(self) -> list[str]:
        return sorted(self._transpiler_repository.all_dialects())

    def _transpilers_with_dialect(self, dialect: str) -> list[str]:
        return sorted(self._transpiler_repository.transpilers_with_dialect(dialect))

    def _transpiler_config_path(self, transpiler: str) -> Path:
        return self._transpiler_repository.transpiler_config_path(transpiler)

    def _prompt_for_new_transpile_installation(self) -> TranspileConfig:
        install_later = "Set it later"
        # TODO tidy this up, logger might not display the below in console...
        logger.info("Please answer a few questions to configure lakebridge `transpile`")
        all_dialects = [install_later, *self._all_installed_dialects()]
        source_dialect: str | None = self._prompts.choice("Select the source dialect:", all_dialects, sort=False)
        if source_dialect == install_later:
            source_dialect = None
        transpiler_name: str | None = None
        transpiler_config_path: Path | None = None
        if source_dialect:
            transpilers = self._transpilers_with_dialect(source_dialect)
            if len(transpilers) > 1:
                transpilers = [install_later] + transpilers
                transpiler_name = self._prompts.choice("Select the transpiler:", transpilers, sort=False)
                if transpiler_name == install_later:
                    transpiler_name = None
            else:
                transpiler_name = next(t for t in transpilers)
                logger.info(f"Lakebridge will use the {transpiler_name} transpiler")
            if transpiler_name:
                transpiler_config_path = self._transpiler_config_path(transpiler_name)
        transpiler_options: dict[str, JsonValue] | None = None
        if transpiler_config_path:
            transpiler_options = self._prompt_for_transpiler_options(
                cast(str, transpiler_name), cast(str, source_dialect)
            )
        input_source: str | None = self._prompts.question(
            "Enter input SQL path (directory/file)", default=install_later
        )
        if input_source == install_later:
            input_source = None
        output_folder = self._prompts.question("Enter output directory", default="transpiled")
        # When defaults are passed along we need to use absolute paths to avoid issues with relative paths
        if output_folder == "transpiled":
            output_folder = str(Path.cwd() / "transpiled")
        error_file_path = self._prompts.question("Enter error file path", default="errors.log")
        if error_file_path == "errors.log":
            error_file_path = str(Path.cwd() / "errors.log")

        run_validation = self._prompts.confirm(
            "Would you like to validate the syntax and semantics of the transpiled queries?"
        )

        return TranspileConfig(
            transpiler_config_path=str(transpiler_config_path) if transpiler_config_path is not None else None,
            transpiler_options=transpiler_options,
            source_dialect=source_dialect,
            skip_validation=(not run_validation),
            input_source=input_source,
            output_folder=output_folder,
            error_file_path=error_file_path,
        )

    def _prompt_for_transpiler_options(self, transpiler_name: str, source_dialect: str) -> dict[str, Any] | None:
        config_options = self._transpiler_repository.transpiler_config_options(transpiler_name, source_dialect)
        if len(config_options) == 0:
            return None
        return {option.flag: option.prompt_for_value(self._prompts) for option in config_options}

    def _configure_catalog(self) -> str:
        return self._resource_configurator.prompt_for_catalog_setup()

    def _configure_schema(
        self,
        catalog: str,
        default_schema_name: str,
    ) -> str:
        return self._resource_configurator.prompt_for_schema_setup(
            catalog,
            default_schema_name,
        )

    def _configure_reconcile(self) -> ReconcileConfig:
        try:
            self._installation.load(ReconcileConfig)
            logger.info("Lakebridge `reconcile` is already installed on this workspace.")
            if not self._prompts.confirm("Do you want to override the existing installation?"):
                # TODO: Exit gracefully, without raising SystemExit
                raise SystemExit(
                    "Lakebridge `reconcile` is already installed and no override has been requested. Exiting..."
                )
        except NotFound:
            logger.info("Couldn't find existing `reconcile` installation")
        except (PermissionDenied, SerdeError, ValueError, AttributeError):
            install_dir = self._installation.install_folder()
            logger.warning(
                f"Existing `reconcile` installation at {install_dir} is corrupted. Continuing new installation..."
            )

        config = self._configure_new_reconcile_installation()
        logger.info("Finished configuring lakebridge `reconcile`.")
        return config

    def _configure_new_reconcile_installation(self) -> ReconcileConfig:
        default_config = self._prompt_for_new_reconcile_installation()
        self._save_config(default_config)
        return default_config

    def _prompt_for_new_reconcile_installation(self) -> ReconcileConfig:
        logger.info("Please answer a few questions to configure lakebridge `reconcile`")
        data_source = self._prompts.choice(
            "Select the Data Source:", [source_type.value for source_type in ReconSourceType]
        )
        report_type = self._prompts.choice(
            "Select the report type:", [report_type.value for report_type in ReconReportType]
        )
        scope_name = self._prompts.question(
            f"Enter Secret scope name to store `{data_source.capitalize()}` connection details / secrets",
            default=f"remorph_{data_source}",
        )

        db_config = self._prompt_for_reconcile_database_config(data_source)
        metadata_config = self._prompt_for_reconcile_metadata_config()

        return ReconcileConfig(
            data_source=data_source,
            report_type=report_type,
            secret_scope=scope_name,
            database_config=db_config,
            metadata_config=metadata_config,
        )

    def _prompt_for_reconcile_database_config(self, source) -> DatabaseConfig:
        source_catalog = None
        if source == ReconSourceType.SNOWFLAKE.value:
            source_catalog = self._prompts.question(f"Enter source catalog name for `{source.capitalize()}`")

        schema_prompt = f"Enter source schema name for `{source.capitalize()}`"
        if source in {ReconSourceType.ORACLE.value}:
            schema_prompt = f"Enter source database name for `{source.capitalize()}`"

        source_schema = self._prompts.question(schema_prompt)
        target_catalog = self._prompts.question("Enter target catalog name for Databricks")
        target_schema = self._prompts.question("Enter target schema name for Databricks")

        return DatabaseConfig(
            source_schema=source_schema,
            target_catalog=target_catalog,
            target_schema=target_schema,
            source_catalog=source_catalog,
        )

    def _prompt_for_reconcile_metadata_config(self) -> ReconcileMetadataConfig:
        logger.info("Configuring reconcile metadata.")
        catalog = self._configure_catalog()
        schema = self._configure_schema(
            catalog,
            "reconcile",
        )
        volume = self._configure_volume(catalog, schema, "reconcile_volume")
        self._has_necessary_access(catalog, schema, volume)
        return ReconcileMetadataConfig(catalog=catalog, schema=schema, volume=volume)

    def _configure_volume(
        self,
        catalog: str,
        schema: str,
        default_volume_name: str,
    ) -> str:
        return self._resource_configurator.prompt_for_volume_setup(
            catalog,
            schema,
            default_volume_name,
        )

    def _save_config(self, config: TranspileConfig | ReconcileConfig):
        logger.info(f"Saving configuration file {config.__file__}")
        self._installation.save(config)
        ws_file_url = self._installation.workspace_link(config.__file__)
        if self._prompts.confirm(f"Open config file {ws_file_url} in the browser?"):
            webbrowser.open(ws_file_url)

    def _has_necessary_access(self, catalog_name: str, schema_name: str, volume_name: str | None = None):
        self._resource_configurator.has_necessary_access(catalog_name, schema_name, volume_name)
