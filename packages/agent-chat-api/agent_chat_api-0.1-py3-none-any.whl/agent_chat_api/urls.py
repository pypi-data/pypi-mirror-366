from django.urls import path
from .views import (
    get_agent_memory_view, 
    send_message_stream_view, 
    get_agent_messages_view,
    create_agent_view,
    delete_agent_view,
    get_agent_view,
    create_memory_block_view,
    create_and_attach_memory_block_view,
    edit_memory_block_view,
    delete_memory_block_view,
    update_agent_view,
    transcribe_stream_view,
    modify_block_view,
    list_all_blocks_view,
    list_agents_for_block_view,
    export_agent_view,
    import_agent_view,
    create_source_view,
    delete_source_view,
    modify_source_view,
    list_sources_view,
    get_agents_for_source_view,
    attach_memory_block_view,
    detach_memory_block_view,
    attach_source_view,
    detach_source_view,
    list_source_files_view,
    delete_source_file_view,
    upload_file_to_source_view,
    list_all_tools_view,
    list_composio_apps_view,
    list_composio_actions_by_app_view,
    list_agent_tools_view,
    attach_tool_to_agent_view,
    detach_tool_from_agent_view,
    list_mcp_servers_view,
    add_mcp_server_view,
    list_mcp_tools_by_server_view,
    delete_mcp_server_view,
    update_mcp_server_view
)

urlpatterns = [
    path('agents/create/', create_agent_view, name='create_agent'),
    path('agents/one/<str:agent_id>/', get_agent_view, name='get_agent'),
    path('agents/<str:agent_id>/update/', update_agent_view, name='update_agent'),
    path('agents/<str:agent_id>/delete/', delete_agent_view, name='delete_agent'),
    path('agents/<str:agent_id>/export/', export_agent_view, name='export_agent'),
    path('agents/import/', import_agent_view, name='import_agent'),
    
    path('agents/<str:agent_id>/memory-blocks/create-attach/', create_and_attach_memory_block_view, name='create_and_attach_memory_block'),
    path('agents/<str:agent_id>/memory-blocks/<str:block_label>/update/', edit_memory_block_view, name='edit_memory_block'),
    path('agents/<str:agent_id>/memory-blocks/<str:block_id>/attach/', attach_memory_block_view, name='attach_memory_block'),
    path('agents/<str:agent_id>/memory-blocks/<str:block_id>/detach/', detach_memory_block_view, name='detach_memory_block'),
    
    path('agents/<str:agent_id>/sources/<str:source_id>/attach/', attach_source_view, name='attach_source'),
    path('agents/<str:agent_id>/sources/<str:source_id>/detach/', detach_source_view, name='detach_source'),
    
    path('agents/<str:agent_id>/tools/', list_agent_tools_view, name='list_agent_tools'),
    path('agents/<str:agent_id>/tools/<str:tool_id>/attach/', attach_tool_to_agent_view, name='attach_tool_to_agent'),
    path('agents/<str:agent_id>/tools/<str:tool_id>/detach/', detach_tool_from_agent_view, name='detach_tool_from_agent'),
    
    path('memory-blocks/create/', create_memory_block_view, name='create_memory_block'),
    path('memory-blocks/list/', list_all_blocks_view, name='list_all_blocks'),
    path('memory-blocks/<str:block_id>/update/', modify_block_view, name='modify_block'),
    path('memory-blocks/<str:block_id>/agents/', list_agents_for_block_view, name='list_agents_for_block'),
    path('memory-blocks/<str:block_id>/<str:block_label>/delete/', delete_memory_block_view, name='delete_memory_block'),
    
    path('sources/create/', create_source_view, name='create_source'),
    path('sources/list/', list_sources_view, name='list_sources'),
    path('sources/<str:source_id>/update/', modify_source_view, name='modify_source'),
    path('sources/<str:source_id>/delete/', delete_source_view, name='delete_source'),
    path('sources/<str:source_id>/agents/', get_agents_for_source_view, name='get_agents_for_source'),
    path('sources/<str:source_id>/files/', list_source_files_view, name='list_source_files'),
    path('sources/<str:source_id>/files/upload/', upload_file_to_source_view, name='upload_file_to_source'),
    path('sources/<str:source_id>/files/<str:file_id>/delete/', delete_source_file_view, name='delete_source_file'),
    
    path('agents/<str:agent_id>/memory/<str:block_label>/', get_agent_memory_view, name='get_agent_memory'),

    path('agents/<str:agent_id>/messages/stream/', send_message_stream_view, name='send_message_stream'),
    path('agents/<str:agent_id>/messages/', get_agent_messages_view, name='get_agent_messages'),

    path("transcribe/", transcribe_stream_view, name="transcribe_stream"),
    
    # Tool endpoints
    path('tools/', list_all_tools_view, name='list_all_tools'),
    path('tools/composio/apps/', list_composio_apps_view, name='list_composio_apps'),
    path('tools/composio/apps/<str:app_name>/actions/', list_composio_actions_by_app_view, name='list_composio_actions_by_app'),
    
    # MCP Server endpoints
    path('tools/mcp/servers/', list_mcp_servers_view, name='list_mcp_servers'),
    path('tools/mcp/servers/add/', add_mcp_server_view, name='add_mcp_server'),
    path('tools/mcp/servers/<str:mcp_server_name>/tools/', list_mcp_tools_by_server_view, name='list_mcp_tools_by_server'),
    path('tools/mcp/servers/<str:server_name>/delete/', delete_mcp_server_view, name='delete_mcp_server'),
    path('tools/mcp/servers/<str:server_name>/update/', update_mcp_server_view, name='update_mcp_server'),
] 