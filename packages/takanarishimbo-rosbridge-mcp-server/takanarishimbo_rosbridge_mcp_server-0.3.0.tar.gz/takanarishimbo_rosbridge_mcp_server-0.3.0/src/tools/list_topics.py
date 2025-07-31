"""
List Topics Tool

Lists all available ROS topics.
"""

import asyncio
from typing import Any

import roslibpy
from mcp.types import Tool


LIST_TOPICS_TOOL = Tool(
    name="list_topics",
    description="List all available ROS topics",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)


async def list_topics(ros: roslibpy.Ros) -> dict[str, Any]:
    """
    List all available ROS topics.

    Args:
        ros: The ROS connection instance

    Returns:
        A dictionary containing the list of topics or error information
    """
    try:
        # Create a promise to handle the async rosbridge call
        future = asyncio.Future()
        
        def handle_topics(msg):
            future.set_result(msg)
        
        # Request topics list from rosbridge
        ros.get_topics(handle_topics)
        
        # Wait for the response with timeout
        result = await asyncio.wait_for(future, timeout=5.0)
        
        # Format the response
        topics_list = []
        if 'topics' in result:
            for i, topic in enumerate(result['topics']):
                topic_info = {
                    'name': topic,
                    'type': result.get('types', [])[i] if i < len(result.get('types', [])) else 'unknown'
                }
                topics_list.append(topic_info)
        
        return {
            'success': True,
            'topics': topics_list,
            'count': len(topics_list)
        }
        
    except asyncio.TimeoutError:
        return {
            'success': False,
            'error': 'Timeout waiting for topics list from rosbridge'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to list topics: {str(e)}'
        }