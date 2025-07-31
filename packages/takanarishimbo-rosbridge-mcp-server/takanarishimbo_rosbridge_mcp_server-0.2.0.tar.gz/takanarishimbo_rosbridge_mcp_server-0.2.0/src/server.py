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
from typing import Any

import roslibpy
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

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
2. Tool Definition

Define the publish_topic tool with its schema

Examples:
  Tool name: "publish_topic"
  Input: { topic: "/cmd_vel", message_type: "geometry_msgs/Twist", message: {...} }
  Input: { topic: "/chatter", message_type: "std_msgs/String", message: {data: "Hello"} }
  Required: topic, message_type, message
  ROS message types: Any valid ROS message type (e.g., "geometry_msgs/Twist", "std_msgs/String")

2. ツール定義

publish_topicツールとそのスキーマを定義

例:
  ツール名: "publish_topic"
  入力: { topic: "/cmd_vel", message_type: "geometry_msgs/Twist", message: {...} }
  入力: { topic: "/chatter", message_type: "std_msgs/String", message: {data: "Hello"} }
  必須: topic, message_type, message
  ROSメッセージタイプ: 有効なROSメッセージタイプ (例: "geometry_msgs/Twist", "std_msgs/String")
"""
PUBLISH_TOPIC_TOOL = Tool(
    name="publish_topic",
    description="Publish a message to a ROS topic via rosbridge",
    inputSchema={
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The ROS topic name (e.g., '/cmd_vel')",
            },
            "message_type": {
                "type": "string",
                "description": "The ROS message type (e.g., 'geometry_msgs/Twist')",
            },
            "message": {
                "type": "object",
                "description": "The message data as a JSON object",
            },
        },
        "required": ["topic", "message_type", "message"],
    },
)

"""
3. Server Initialization

Create MCP server instance with metadata

Examples:
  Server name: "rosbridge-mcp-server"
  Version: "0.1.0"
  Protocol: Model Context Protocol (MCP)

3. サーバー初期化

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
4. Topic Publishing Function

Publish messages to ROS topics

Examples:
  publish_topic("/cmd_vel", "geometry_msgs/Twist", {linear: {x: 0.5}}) → Success message
  publish_topic("/chatter", "std_msgs/String", {data: "Hello"}) → Success message
  Invalid topic → Error message
  Connection error → "Failed to publish to topic '/topic': Connection error"

4. トピック公開関数

ROSトピックにメッセージを公開

例:
  publish_topic("/cmd_vel", "geometry_msgs/Twist", {linear: {x: 0.5}}) → 成功メッセージ
  publish_topic("/chatter", "std_msgs/String", {data: "Hello"}) → 成功メッセージ
  無効なトピック → エラーメッセージ
  接続エラー → "Failed to publish to topic '/topic': Connection error"
"""


async def publish_topic(topic: str, message_type: str, message: dict[str, Any]) -> str:
    """
    Publish a message to a ROS topic.

    Args:
        topic: The ROS topic name
        message_type: The ROS message type
        message: The message data as a dictionary

    Returns:
        A status message indicating success or failure
    """
    try:
        # Create topic
        t = roslibpy.Topic(ros, topic, message_type)

        # Advertise
        t.advertise()

        # Small delay to ensure advertise is processed
        await asyncio.sleep(0.1)

        # Publish message
        msg = roslibpy.Message(message)
        t.publish(msg)

        # Small delay to ensure publish is processed
        await asyncio.sleep(0.1)

        # Unadvertise
        t.unadvertise()

        return f"Successfully published message to topic '{topic}' with type '{message_type}'"

    except Exception as e:
        error_msg = f"Failed to publish to topic '{topic}': {str(e)}"
        print(error_msg)
        return error_msg


"""
5. Tool List Handler

Handle requests to list available tools

Examples:
  Request: ListToolsRequest → Response: { tools: [PUBLISH_TOPIC_TOOL] }
  Available tools: publish_topic
  Tool count: 1
  This handler responds to MCP clients asking what tools are available

5. ツールリストハンドラー

利用可能なツールをリストするリクエストを処理

例:
  リクエスト: ListToolsRequest → レスポンス: { tools: [PUBLISH_TOPIC_TOOL] }
  利用可能なツール: publish_topic
  ツール数: 1
  このハンドラーは利用可能なツールを尋ねるMCPクライアントに応答
"""


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools.

    Returns a list of tools that this MCP server provides.
    Currently provides only the publish_topic tool.
    """
    return [PUBLISH_TOPIC_TOOL]


"""
6. Tool Call Handler

Set up the request handler for tool calls

Examples:
  Request: { name: "publish_topic", arguments: {topic: "/cmd_vel", ...} } → Publishes message
  Request: { name: "publish_topic", arguments: {} } → Error: Missing required arguments
  Request: { name: "unknown_tool" } → Error: "Unknown tool: unknown_tool"
  Connection error → Error: "Failed to publish to topic..."

6. ツール呼び出しハンドラー

ツール呼び出しのリクエストハンドラーを設定

例:
  リクエスト: { name: "publish_topic", arguments: {topic: "/cmd_vel", ...} } → メッセージを公開
  リクエスト: { name: "publish_topic", arguments: {} } → エラー: 必須引数が不足
  リクエスト: { name: "unknown_tool" } → エラー: "Unknown tool: unknown_tool"
  接続エラー → エラー: "Failed to publish to topic..."
"""


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    """
    Handle tool execution requests.

    Process tool calls from MCP clients and publish messages to ROS topics.

    Args:
        name: The name of the tool to execute
        arguments: Tool-specific arguments (topic, message_type, message)

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

        result = await publish_topic(topic, message_type, message)
        is_error = result.startswith("Failed")

        return [
            {
                "type": "text",
                "text": result,
                "isError": is_error,
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
7. Server Startup Function

Initialize and run the MCP server with stdio transport

Examples:
  Normal startup → "Rosbridge MCP Server running on stdio"
  Transport: stdio (communicates via stdin/stdout)
  Connection error → Process exits with appropriate error

7. サーバー起動関数

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
8. Server Execution

Execute the server when run as a script

Examples:
  Direct execution: python server.py
  Via uvx: uvx rosbridge-mcp-server
  With environment: ROSBRIDGE_HOST=localhost ROSBRIDGE_PORT=9090 python server.py
  Fatal error → Exits with appropriate error code

8. サーバー実行

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


if __name__ == "__main__":
    main()
