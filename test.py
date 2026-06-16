import os
import json

# Create the notebook file in your project root
notebook_path = os.path.expanduser('~/Desktop/Projects/json_normalization_practice.ipynb')

notebook_content = {
  "nbformat": 4,
  "nbformat_minor": 5,
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    },
    "language_info": {
      "name": "python",
      "version": "3.10"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "# JSON Normalization Practice Guide\n",
        "\n",
        "Learn how to work with JSON files and convert them to pandas DataFrames."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "import json\n",
        "import pandas as pd\n",
        "import os\n",
        "\n",
        "print('Setup complete!')"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Reading JSON: The Common Mistake"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "# WRONG: f.read() returns a STRING\n",
        "# with open('file.json', 'r') as f:\n",
        "#     data = f.read()  # This is a STRING, not a dict!\n",
        "#     df = pd.json_normalize(data)  # ERROR!\n",
        "\n",
        "# CORRECT: Use json.loads() to parse the string\n",
        "# with open('file.json', 'r') as f:\n",
        "#     raw = f.read()  # STRING\n",
        "#     data = json.loads(raw)  # Convert to DICT/LIST\n",
        "#     df = pd.json_normalize(data)  # Now it works!\n",
        "\n",
        "print('See code comments for correct pattern')"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Simple Example: List of Objects"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "import json\n",
        "import pandas as pd\n",
        "\n",
        "# Sample JSON as string\n",
        "json_string = '''[\n",
        "  {\"id\": 1, \"name\": \"Alice\", \"email\": \"alice@example.com\"},\n",
        "  {\"id\": 2, \"name\": \"Bob\", \"email\": \"bob@example.com\"}\n",
        "]'''\n",
        "\n",
        "# Parse string to list\n",
        "data = json.loads(json_string)\n",
        "print('Type:', type(data))\n",
        "\n",
        "# Normalize to DataFrame\n",
        "df = pd.json_normalize(data)\n",
        "print(df)"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Nested JSON with record_path"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "# JSON with nested structure\n",
        "nested_json = '''{\n",
        "  \"store\": \"store-1\",\n",
        "  \"orders\": [\n",
        "    {\"order_id\": \"o1\", \"items\": [{\"sku\": \"a\", \"qty\": 1}, {\"sku\": \"b\", \"qty\": 2}]},\n",
        "    {\"order_id\": \"o2\", \"items\": [{\"sku\": \"c\", \"qty\": 3}]}\n",
        "  ]\n",
        "}'''\n",
        "\n",
        "data = json.loads(nested_json)\n",
        "\n",
        "# Flatten with record_path and meta\n",
        "df = pd.json_normalize(data, record_path=['orders', 'items'], meta=[['orders', 'order_id'], 'store'], errors='ignore')\n",
        "print(df)"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Reading Your CA_category_id.json"
      ]
    },
    {
      "cell_type": "code",
      "execute_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "import json\n",
        "import pandas as pd\n",
        "import os\n",
        "\n",
        "# Path to your JSON file\n",
        "file_path = '../Streaming_platform_Data_Pipeline/Data1/CA_category_id.json'\n",
        "\n",
        "if os.path.exists(file_path):\n",
        "    # CORRECT WAY: parse with json.loads()\n",
        "    with open(file_path, 'r', encoding='utf-8') as f:\n",
        "        raw_string = f.read()  # Get string\n",
        "        data = json.loads(raw_string)  # Parse to dict/list\n",
        "    \n",
        "    print('Data type:', type(data))\n",
        "    print('Keys:', list(data.keys()) if isinstance(data, dict) else 'List')\n",
        "    \n",
        "    # Normalize based on structure\n",
        "    if isinstance(data, dict) and 'kind' in data:\n",
        "        df = pd.json_normalize(data['kind'])\n",
        "    elif isinstance(data, list):\n",
        "        df = pd.json_normalize(data)\n",
        "    else:\n",
        "        df = pd.json_normalize(data)\n",
        "    \n",
        "    print('\\nDataFrame shape:', df.shape)\n",
        "    print(df.head())\n",
        "else:\n",
        "    print(f'File not found at {file_path}')"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Practice: Exploding Arrays"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "import pandas as pd\n",
        "import json\n",
        "\n",
        "json_str = '''[\n",
        "  {\"id\": 1, \"tags\": [\"a\", \"b\", \"c\"]},\n",
        "  {\"id\": 2, \"tags\": [\"b\", \"d\"]}\n",
        "]'''\n",
        "\n",
        "data = json.loads(json_str)\n",
        "df = pd.json_normalize(data)\n",
        "print('Before explode:')\n",
        "print(df)\n",
        "\n",
        "print('\\nAfter explode (one tag per row):')\n",
        "df_exploded = df.explode('tags')\n",
        "print(df_exploded)"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Practice: Handling Missing Fields"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "import json\n",
        "import pandas as pd\n",
        "\n",
        "json_str = '''[\n",
        "  {\"id\": 1, \"name\": \"Alice\", \"email\": \"alice@ex.com\"},\n",
        "  {\"id\": 2, \"name\": \"Bob\"},\n",
        "  {\"id\": 3, \"email\": \"charlie@ex.com\"}\n",
        "]'''\n",
        "\n",
        "data = json.loads(json_str)\n",
        "df = pd.json_normalize(data)\n",
        "print('Raw (with NaN for missing fields):')\n",
        "print(df)\n",
        "\n",
        "print('\\nAfter fillna:')\n",
        "df_filled = df.fillna({'name': 'Unknown', 'email': 'no-email@ex.com'})\n",
        "print(df_filled)"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Summary\n",
        "1. **Key rule**: f.read() returns STRING → use json.loads() to parse\n",
        "2. **Simple lists**: pd.json_normalize(list_of_dicts)\n",
        "3. **Nested records**: use record_path + meta\n",
        "4. **Arrays**: use df.explode(column_name)\n",
        "5. **Missing fields**: NaN filled automatically, use fillna() to replace\n",
        "6. **Double-encoded**: detect string starting with '{' or '[' and json.loads() it again"
      ]
    }
  ]
}

# Write the notebook file
with open(notebook_path, 'w') as f:
    json.dump(notebook_content, f, indent=2)

print(f"✓ Notebook created at: {notebook_path}")
print(f"✓ File exists: {os.path.exists(notebook_path)}")
print(f"\nTo open it, run in terminal:")
print(f"  jupyter notebook {notebook_path}")
print(f"\nOr navigate to:")
print(f"  ~/Desktop/Projects/")
print(f"  and look for: json_normalization_practice.ipynb")