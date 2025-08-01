"""
Terraform configuration parser service.
"""

from pathlib import Path
from typing import Any

import hcl2

from ..exc import TerraformConfigError
from ..models.terraform import BackendConfig, TerraformConfig


class TerraformParser:
    """
    Parser for Terraform HCL configuration files
    """

    def parse_directory(self, directory: Path, verbose: bool = False) -> TerraformConfig:
        """
        Parse all .tf files in directory using hcl2.

        Args:
            directory: Path to the directory containing .tf files
            verbose: Enable verbose logging

        Returns:
            Parsed Terraform configuration

        Raises:
            FileNotFoundError: If directory doesn't exist
            hcl2.Hcl2Error: If HCL parsing fails
            TerraformConfigError: If configuration is invalid

        """
        if not directory.exists():
            msg = f"Directory not found: {directory}"
            raise FileNotFoundError(msg)

        config = TerraformConfig()
        tf_files = list(directory.glob("*.tf"))

        if not tf_files:
            # Return empty config if no .tf files found
            return config

        # Collect all terraform blocks from all files
        all_terraform_blocks = []

        for tf_file in tf_files:
            try:
                with Path(tf_file).open(mode="r", encoding="utf-8") as f:
                    parsed = hcl2.load(f)
                    if verbose:
                        from rich.console import Console
                        console = Console()
                        console.print(f"[dim]DEBUG:[/dim] Parsing file: {tf_file.name}")

                    # Process terraform blocks
                    if "terraform" in parsed:
                        terraform_blocks = parsed["terraform"]
                        if verbose:
                            console.print(f"[dim]DEBUG:[/dim] Found {len(terraform_blocks)} terraform blocks in {tf_file.name}")

                        for block in terraform_blocks:
                            all_terraform_blocks.append(block)
                            if verbose:
                                console.print(f"[dim]DEBUG:[/dim] Added terraform block with keys: {list(block.keys())}")

                    # Process provider blocks
                    if "provider" in parsed:
                        for provider in parsed["provider"]:
                            config.providers.append(provider)

            except Exception as e:  # noqa: PERF203
                # HCL2 apparently only throws a generic Exception, so we need
                # to catch all exceptions.
                msg = f"Unexpected error parsing {tf_file}: {e}"
                raise TerraformConfigError(
                    msg,
                    field="file_io",
                    value=str(tf_file),
                ) from e

        # Now select the terraform block with backend configuration
        if all_terraform_blocks:
            terraform_block_with_backend = None
            for i, block in enumerate(all_terraform_blocks):
                if verbose:
                    from rich.console import Console
                    console = Console()
                    console.print(f"[dim]DEBUG:[/dim] Evaluating terraform block {i}: {list(block.keys())}")

                if "backend" in block:
                    terraform_block_with_backend = block
                    if verbose:
                        console.print(f"[dim]DEBUG:[/dim] Selected terraform block with backend: {block}")
                    break

            # Use the terraform block with backend, or the first one if none have backend
            if terraform_block_with_backend:
                config.terraform_block = terraform_block_with_backend
                if verbose:
                    console.print(f"[dim]DEBUG:[/dim] Using terraform block with backend configuration")
            else:
                config.terraform_block = all_terraform_blocks[0]
                if verbose:
                    console.print(f"[dim]DEBUG:[/dim] No backend found, using first terraform block")

            # Extract required version if present
            if config.terraform_block and "required_version" in config.terraform_block:
                config.required_version = config.terraform_block["required_version"]

        return config

    def parse_from_string(self, content: str) -> TerraformConfig:
        """
        Parse Terraform configuration from string content.

        Args:
            content: HCL configuration content

        Returns:
            Parsed Terraform configuration

        Raises:
            hcl2.Hcl2Error: If HCL parsing fails
            TerraformConfigError: If configuration is invalid

        """
        try:
            parsed = hcl2.loads(content)
            config = TerraformConfig()
            self._process_parsed_content(parsed, config)
        except Exception as e:
            msg = f"Failed to parse HCL content: {e}"
            raise TerraformConfigError(
                msg,
                field="hcl_syntax",
                value="<string>",
            ) from e
        return config

    def _process_parsed_content(
        self, parsed: dict[str, Any], config: TerraformConfig, verbose: bool = False
    ) -> None:
        """
        Process parsed HCL content and update configuration.

        Args:
            parsed: Parsed HCL content
            config: Configuration to update
            verbose: Enable verbose logging

        """
        if verbose:
            from rich.console import Console
            console = Console()
            console.print(f"[dim]DEBUG:[/dim] Parsed content keys: {list(parsed.keys())}")

        # Process terraform block
        if "terraform" in parsed:
            terraform_blocks = parsed["terraform"]
            if verbose:
                console.print(f"[dim]DEBUG:[/dim] Found {len(terraform_blocks)} terraform blocks")

            # Look for terraform block with backend configuration
            terraform_block_with_backend = None
            for i, block in enumerate(terraform_blocks):
                if verbose:
                    console.print(f"[dim]DEBUG:[/dim] Terraform block {i} keys: {list(block.keys())}")

                if "backend" in block:
                    terraform_block_with_backend = block
                    if verbose:
                        console.print(f"[dim]DEBUG:[/dim] Found terraform block with backend: {block}")
                    break

            # Use the terraform block with backend, or the first one if none have backend
            if terraform_block_with_backend:
                config.terraform_block = terraform_block_with_backend
                if verbose:
                    console.print(f"[dim]DEBUG:[/dim] Using terraform block with backend configuration")
            elif terraform_blocks:
                config.terraform_block = terraform_blocks[0]
                if verbose:
                    console.print(f"[dim]DEBUG:[/dim] No backend found, using first terraform block")

            # Extract required version if present
            if config.terraform_block and "required_version" in config.terraform_block:
                config.required_version = config.terraform_block["required_version"]

        # Process provider blocks
        if "provider" in parsed:
            for provider in parsed["provider"]:
                config.providers.append(provider)

    def extract_backend_config(
        self, terraform_block: dict[str, Any], verbose: bool = False
    ) -> BackendConfig | None:
        """
        Extract backend configuration from terraform block.

        Args:
            terraform_block: The terraform block dictionary
            verbose: Enable verbose logging

        Returns:
            Backend configuration or None if no backend configured

        """
        if verbose:
            from rich.console import Console
            console = Console()
            console.print(f"[dim]DEBUG:[/dim] Terraform block keys: {list(terraform_block.keys())}")

        if "backend" not in terraform_block:
            if verbose:
                console.print(f"[dim]DEBUG:[/dim] No backend key found in terraform block")
            return BackendConfig(type="local", config={})

        backend_configs = terraform_block["backend"]
        if verbose:
            console.print(f"[dim]DEBUG:[/dim] Backend configs: {backend_configs}")

        if not backend_configs:
            if verbose:
                console.print(f"[dim]DEBUG:[/dim] No backend configs found")
            return BackendConfig(type="local", config={})

        backend_config = backend_configs[0]
        if verbose:
            console.print(f"[dim]DEBUG:[/dim] First backend config: {backend_config}")

        # Backend config structure: [{"s3": {"bucket": "..."}}] or [{"s3":
        # [{"bucket": "..."}]}]
        backend_type = next(iter(backend_config.keys()))
        backend_config_value = backend_config[backend_type]

        if verbose:
            console.print(f"[dim]DEBUG:[/dim] Backend type: {backend_type}")
            console.print(f"[dim]DEBUG:[/dim] Backend config value: {backend_config_value}")

        # Handle both formats: direct dict or list of dicts
        if isinstance(backend_config_value, list):
            config_data = backend_config_value[0] if backend_config_value else {}
        else:
            config_data = backend_config_value if backend_config_value else {}

        if verbose:
            console.print(f"[dim]DEBUG:[/dim] Final config data: {config_data}")

        return BackendConfig(type=backend_type, config=config_data)
