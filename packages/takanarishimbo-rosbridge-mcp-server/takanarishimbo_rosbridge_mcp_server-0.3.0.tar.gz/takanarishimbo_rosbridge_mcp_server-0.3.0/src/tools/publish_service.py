"""
Publish Service Tool

Calls ROS services via rosbridge.
"""

import asyncio
from typing import Any

import roslibpy
from mcp.types import Tool


PUBLISH_SERVICE_TOOL = Tool(
    name="publish_service",
    description="Call a ROS service",
    inputSchema={
        "type": "object",
        "properties": {
            "service": {
                "type": "string",
                "description": "The ROS service name (e.g., '/add_two_ints')",
            },
            "service_type": {
                "type": "string",
                "description": "The ROS service type (e.g., 'rospy_tutorials/AddTwoInts')",
            },
            "request": {
                "type": "object",
                "description": "The service request data as a JSON object",
            },
            "timeout": {
                "type": "number",
                "description": "Timeout in seconds to wait for response (default: 10)",
                "default": 10,
            },
        },
        "required": ["service", "service_type", "request"],
    },
)


async def publish_service(
    ros: roslibpy.Ros, 
    service: str, 
    service_type: str, 
    request: dict[str, Any],
    timeout: float = 10.0
) -> dict[str, Any]:
    """
    Call a ROS service.

    Args:
        ros: The ROS connection instance
        service: The ROS service name
        service_type: The ROS service type
        request: The service request data as a dictionary
        timeout: Timeout in seconds to wait for response

    Returns:
        A dictionary containing the response or error information
    """
    try:
        # Create service client
        service_client = roslibpy.Service(ros, service, service_type)
        
        # Create a promise to handle the async service call
        future = asyncio.Future()
        
        def handle_response(response):
            future.set_result({
                'success': True,
                'response': response,
                'service': service
            })
        
        def handle_error(error):
            future.set_result({
                'success': False,
                'error': str(error),
                'service': service
            })
        
        # Create service request
        service_request = roslibpy.ServiceRequest(request)
        
        # Call the service
        service_client.call(service_request, handle_response, handle_error)
        
        # Wait for response with timeout
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            return {
                'success': False,
                'error': f'Timeout waiting for service response after {timeout} seconds',
                'service': service
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to call service: {str(e)}',
            'service': service
        }