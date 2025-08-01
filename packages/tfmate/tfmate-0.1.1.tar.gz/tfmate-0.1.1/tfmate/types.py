"""
Type aliases for tfmate.
"""

from typing import Any

# Type aliases for common patterns
JSONDict = dict[str, Any]
TerraformConfigDict = dict[str, Any]
StateFileDict = dict[str, Any]
ProviderConfigDict = dict[str, Any]
BackendConfigDict = dict[str, Any]

# Type aliases for lists
TerraformFileList = list[str]
ProviderList = list[ProviderConfigDict]
ResourceList = list[dict[str, Any]]

# Type aliases for optional values
OptionalStr = str | None
OptionalDict = dict[str, Any] | None
OptionalList = list[Any] | None
