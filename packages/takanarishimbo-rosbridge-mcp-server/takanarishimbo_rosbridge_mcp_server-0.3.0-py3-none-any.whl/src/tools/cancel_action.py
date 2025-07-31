"""
Cancel Action Tool

Cancels running ROS action goals via rosbridge.
"""

import asyncio
from typing import Any

import roslibpy
from mcp.types import Tool


CANCEL_ACTION_TOOL = Tool(
    name="cancel_action",
    description="Cancel a running ROS action goal",
    inputSchema={
        "type": "object",
        "properties": {
            "action_name": {
                "type": "string",
                "description": "The ROS action server name (e.g., '/move_base')",
            },
            "goal_id": {
                "type": "string",
                "description": "The goal ID to cancel (optional, cancels all goals if not provided)",
            },
        },
        "required": ["action_name"],
    },
)


async def cancel_action(
    ros: roslibpy.Ros, 
    action_name: str, 
    goal_id: str = None
) -> dict[str, Any]:
    """
    Cancel a running ROS action goal.

    Args:
        ros: The ROS connection instance
        action_name: The ROS action server name
        goal_id: The specific goal ID to cancel (optional)

    Returns:
        A dictionary containing the result or error information
    """
    try:
        # Create a promise to handle the async rosbridge call
        future = asyncio.Future()
        
        # Create the cancel message
        cancel_msg = {
            'op': 'cancel_action_goal',
            'action': action_name
        }
        
        if goal_id:
            cancel_msg['id'] = goal_id
        
        def handle_response(msg):
            future.set_result(msg)
        
        # Send cancel request
        ros.send_on_ready(cancel_msg)
        
        # For cancel operations, we don't expect a response in all cases
        # So we'll just confirm the message was sent
        await asyncio.sleep(0.1)  # Small delay to ensure message is sent
        
        if goal_id:
            return {
                'success': True,
                'message': f"Cancel request sent for goal '{goal_id}' on action '{action_name}'"
            }
        else:
            return {
                'success': True,
                'message': f"Cancel request sent for all goals on action '{action_name}'"
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to cancel action: {str(e)}'
        }