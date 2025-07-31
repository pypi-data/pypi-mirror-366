"""
Publish Topic Tool

Publishes messages to ROS topics via rosbridge.
"""

import asyncio
from typing import Any

import roslibpy
from mcp.types import Tool


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


async def publish_topic(ros: roslibpy.Ros, topic: str, message_type: str, message: dict[str, Any]) -> str:
    """
    Publish a message to a ROS topic.

    Args:
        ros: The ROS connection instance
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