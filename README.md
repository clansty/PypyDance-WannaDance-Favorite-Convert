# Dance World Favorite Converter

This toolset allows you to convert favorite song lists between **WannaDance** and **PypyDance** VRChat worlds.

It automatically downloads the latest song databases if they are not present in the directory.

## Prerequisites

- Python 3.x

## Usage

### 1. WannaDance -> PypyDance

Converts a WannaDance export string to PypyDance format.

```bash
python convert_wd_to_pypy.py "WannaFavorite:1234,5678,..."
```

-   **Input**: WannaDance export string (e.g., `WannaFavorite:1234,5678`) or just comma-separated IDs. You can also pass a path to a text file containing the string.
-   **Output**: Saves the result to `converted_pypy_list.txt`.

### 2. PypyDance -> WannaDance

Converts a PypyDance export string to WannaDance format.

```bash
python convert_pypy_to_wd.py "1234,5678,..."
```

-   **Input**: PypyDance export string (comma-separated IDs). You can also pass a path to a text file containing the string.
-   **Output**: Saves the result to `converted_wd_list.txt`.

## How it works

The scripts use fuzzy matching to find songs in the target database based on:
-   Token overlap in song names
-   Artist name matching
-   Exact substring matching

This handles cases where names are slightly different (e.g., "Song Name (Remix)" vs "Song Name [Remix]").

## Data Sources

If `wannadance.json` or `pypydance.json` are missing, they will be downloaded from:
-   **PypyDance**: `https://api.pypy.dance/bundle`
-   **WannaDance**: `https://api.udon.dance/Api/Songs/list`

