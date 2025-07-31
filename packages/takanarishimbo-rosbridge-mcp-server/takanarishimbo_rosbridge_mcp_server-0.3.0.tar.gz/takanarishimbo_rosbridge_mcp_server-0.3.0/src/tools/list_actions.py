"""
List Actions Tool

Lists all available ROS action servers.
"""

import asyncio
from typing import Any

import roslibpy
from mcp.types import Tool


LIST_ACTIONS_TOOL = Tool(
    name="list_actions",
    description="List all available ROS action servers",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)


async def list_actions(ros: roslibpy.Ros) -> dict[str, Any]:
    """
    List all available ROS action servers.

    Args:
        ros: The ROS connection instance

    Returns:
        A dictionary containing the list of action servers or error information
    """
    try:
        # Create a promise to handle the async rosbridge call
        future = asyncio.Future()
        
        def handle_action_servers(msg):
            future.set_result(msg)
        
        # Request action servers list from rosbridge
        ros.get_action_servers(handle_action_servers)
        
        # Wait for the response with timeout
        result = await asyncio.wait_for(future, timeout=5.0)
        
        # Format the response
        actions_list = []
        if 'action_servers' in result:
            for action_server in result['action_servers']:
                action_info = {
                    'name': action_server
                }
                actions_list.append(action_info)
        
        return {
            'success': True,
            'actions': actions_list,
            'count': len(actions_list)
        }
        
    except asyncio.TimeoutError:
        return {
            'success': False,
            'error': 'Timeout waiting for action servers list from rosbridge'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to list action servers: {str(e)}'
        }