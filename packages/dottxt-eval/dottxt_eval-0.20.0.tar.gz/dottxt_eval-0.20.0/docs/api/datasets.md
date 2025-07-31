# Datasets Module

Classes and functions for the dataset plugin system.

## Dataset Abstract Base Class

Base class that all dataset plugins must inherit from.

**See also**: [How to Create a Dataset Plugin](../how-to/create-dataset-plugin.md)

::: doteval.datasets.Dataset

## DatasetRegistry Class

Central registry for managing dataset plugins. This is primarily used internally but can be useful for advanced use cases.

::: doteval.datasets.DatasetRegistry

## Functions

### list_available

Get a list of all available datasets from installed plugins.

::: doteval.datasets.list_available

### get_dataset_info

Get information about a specific dataset.

::: doteval.datasets.get_dataset_info
