"""
Get Topic Info Tool

Gets detailed information about a specific ROS topic.
"""

import asyncio
from typing import Any

import roslibpy
from mcp.types import Tool


GET_TOPIC_INFO_TOOL = Tool(
    name="get_topic_info",
    description="Get detailed information about a specific ROS topic",
    inputSchema={
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The ROS topic name (e.g., '/cmd_vel')",
            },
        },
        "required": ["topic"],
    },
)


async def get_topic_info(ros: roslibpy.Ros, topic: str) -> dict[str, Any]:
    """
    Get detailed information about a specific ROS topic.

    Args:
        ros: The ROS connection instance
        topic: The ROS topic name

    Returns:
        A dictionary containing topic information or error information
    """
    try:
        # Create a promise to handle the async rosbridge call
        future = asyncio.Future()
        
        def handle_topic_type(msg):
            future.set_result(msg)
        
        # Request topic type from rosbridge
        ros.get_topic_type(topic, handle_topic_type)
        
        # Wait for the response with timeout
        result = await asyncio.wait_for(future, timeout=5.0)
        
        if result is None:
            return {
                'success': False,
                'error': f'Topic {topic} not found'
            }
        
        # Get publishers and subscribers info
        publishers_future = asyncio.Future()
        subscribers_future = asyncio.Future()
        
        def handle_publishers(msg):
            publishers_future.set_result(msg)
        
        def handle_subscribers(msg):
            subscribers_future.set_result(msg)
            
        # Request publishers and subscribers
        ros.get_publishers(topic, handle_publishers)
        ros.get_subscribers(topic, handle_subscribers)
        
        # Wait for responses
        publishers = await asyncio.wait_for(publishers_future, timeout=5.0)
        subscribers = await asyncio.wait_for(subscribers_future, timeout=5.0)
        
        return {
            'success': True,
            'topic': topic,
            'type': result,
            'publishers': publishers if publishers else [],
            'subscribers': subscribers if subscribers else [],
            'publisher_count': len(publishers) if publishers else 0,
            'subscriber_count': len(subscribers) if subscribers else 0
        }
        
    except asyncio.TimeoutError:
        return {
            'success': False,
            'error': f'Timeout waiting for topic info for {topic}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to get topic info: {str(e)}'
        }