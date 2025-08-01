<p align="center">English | <a href="./README_CN.md">中文</a><br></p>
# Alibaba Cloud PolarDB OpenAPI MCP Server
MCP server for PolarDB Services via OPENAPI

## Prerequisites
1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
2. Install Python using `uv python install 3.12`
3. Alibaba Cloud credentials with access to Alibaba Cloud PolarDB services

## Quick Start

### Option 1: Simple Setup with [cherry-studio](https://github.com/CherryHQ/cherry-studio) (Recommended)

**No manual installation required!** Simply import this JSON configuration in Cherry Studio:

```json
{
  "mcpServers": {
    "polardb-openapi": {
      "command": "uvx",
      "args": [
        "--from",
        "polardb-openapi-mcp-server==0.2.0a1",
        "run_polardb_openapi_mcp_server"
      ],
      "env": {
        "ALIBABA_CLOUD_ACCESS_KEY_ID": "your-access-key-id",
        "ALIBABA_CLOUD_ACCESS_KEY_SECRET": "your-access-key-secret",
        "ALIBABA_CLOUD_REGION": "cn-hangzhou",
        "RUN_MODE": "stdio"
      }
    }
  }
}
```

Replace the credentials with your actual Alibaba Cloud access keys, and Cherry Studio will automatically handle installation and execution.

### Option 2: Manual Setup with [cherry-studio](https://github.com/CherryHQ/cherry-studio)

#### 1. Download the Code

Clone the project from Github:

```shell
git clone https://github.com/aliyun/alibabacloud-polardb-mcp-server.git

cd alibabacloud-polardb-mcp-server/polardb-openapi-mcp-server
```
#### 2. Configure Environment Variables

Create a `.env` file in the project root directory. Below is an example configuration:

```env
RUN_MODE=sse
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
SSE_BIND_HOST=127.0.0.1
SSE_BIND_PORT=12345
```

Please replace `your_access_key_id` and `your_access_key_secret` with your actual Alibaba Cloud credentials.

#### 3. Install Dependencies and Start the server

Create a virtual environment, install dependencies, and start the server:

```shell
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
python server.py
```

#### 4. Configure Cherry Studio
To configure the MCP server in Cherry Studio:

- Select server type: `sse`
- Enter URL: `http://127.0.0.1:12345/sse`

Once configured, you can start the server.

### Using Claude
Download from Github
```shell
git clone https://github.com/aliyun/alibabacloud-polardb-mcp-server.git
```
Add the following configuration to the MCP client configuration file (claude_desktop_config.json):
```json5
{
  "mcpServers": {
    "polardb-openapi-mcp-server": {
      "command": "/bin/bash",
      "args": [
        "/path/to/polardb_mcp_server/polardb-openapi-mcp-server/start_mcp_server.sh",
        "/path/to/polardb_mcp_server/polardb-openapi-mcp-server"
      ]
    }
 }
}
```

### Using Local Client
* Security & Privacy: Your organization may have policies restricting the use of cloud-based MCP clients, as they typically log operational activities that could contain sensitive or proprietary information.
* Reliability & Ease of Use: Many existing MCP clients can be complex to configure and may experience frequent downtime due to high traffic loads. Our local client provides a stable, straightforward alternative for managing your PolarDB OpenAPI MCP server.
* PolarDB Optimization: Our client includes specialized PolarDB domain knowledge and enhanced features specifically designed for PolarDB operations that are not available in generic MCP clients.

Start your local MCP client service with the following command:

**Option 1: Using the startup script (recommended):**
```shell
cd /path/to/polardb_mcp_server/polardb-openapi-mcp-server
./start_web_client.sh
```

**Option 2: Manual startup:**
```shell
cd /path/to/polardb_mcp_server/polardb-openapi-mcp-server
source .venv/bin/activate
uv pip install flask>=2.0.0  # Ensure Flask is installed
python3 fixed_mcp_protocol_web.py /path/to/polardb_mcp_server/polardb-openapi-mcp-server
```

You can then open the following URL in your browser to access the MCP client:
http://localhost:4657/

You can then ask any question by input question into "Natural Language Interface", then press "Ask" button.

## Components
### OpenAPI Tools
* `polardb_create_cluster`: Create a new PolarDB cluster.
* `polardb_create_db_endpoint_address`: Create a new database endpoint address for a PolarDB cluster.
* `polardb_create_account`: Create a database account for a PolarDB cluster with specified privileges.
* `polardb_describe_regions`: List all available regions for Alibaba Cloud PolarDB.
* `polardb_describe_db_clusters`: List all PolarDB clusters in a specific region with comprehensive cluster details.
* `polardb_describe_db_cluster`: Get detailed information about a specific PolarDB cluster.
* `polardb_describe_available_resources`: List available resources for creating PolarDB clusters.
* `polardb_describe_db_node_parameters`: Get configuration parameters for a specific PolarDB database node.
* `polardb_describe_slow_log_records`: Get slow log records for a specific PolarDB cluster within a time range.
* `polardb_describe_db_node_performance`: Get performance metrics for a specific PolarDB database node within a time range.
* `polardb_describe_db_cluster_access_whitelist`: Get the current active access whitelist configuration for a PolarDB cluster.
* `polardb_describe_accounts`: List database accounts for a PolarDB cluster, including account types, status, and database privileges.
* `polardb_describe_databases`: List databases in a specific PolarDB cluster, optionally filtered by database name.
* `polardb_describe_db_cluster_endpoints`: List database endpoints for a specific PolarDB cluster, including connection strings and IP addresses.
* `polardb_describe_db_cluster_parameters`: Get configuration parameters for a PolarDB cluster, organized by category with important parameters highlighted.
* `polardb_describe_db_cluster_performance`: Get performance metrics for a specific PolarDB cluster within a time range with enhanced analysis.
* `polardb_describe_global_security_ipgroup_relation`: Get global security IP group relations for a specific PolarDB cluster.
* `polardb_describe_db_cluster_connectivity`: Test network connectivity to a PolarDB cluster from a specific source IP address.
* `polardb_describe_db_proxy_performance`: Get proxy performance metrics for a specific PolarDB cluster within a time range with enhanced analysis.
* `polardb_describe_error_log_records`: Get error log records for a specific PolarDB cluster/instance within a time range using DAS API. Helps identify database errors, connection issues, and server problems.
* `polardb_modify_db_node_parameters`: Modify configuration parameters for PolarDB database nodes.
* `polardb_modify_db_cluster_access_whitelist`: Modify the access whitelist for a PolarDB cluster to control which IP addresses can connect.
* `polardb_modify_db_cluster_description`: Modify the description of a PolarDB cluster with comprehensive validation and formatting guidelines.
* `polardb_modify_db_cluster_parameters`: Modify configuration parameters for PolarDB cluster.
* `polardb_tag_resources`: Add tags to PolarDB resources (clusters, nodes, etc.).
* `polardb_extract_node_ids`: Extract node IDs from a PolarDB cluster by role (reader/writer).
* `polardb_restart_db_node`: Restart a specific PolarDB database node with comprehensive monitoring guidance and safety recommendations.
* `vpc_describe_vpcs`: List all VPCs (Virtual Private Clouds) in a specific region with detailed network configuration information.
* `vpc_describe_vswitches`: List all VSwitches (Virtual Switches) in a specific region with detailed subnet configuration information.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License
This project is licensed under the Apache 2.0 License.
