#!/usr/bin/env python3
"""
0. Rosbridge MCP Server

This server provides tools to publish messages to ROS topics via rosbridge.

Environment Variables:
- ROSBRIDGE_HOST: The rosbridge server host (default: "localhost")
- ROSBRIDGE_PORT: The rosbridge server port (default: "9090")

Example:
  ROSBRIDGE_HOST=localhost uvx rosbridge-mcp-server
  ROSBRIDGE_HOST=192.168.1.100 ROSBRIDGE_PORT=9091 uvx rosbridge-mcp-server

0. Rosbridge MCPサーバー

このサーバーは、rosbridgeを介してROSトピックにメッセージを公開するツールを提供します。

環境変数:
- ROSBRIDGE_HOST: rosbridgeサーバーのホスト (デフォルト: "localhost")
- ROSBRIDGE_PORT: rosbridgeサーバーのポート (デフォルト: "9090")

例:
  ROSBRIDGE_HOST=localhost uvx rosbridge-mcp-server
  ROSBRIDGE_HOST=192.168.1.100 ROSBRIDGE_PORT=9091 uvx rosbridge-mcp-server
"""

import asyncio
import os

import roslibpy
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .tools import (
    LIST_TOPICS_TOOL,
    LIST_ACTIONS_TOOL,
    LIST_SERVICES_TOOL,
    GET_TOPIC_INFO_TOOL,
    PUBLISH_TOPIC_TOOL,
    PUBLISH_ACTION_TOOL,
    CANCEL_ACTION_TOOL,
    PUBLISH_SERVICE_TOOL,
    list_topics,
    list_actions,
    list_services,
    get_topic_info,
    publish_topic,
    publish_action,
    cancel_action,
    publish_service,
)

# Server version

"""
1. Environment Configuration

Get configuration from environment variables

Examples:
  ROSBRIDGE_HOST="localhost" → Connect to local rosbridge
  ROSBRIDGE_PORT="9090" → Use default rosbridge port
  ROSBRIDGE_HOST="192.168.1.100" ROSBRIDGE_PORT="9091" → Connect to remote rosbridge
  No environment variables → Defaults to localhost:9090

1. 環境設定

環境変数から設定を取得

例:
  ROSBRIDGE_HOST="localhost" → ローカルのrosbridgeに接続
  ROSBRIDGE_PORT="9090" → デフォルトのrosbridgeポートを使用
  ROSBRIDGE_HOST="192.168.1.100" ROSBRIDGE_PORT="9091" → リモートのrosbridgeに接続
  環境変数なし → localhost:9090をデフォルト使用
"""
ROSBRIDGE_HOST = os.environ.get("ROSBRIDGE_HOST", "localhost")
ROSBRIDGE_PORT = int(os.environ.get("ROSBRIDGE_PORT", "9090"))

"""
2. Server Initialization

Create MCP server instance with metadata

Examples:
  Server name: "rosbridge-mcp-server"
  Version: "0.1.0"
  Protocol: Model Context Protocol (MCP)

2. サーバー初期化

メタデータを持つMCPサーバーインスタンスを作成

例:
  サーバー名: "rosbridge-mcp-server"
  バージョン: "0.1.0"
  プロトコル: Model Context Protocol (MCP)
"""
app = Server("rosbridge-mcp-server")
ros = roslibpy.Ros(host=ROSBRIDGE_HOST, port=ROSBRIDGE_PORT)
ros.run()


"""
3. Tool List Handler

Handle requests to list available tools

Examples:
  Request: ListToolsRequest → Response: { tools: [PUBLISH_TOPIC_TOOL, LIST_TOPICS_TOOL, ...] }
  Available tools: publish_topic, list_topics, list_actions, list_services
  Tool count: 4
  This handler responds to MCP clients asking what tools are available

3. ツールリストハンドラー

利用可能なツールをリストするリクエストを処理

例:
  リクエスト: ListToolsRequest → レスポンス: { tools: [PUBLISH_TOPIC_TOOL, LIST_TOPICS_TOOL, ...] }
  利用可能なツール: publish_topic, list_topics, list_actions, list_services
  ツール数: 4
  このハンドラーは利用可能なツールを尋ねるMCPクライアントに応答
"""


@app.list_tools()
async def list_tools() -> list:
    """
    List all available tools.

    Returns a list of tools that this MCP server provides.
    """
    return [
        PUBLISH_TOPIC_TOOL,
        LIST_TOPICS_TOOL,
        LIST_ACTIONS_TOOL,
        LIST_SERVICES_TOOL,
        GET_TOPIC_INFO_TOOL,
        PUBLISH_ACTION_TOOL,
        CANCEL_ACTION_TOOL,
        PUBLISH_SERVICE_TOOL,
    ]


"""
4. Tool Call Handler

Set up the request handler for tool calls

Examples:
  Request: { name: "publish_topic", arguments: {topic: "/cmd_vel", ...} } → Publishes message
  Request: { name: "list_topics", arguments: {} } → Lists available topics
  Request: { name: "unknown_tool" } → Error: "Unknown tool: unknown_tool"
  Connection error → Error: "Failed to..."

4. ツール呼び出しハンドラー

ツール呼び出しのリクエストハンドラーを設定

例:
  リクエスト: { name: "publish_topic", arguments: {topic: "/cmd_vel", ...} } → メッセージを公開
  リクエスト: { name: "list_topics", arguments: {} } → 利用可能なトピックをリスト
  リクエスト: { name: "unknown_tool" } → エラー: "Unknown tool: unknown_tool"
  接続エラー → エラー: "Failed to..."
"""


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    """
    Handle tool execution requests.

    Process tool calls from MCP clients and execute various ROS operations.

    Args:
        name: The name of the tool to execute
        arguments: Tool-specific arguments

    Returns:
        A list containing the tool execution result or error message
    """
    if name == "publish_topic":
        topic = arguments.get("topic")
        message_type = arguments.get("message_type")
        message = arguments.get("message")

        if not all([topic, message_type, message]):
            return [
                {
                    "type": "text",
                    "text": "Error: Missing required arguments. Please provide 'topic', 'message_type', and 'message'.",
                    "isError": True,
                }
            ]

        result = await publish_topic(ros, topic, message_type, message)
        is_error = result.startswith("Failed")

        return [
            {
                "type": "text",
                "text": result,
                "isError": is_error,
            }
        ]

    elif name == "list_topics":
        result = await list_topics(ros)

        if result["success"]:
            # Format topics list for display
            topics_text = f"Found {result['count']} topics:\n"
            for topic in result["topics"]:
                topics_text += f"  - {topic['name']} [{topic['type']}]\n"

            return [
                {
                    "type": "text",
                    "text": topics_text.strip(),
                    "isError": False,
                }
            ]
        else:
            return [
                {
                    "type": "text",
                    "text": f"Error: {result['error']}",
                    "isError": True,
                }
            ]

    elif name == "list_actions":
        result = await list_actions(ros)

        if result["success"]:
            # Format actions list for display
            actions_text = f"Found {result['count']} action servers:\n"
            for action in result["actions"]:
                actions_text += f"  - {action['name']}\n"

            return [
                {
                    "type": "text",
                    "text": actions_text.strip(),
                    "isError": False,
                }
            ]
        else:
            return [
                {
                    "type": "text",
                    "text": f"Error: {result['error']}",
                    "isError": True,
                }
            ]

    elif name == "list_services":
        result = await list_services(ros)

        if result["success"]:
            # Format services list for display
            services_text = f"Found {result['count']} services:\n"
            for service in result["services"]:
                services_text += f"  - {service['name']}\n"

            return [
                {
                    "type": "text",
                    "text": services_text.strip(),
                    "isError": False,
                }
            ]
        else:
            return [
                {
                    "type": "text",
                    "text": f"Error: {result['error']}",
                    "isError": True,
                }
            ]

    elif name == "get_topic_info":
        topic = arguments.get("topic")

        if not topic:
            return [
                {
                    "type": "text",
                    "text": "Error: Missing required argument 'topic'.",
                    "isError": True,
                }
            ]

        result = await get_topic_info(ros, topic)

        if result["success"]:
            # Format topic info for display
            info_text = f"Topic: {result['topic']}\n"
            info_text += f"Type: {result['type']}\n"
            info_text += f"Publishers: {result['publisher_count']}\n"
            if result["publishers"]:
                for pub in result["publishers"]:
                    info_text += f"  - {pub}\n"
            info_text += f"Subscribers: {result['subscriber_count']}\n"
            if result["subscribers"]:
                for sub in result["subscribers"]:
                    info_text += f"  - {sub}\n"

            return [
                {
                    "type": "text",
                    "text": info_text.strip(),
                    "isError": False,
                }
            ]
        else:
            return [
                {
                    "type": "text",
                    "text": f"Error: {result['error']}",
                    "isError": True,
                }
            ]

    elif name == "publish_action":
        action_name = arguments.get("action_name")
        action_type = arguments.get("action_type")
        goal = arguments.get("goal")
        timeout = arguments.get("timeout", 30.0)

        if not all([action_name, action_type, goal]):
            return [
                {
                    "type": "text",
                    "text": "Error: Missing required arguments. Please provide 'action_name', 'action_type', and 'goal'.",
                    "isError": True,
                }
            ]

        result = await publish_action(ros, action_name, action_type, goal, timeout)

        if result["success"]:
            # Format action result for display
            result_text = f"Action completed successfully!\n"
            result_text += f"Goal ID: {result['goal_id']}\n"
            result_text += f"Result: {result['result']}\n"
            if result["feedback"]:
                result_text += f"Feedback received: {len(result['feedback'])} messages"

            return [
                {
                    "type": "text",
                    "text": result_text.strip(),
                    "isError": False,
                }
            ]
        else:
            return [
                {
                    "type": "text",
                    "text": f"Error: {result['error']}",
                    "isError": True,
                }
            ]

    elif name == "cancel_action":
        action_name = arguments.get("action_name")
        goal_id = arguments.get("goal_id")

        if not action_name:
            return [
                {
                    "type": "text",
                    "text": "Error: Missing required argument 'action_name'.",
                    "isError": True,
                }
            ]

        result = await cancel_action(ros, action_name, goal_id)

        return [
            {
                "type": "text",
                "text": result["message"] if result["success"] else f"Error: {result['error']}",
                "isError": not result["success"],
            }
        ]

    elif name == "publish_service":
        service = arguments.get("service")
        service_type = arguments.get("service_type")
        request = arguments.get("request")
        timeout = arguments.get("timeout", 10.0)

        if not all([service, service_type, request]):
            return [
                {
                    "type": "text",
                    "text": "Error: Missing required arguments. Please provide 'service', 'service_type', and 'request'.",
                    "isError": True,
                }
            ]

        result = await publish_service(ros, service, service_type, request, timeout)

        if result["success"]:
            # Format service response for display
            response_text = f"Service call successful!\n"
            response_text += f"Service: {result['service']}\n"
            response_text += f"Response: {result['response']}"

            return [
                {
                    "type": "text",
                    "text": response_text.strip(),
                    "isError": False,
                }
            ]
        else:
            return [
                {
                    "type": "text",
                    "text": f"Error: {result['error']}",
                    "isError": True,
                }
            ]

    else:
        return [
            {
                "type": "text",
                "text": f"Unknown tool: {name}",
                "isError": True,
            }
        ]


"""
5. Server Startup Function

Initialize and run the MCP server with stdio transport

Examples:
  Normal startup → "Rosbridge MCP Server running on stdio"
  Transport: stdio (communicates via stdin/stdout)
  Connection error → Process exits with appropriate error

5. サーバー起動関数

stdioトランスポートでMCPサーバーを初期化して実行

例:
  通常の起動 → "Rosbridge MCP Server running on stdio"
  トランスポート: stdio (stdin/stdout経由で通信)
  接続エラー → プロセスは適切なエラーで終了
"""


async def run_server():
    """
    Initialize and run the MCP server with stdio transport.

    Sets up the stdio communication channels, prints startup information,
    and starts the MCP server. The server communicates via standard input/output streams.
    """
    print("Rosbridge MCP Server running on stdio")
    print(f"Connecting to rosbridge at {ROSBRIDGE_HOST}:{ROSBRIDGE_PORT}")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


"""
6. Server Execution

Execute the server when run as a script

Examples:
  Direct execution: python server.py
  Via uvx: uvx rosbridge-mcp-server
  With environment: ROSBRIDGE_HOST=localhost ROSBRIDGE_PORT=9090 python server.py
  Fatal error → Exits with appropriate error code

6. サーバー実行

スクリプトとして実行されたときにサーバーを実行

例:
  直接実行: python server.py
  uvx経由: uvx rosbridge-mcp-server
  環境変数付き: ROSBRIDGE_HOST=localhost ROSBRIDGE_PORT=9090 python server.py
  致命的なエラー → 適切なエラーコードで終了
"""


def main():
    """
    Main entry point for the server.

    Starts the MCP server and handles any startup errors.
    """
    asyncio.run(run_server())
