from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from pydantic import ValidationError

from agent_chat_api.services.transcription_service import TranscriptionService
from .services.agent_service import AgentService
from .services.chat_service import ChatService
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import StreamingHttpResponse
import os


# AGENT VIEWS

@csrf_exempt
@require_http_methods(["POST"])
async def create_agent_view(request):
    try:
        data = json.loads(request.body)
        name = data.get("name")
        agent_definition = data.get("agent_definition", {})
        user_full_name = data.get("user_full_name")
        user_id = data.get("user_id")
        
        # Validate required fields
        if not name:
            return JsonResponse({"error": "Agent name is required"}, status=400)
        if not user_full_name:
            return JsonResponse({"error": "User full name is required"}, status=400)
        if not user_id:
            return JsonResponse({"error": "User ID is required"}, status=400)
        
        agent_id = await AgentService.create_agent(name, agent_definition, user_full_name, user_id)
        
        return JsonResponse({
            "agent_id": agent_id,
            "message": "Agent created successfully"
        }, status=201)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PATCH"])
async def update_agent_view(request, agent_id: str):
    try:
        data = json.loads(request.body)
        
        # Extract all possible parameters from the request
        name = data.get("name")
        system_prompt = data.get("system")
        description = data.get("description")
        model = data.get("model")
        embedding = data.get("embedding")
        
        # Check if at least one field is being updated
        if all(param is None for param in [name, system_prompt, description, model, embedding]):
            return JsonResponse({"error": "At least one field must be provided for update"}, status=400)
        
        updated_agent = await AgentService.update_agent(
            agent_id=agent_id,
            name=name,
            system_prompt=system_prompt,
            description=description,
            model=model,
            embedding=embedding
        )
        
        if updated_agent:
            return JsonResponse(updated_agent, status=200)
        else:
            return JsonResponse({"error": "Failed to update agent"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 


@csrf_exempt
@require_http_methods(["DELETE"])
async def delete_agent_view(request, agent_id: str):
    try:
        await AgentService.delete_agent(agent_id)
        
        return JsonResponse({
            "message": "Agent deleted successfully"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
async def get_agent_view(request, agent_id: str):
    try:
        agent = await AgentService.get_agent(agent_id)
        if agent is None:
            return JsonResponse({"error": f"Agent {agent_id} not found"}, status=404)
        return JsonResponse(agent)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
async def export_agent_view(request, agent_id: str):
    try:
        exported_data = await AgentService.export_agent(agent_id)
        if exported_data:
            return JsonResponse({"agent_data": exported_data})
        else:
            return JsonResponse({"error": "Failed to export agent"}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
async def import_agent_view(request):
    try:
        # Get query parameters with defaults
        append_copy_suffix = request.GET.get('append_copy_suffix', 'true').lower() == 'true'
        override_existing_tools = request.GET.get('override_existing_tools', 'true').lower() == 'true'
        strip_messages = request.GET.get('strip_messages', 'true').lower() == 'true'
        
        # Check if JSON data is provided in the request body
        json_data = None
        file_data = None
        
        if request.content_type and 'application/json' in request.content_type:
            try:
                data = json.loads(request.body)
                json_data = data.get('json')
                if not json_data:
                    return JsonResponse({"error": "JSON data must be provided in 'json' field"}, status=400)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
        else:
            # Check for file upload
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({"error": "Either file upload or JSON data must be provided"}, status=400)
            
            # Read file data as bytes
            file_data = uploaded_file.read()
        
        # Import the agent
        imported_agent = await AgentService.import_agent(
            file_data=file_data,
            json_data=json_data,
            append_copy_suffix=append_copy_suffix,
            override_existing_tools=override_existing_tools,
            strip_messages=strip_messages
        )
        
        if imported_agent:
            return JsonResponse(imported_agent, status=201)
        else:
            return JsonResponse({"error": "Failed to import agent"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# AGENT - MEMORY BLOCK VIEWS

@require_http_methods(["GET"])
async def get_agent_memory_view(request, agent_id: str, block_label: str):
    try:
        memory = await AgentService.get_memory_block(agent_id, block_label)
        
        if memory is None:
            return JsonResponse({
                "error": f"{block_label} memory block not found"
            }, status=404)
            
        return JsonResponse(memory)
    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500) 


@csrf_exempt
@require_http_methods(["POST"])
async def create_and_attach_memory_block_view(request, agent_id: str):
    try:
        data = json.loads(request.body)
        label = data.get("label")
        value = data.get("value")
        description = data.get("description")
        limit = data.get("limit")
        if not label or not value and value != "":
            return JsonResponse({"error": "label and value are required"}, status=400)
        block = await AgentService.create_and_attach_memory_block(agent_id, label, value, description, limit)
        if block is None:
            return JsonResponse({"error": "Failed to create and attach memory block"}, status=500)
        return JsonResponse(block, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 


@csrf_exempt
@require_http_methods(["PATCH"])
async def edit_memory_block_view(request, agent_id: str, block_label: str):
    try:
        data = json.loads(request.body)
        
        # Extract all possible parameters from the request
        value = data.get("value")
        limit = data.get("limit")
        name = data.get("name")
        is_template = data.get("is_template")
        preserve_on_migration = data.get("preserve_on_migration")
        label = data.get("label")
        read_only = data.get("read_only")
        description = data.get("description")
        metadata = data.get("metadata")
        
        # Check if at least one field is being updated
        if all(param is None for param in [value, limit, name, is_template, preserve_on_migration, label, read_only, description, metadata]):
            return JsonResponse({"error": "At least one field must be provided for update"}, status=400)
        
        success = await AgentService.edit_memory_block(
            agent_id=agent_id,
            block_label=block_label,
            value=value,
            limit=limit,
            name=name,
            is_template=is_template,
            preserve_on_migration=preserve_on_migration,
            label=label,
            read_only=read_only,
            description=description,
            metadata=metadata
        )
        
        if success:
            return JsonResponse({"message": "Memory block updated successfully"}, status=200)
        else:
            return JsonResponse({"error": "Failed to update memory block"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 


@csrf_exempt
@require_http_methods(["PATCH"])
async def attach_memory_block_view(request, agent_id: str, block_id: str):
    try:
        updated_agent = await AgentService.attach_memory_block_to_agent(agent_id, block_id)
        
        if updated_agent:
            return JsonResponse(updated_agent, status=200)
        else:
            return JsonResponse({"error": "Failed to attach memory block to agent"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PATCH"])
async def detach_memory_block_view(request, agent_id: str, block_id: str):
    try:
        updated_agent = await AgentService.detach_memory_block_from_agent(agent_id, block_id)
        
        if updated_agent:
            return JsonResponse(updated_agent, status=200)
        else:
            return JsonResponse({"error": "Failed to detach memory block from agent"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 


# AGENT - MESSAGE VIEWS

@csrf_exempt
@require_http_methods(["POST"])
async def send_message_stream_view(request, agent_id: str):
    try:
        data = json.loads(request.body)
        message = data.get("message")
        
        if not message:
            return JsonResponse({"error": "Message is required"}, status=400)

        async def event_stream():
            try:
                async for chunk in ChatService.send_message_stream(agent_id, message):
                    # Format the chunk as a server-sent event
                    yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                # Log the error and yield an error event
                print(f"Streaming error: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        response = StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
async def get_agent_messages_view(request, agent_id: str):
    try:
        # Get optional parameters from query string
        limit = request.GET.get('limit', 50)
        before_id = request.GET.get('before_id')
        
        try:
            limit = int(limit)
        except ValueError:
            limit = 50
            
        messages = await ChatService.get_agent_messages(
            agent_id=agent_id,
            limit=limit,
            before_id=before_id
        )
        messages = [message.model_dump() for message in messages]
        return JsonResponse({"messages": messages})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 


# AGENT SOURCE VIEWS

@csrf_exempt
@require_http_methods(["PATCH"])
async def attach_source_view(request, agent_id: str, source_id: str):
    try:
        updated_agent = await AgentService.attach_source_to_agent(agent_id, source_id)
        
        if updated_agent:
            return JsonResponse(updated_agent, status=200)
        else:
            return JsonResponse({"error": "Failed to attach source to agent"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PATCH"])
async def detach_source_view(request, agent_id: str, source_id: str):
    try:
        updated_agent = await AgentService.detach_source_from_agent(agent_id, source_id)
        
        if updated_agent:
            return JsonResponse(updated_agent, status=200)
        else:
            return JsonResponse({"error": "Failed to detach source from agent"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# AGENT TOOLS VIEWS

@require_http_methods(["GET"])
async def list_agent_tools_view(request, agent_id: str):
    """Get tools from an existing agent"""
    try:
        tools = await AgentService.list_agent_tools(agent_id)
        return JsonResponse({"tools": tools})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PATCH"])
async def attach_tool_to_agent_view(request, agent_id: str, tool_id: str):
    """Attach a tool to an agent"""
    try:
        updated_agent = await AgentService.attach_tool_to_agent(agent_id, tool_id)
        
        if updated_agent:
            return JsonResponse(updated_agent, status=200)
        else:
            return JsonResponse({"error": "Failed to attach tool to agent"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PATCH"])
async def detach_tool_from_agent_view(request, agent_id: str, tool_id: str):
    """Detach a tool from an agent"""
    try:
        updated_agent = await AgentService.detach_tool_from_agent(agent_id, tool_id)
        
        if updated_agent:
            return JsonResponse(updated_agent, status=200)
        else:
            return JsonResponse({"error": "Failed to detach tool from agent"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 


# MEMORY BLOCK VIEWS

@require_http_methods(["GET"])
async def list_all_blocks_view(request):
    try:
        # Get the templates_only query parameter and parse it as a boolean
        templates_only_param = request.GET.get('templates_only')
        
        # Default to True if not provided, otherwise parse the string to boolean
        if templates_only_param is None:
            templates_only = True  # Default value
        else:
            templates_only = templates_only_param.lower() == 'true'
        
        blocks = await AgentService.list_all_blocks(templates_only=templates_only)
        return JsonResponse({"blocks": blocks})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 

@csrf_exempt
@require_http_methods(["POST"])
async def create_memory_block_view(request):
    try:
        data = json.loads(request.body)
        label = data.get("label")
        value = data.get("value")
        name = data.get("name")
        description = data.get("description")
        limit = data.get("limit")
        is_template = data.get("is_template")
        if not label or not value:
            return JsonResponse({"error": "label and value are required"}, status=400)
        block = await AgentService.create_memory_block(label, value, name, description, limit, is_template)
        if block is None:
            return JsonResponse({"error": "Failed to create memory block"}, status=500)
        return JsonResponse(block, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["PATCH"])
async def modify_block_view(request, block_id: str):
    try:
        data = json.loads(request.body)
        
        # Extract all possible parameters from the request
        value = data.get("value")
        limit = data.get("limit")
        name = data.get("name")
        is_template = data.get("is_template")
        preserve_on_migration = data.get("preserve_on_migration")
        label = data.get("label")
        read_only = data.get("read_only")
        description = data.get("description")
        metadata = data.get("metadata")
        
        # Check if at least one field is being updated
        if all(param is None for param in [value, limit, name, is_template, preserve_on_migration, label, read_only, description, metadata]):
            return JsonResponse({"error": "At least one field must be provided for update"}, status=400)
        
        modified_block = await AgentService.modify_block(
            block_id=block_id,
            value=value,
            limit=limit,
            name=name,
            is_template=is_template,
            preserve_on_migration=preserve_on_migration,
            label=label,
            read_only=read_only,
            description=description,
            metadata=metadata
        )
        
        if modified_block:
            return JsonResponse(modified_block, status=200)
        else:
            return JsonResponse({"error": "Failed to modify block"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 

@csrf_exempt
@require_http_methods(["DELETE"])
async def delete_memory_block_view(request, block_id: str, block_label: str):
    try:
        # Check if trying to delete protected blocks
        if block_label.lower() in ["human", "persona"]:
            return JsonResponse({
                "error": f"Cannot delete protected memory block: {block_label}"
            }, status=400)
        
        success = await AgentService.delete_memory_block(block_id, block_label)
        
        if success:
            return JsonResponse({"message": "Memory block deleted successfully"}, status=204)
        else:
            return JsonResponse({"error": "Failed to delete memory block"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 

@require_http_methods(["GET"])
async def list_agents_for_block_view(request, block_id: str):
    try:
        agents = await AgentService.list_agents_for_block(block_id)
        return JsonResponse({"agents": agents})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 
        

# SOURCE VIEWS

@csrf_exempt
@require_http_methods(["POST"])
async def create_source_view(request):
    try:
        data = json.loads(request.body)
        name = data.get("name")
        description = data.get("description")
        instructions = data.get("instructions")
        metadata = data.get("metadata")
        embedding = data.get("embedding")
        embedding_chunk_size = data.get("embedding_chunk_size")
        embedding_config = data.get("embedding_config")
        
        # Validate required fields
        if not name:
            return JsonResponse({"error": "Source name is required"}, status=400)
        
        # Convert embedding_chunk_size to int if provided
        if embedding_chunk_size is not None:
            try:
                embedding_chunk_size = int(embedding_chunk_size)
            except (ValueError, TypeError):
                return JsonResponse({"error": "embedding_chunk_size must be an integer"}, status=400)
        
        source = await AgentService.create_source(
            name=name,
            description=description,
            instructions=instructions,
            metadata=metadata,
            embedding=embedding,
            embedding_chunk_size=embedding_chunk_size,
            embedding_config=embedding_config
        )
        
        if source:
            return JsonResponse(source, status=201)
        else:
            return JsonResponse({"error": "Failed to create source"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
async def delete_source_view(request, source_id: str):
    try:
        success = await AgentService.delete_source(source_id)
        
        if success:
            return JsonResponse({"message": "Source deleted successfully"}, status=204)
        else:
            return JsonResponse({"error": "Failed to delete source"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["PATCH"])
async def modify_source_view(request, source_id: str):
    try:
        data = json.loads(request.body)
        
        # Extract all possible parameters from the request
        name = data.get("name")
        description = data.get("description")
        instructions = data.get("instructions")
        metadata = data.get("metadata")
        embedding_config = data.get("embedding_config")
        
        # Check if at least one field is being updated
        if all(param is None for param in [name, description, instructions, metadata, embedding_config]):
            return JsonResponse({"error": "At least one field must be provided for update"}, status=400)
        
        modified_source = await AgentService.modify_source(
            source_id=source_id,
            name=name,
            description=description,
            instructions=instructions,
            metadata=metadata,
            embedding_config=embedding_config
        )
        
        if modified_source:
            return JsonResponse(modified_source, status=200)
        else:
            return JsonResponse({"error": "Failed to modify source"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
async def list_sources_view(request):
    try:
        sources = await AgentService.list_sources()
        return JsonResponse({"sources": sources})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
async def get_agents_for_source_view(request, source_id: str):
    try:
        agents = await AgentService.get_agents_for_source(source_id)
        return JsonResponse({"agent_ids": agents})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
async def list_source_files_view(request, source_id: str):
    try:
        # Get query parameters with defaults
        limit = request.GET.get('limit', '1000')
        after = request.GET.get('after')
        include_content = request.GET.get('include_content', 'false').lower() == 'true'
        
        # Convert limit to int
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = 1000
        
        files = await AgentService.list_source_files(
            source_id=source_id,
            limit=limit,
            after=after,
            include_content=include_content
        )
        return JsonResponse({"files": files})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
async def delete_source_file_view(request, source_id: str, file_id: str):
    try:
        success = await AgentService.delete_source_file(source_id, file_id)
        
        if success:
            return JsonResponse({"message": "File deleted successfully"}, status=204)
        else:
            return JsonResponse({"error": "Failed to delete file"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
async def upload_file_to_source_view(request, source_id: str):
    try:
        # Get query parameter for duplicate handling, default to "error"
        duplicate_handling = request.GET.get('duplicate_handling', 'error')
        
        # Check for file upload
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({"error": "File upload is required"}, status=400)
        
        # Upload the file - pass the uploaded file object directly
        uploaded_file_data = await AgentService.upload_file_to_source(
            source_id=source_id,
            uploaded_file=uploaded_file,
            duplicate_handling=duplicate_handling
        )
        
        if uploaded_file_data:
            return JsonResponse(uploaded_file_data, status=201)
        else:
            return JsonResponse({"error": "Failed to upload file"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# TRANSCRIPTION VIEWS

@csrf_exempt
async def transcribe_stream_view(request):
    """Handle streaming audio transcription"""
    if request.method == "POST":
        # Get the audio chunk from the request
        audio_chunk = request.FILES.get('audio')
        if not audio_chunk:
            return JsonResponse({"error": "No audio data"}, status=400)
            
        transcription_service = TranscriptionService()
        
        # Validate audio format
        if not transcription_service.validate_audio_format(audio_chunk.name):
            return JsonResponse(
                {"error": f"Unsupported audio format. Supported formats: {', '.join(TranscriptionService.ALLOWED_FORMATS)}"},
                status=400
            )

        async def event_stream():
            try:
                # Process the audio chunk
                transcribed_text = await transcription_service.transcribe_chunk(audio_chunk)
                
                # Send the transcribed text
                if transcribed_text:
                    yield f"data: {json.dumps({'text': transcribed_text})}\n\n"
                else:
                    yield f"data: {json.dumps({'text': ''})}\n\n"
                    
            except ValidationError as e:
                yield f"event: error\ndata: {str(e)}\n\n"
            except Exception as e:
                yield f"event: error\ndata: {str(e)}\n\n"

        return StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'  # Important for nginx
            }
        )
    
    return JsonResponse({"error": "Method not allowed"}, status=405)


# TOOLS VIEWS

@require_http_methods(["GET"])
async def list_all_tools_view(request):
    """List all tools available to agents"""
    try:
        # Get optional query parameters
        after = request.GET.get('after')
        limit = request.GET.get('limit')
        name = request.GET.get('name')
        
        # Convert limit to int if provided
        if limit:
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                return JsonResponse({"error": "limit must be an integer"}, status=400)
        
        tools = await AgentService.list_all_tools(after=after, limit=limit, name=name)
        return JsonResponse({"tools": tools})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
async def list_composio_apps_view(request):
    """List all Composio apps available"""
    try:
        apps = await AgentService.list_composio_apps()
        return JsonResponse({"apps": apps})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
async def list_composio_actions_by_app_view(request, app_name: str):
    """List all Composio actions for a specific app"""
    try:
        actions = await AgentService.list_composio_actions_by_app(app_name)
        return JsonResponse({"actions": actions})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# MCP SERVERS VIEWS

@require_http_methods(["GET"])
async def list_mcp_servers_view(request):
    """Get a list of all configured MCP servers"""
    try:
        servers = await AgentService.list_mcp_servers()
        return JsonResponse({"servers": servers})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
async def add_mcp_server_view(request):
    """Add a new MCP server to the Letta MCP server config"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields based on server type
        if not data:
            return JsonResponse({"error": "Server configuration is required"}, status=400)
        
        server_configs = await AgentService.add_mcp_server(data)
        
        if server_configs:
            return JsonResponse({"servers": server_configs}, status=200)
        else:
            return JsonResponse({"error": "Failed to add MCP server"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
async def list_mcp_tools_by_server_view(request, mcp_server_name: str):
    """Get a list of all tools for a specific MCP server"""
    try:
        tools = await AgentService.list_mcp_tools_by_server(mcp_server_name)
        return JsonResponse({"tools": tools})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
async def delete_mcp_server_view(request, server_name: str):
    """Delete a MCP server from the config"""
    try:
        success = await AgentService.delete_mcp_server(server_name)
        
        if success:
            return JsonResponse({"message": "MCP server deleted successfully"}, status=204)
        else:
            return JsonResponse({"error": "Failed to delete MCP server"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PATCH"])
async def update_mcp_server_view(request, server_name: str):
    """Update a MCP server configuration"""
    try:
        data = json.loads(request.body)
        
        if not data:
            return JsonResponse({"error": "Server configuration is required"}, status=400)
        
        updated_server = await AgentService.update_mcp_server(server_name, data)
        
        if updated_server:
            return JsonResponse(updated_server, status=200)
        else:
            return JsonResponse({"error": "Failed to update MCP server"}, status=500)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)





