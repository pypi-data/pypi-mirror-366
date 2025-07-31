"""
List Services Tool

Lists all available ROS services.
"""

import asyncio
from typing import Any

import roslibpy
from mcp.types import Tool


LIST_SERVICES_TOOL = Tool(
    name="list_services",
    description="List all available ROS services",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)


async def list_services(ros: roslibpy.Ros) -> dict[str, Any]:
    """
    List all available ROS services.

    Args:
        ros: The ROS connection instance

    Returns:
        A dictionary containing the list of services or error information
    """
    try:
        # Create a promise to handle the async rosbridge call
        future = asyncio.Future()
        
        def handle_services(msg):
            future.set_result(msg)
        
        # Request services list from rosbridge
        ros.get_services(handle_services)
        
        # Wait for the response with timeout
        result = await asyncio.wait_for(future, timeout=5.0)
        
        # Format the response
        services_list = []
        if 'services' in result:
            for service in result['services']:
                service_info = {
                    'name': service
                }
                services_list.append(service_info)
        
        return {
            'success': True,
            'services': services_list,
            'count': len(services_list)
        }
        
    except asyncio.TimeoutError:
        return {
            'success': False,
            'error': 'Timeout waiting for services list from rosbridge'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to list services: {str(e)}'
        }