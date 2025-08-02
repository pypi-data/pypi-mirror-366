import os
import tempfile
import json

from .letta_client import get_letta_client
from typing import Optional, Dict, Any, List
from letta_client import CreateBlock

class AgentService:

    # AGENTS

    @staticmethod
    async def export_agent(agent_id: str) -> Optional[str]:
        """
        Export an agent as serialized JSON
        
        Args:
            agent_id: The ID of the agent to export
        
        Returns:
            The serialized JSON string of the agent, or None if failed
        """
        letta = get_letta_client()
        
        try:
            response = await letta.agents.export_file(agent_id)
            return response if response else None
            
        except Exception as e:
            print(f"Error exporting agent: {str(e)}")
            return None

    @staticmethod
    async def import_agent(file_data: bytes = None, json_data: Dict[str, Any] = None, 
                          append_copy_suffix: bool = True, override_existing_tools: bool = True,
                          strip_messages: bool = True) -> Optional[Dict[str, Any]]:
        """
        Import an agent from file data or JSON data
        
        Args:
            file_data: Raw file data (bytes) for multipart form
            json_data: JSON data representing the agent (will be converted to file data)
            append_copy_suffix: Append "_copy" to agent name (default: True)
            override_existing_tools: Override existing tools (default: True)
            strip_messages: Strip all messages from agent (default: True)
        
        Returns:
            The imported agent data as a dict, or None if failed
        """
        letta = get_letta_client()
        
        try:
            print(f"Importing agent from file_data or json_data")
            
            # If JSON data is provided, convert it to file data
            if json_data:
                import tempfile
                import json
                # Create a temporary .af file
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False)
                json.dump(json_data, temp_file, indent=2)
                temp_file.close()
                
                # Read the file data
                with open(temp_file.name, 'rb') as f:
                    file_data = f.read()
                
                # Clean up temp file
                os.unlink(temp_file.name)
            
            if not file_data:
                raise ValueError("Either file_data or json_data must be provided")
            
            # Build parameters dict for multipart form
            params = {
                "file": file_data,
                "append_copy_suffix": append_copy_suffix,
                "override_existing_tools": override_existing_tools,
                "strip_messages": strip_messages
            }
            
            # Import the agent
            response = await letta.agents.import_file(**params)
            
            return response.model_dump() if response else None
            
        except Exception as e:
            print(f"Error importing agent: {str(e)}")
            return None


    @staticmethod
    async def create_agent(name: str, agent_definition: dict, user_full_name: str, user_id: str) -> str:
        """
        Central method to create agents through Letta
        Returns the agent ID
        """
        letta = get_letta_client()
        
        # Get or create user identity first
        identity_id = await AgentService.get_or_create_user_identity(user_id, user_full_name)
        if not identity_id:
            raise Exception(f"Failed to create or retrieve identity for user: {user_id}")
        
        # Determine model with fallback logic
        model = None
        if agent_definition and "DEFAULT_LLM" in agent_definition:
            model = agent_definition["DEFAULT_LLM"]
        elif os.getenv("DEFAULT_AGENT_LLM"):
            model = os.getenv("DEFAULT_AGENT_LLM")
        else:
            model = "openai/gpt-4o-mini"  # Default model
        
        # Determine embedding with fallback logic
        embedding = None
        if agent_definition and "DEFAULT_EMBEDDING" in agent_definition:
            embedding = agent_definition["DEFAULT_EMBEDDING"]
        elif os.getenv("DEFAULT_AGENT_EMBEDDING_LLM"):
            embedding = os.getenv("DEFAULT_AGENT_EMBEDDING_LLM")
        else:
            embedding = "openai/text-embedding-3-small"  # Default embedding
        
        # Create the agent with type-specific metadata
        memory_blocks = [
            CreateBlock(
                value=f"Name: {user_full_name}",
                label="human"
            ),
            CreateBlock(
                value="",
                label="persona"
            )
        ]
        
        # Add additional memory blocks if they exist in agent_definition
        if agent_definition and "DEFAULT_MEMORY_BLOCKS" in agent_definition:
            memory_blocks.extend(agent_definition["DEFAULT_MEMORY_BLOCKS"])
        
        response = await letta.agents.create(
            name=name,
            memory_blocks=memory_blocks,
            identity_ids=[identity_id],  # Use the Letta identity ID
            project_id=os.getenv("LETTA_PROJECT_ID"),
            model=model,
            embedding=embedding,
            tags=[user_id]
        )
        
        return response.id


    @staticmethod
    async def update_agent(agent_id: str, name: str = None, system_prompt: str = None, description: str = None, 
                          model: str = None, embedding: str = None) -> Optional[Dict[str, Any]]:
        """
        Update an existing agent with limited fields
        
        Args:
            agent_id: The ID of the agent to update
            name: The new name of the agent (optional)
            system_prompt: The new system prompt of the agent (optional)
            description: The new description of the agent (optional)
            model: The new LLM model (optional)
            embedding: The new embedding model (optional)
        
        Returns:
            The updated agent data as a dict, or None if failed
        """
        letta = get_letta_client()
        
        try:
            # Build the parameters dict, only including non-None values
            params = {
                "agent_id": agent_id
            }
            
            if name is not None:
                params["name"] = name
            if system_prompt is not None:
                params["system"] = system_prompt
            if description is not None:
                params["description"] = description
            if model is not None:
                params["model"] = model
            if embedding is not None:
                params["embedding"] = embedding
            
            response = await letta.agents.modify(**params)
            return response.model_dump() if response else None
            
        except Exception as e:
            print(f"Error updating agent: {str(e)}")
            return None
    

    @staticmethod
    async def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a Letta agent by its id.
        Args:
            agent_id: The ID of the agent to retrieve.
        Returns:
            The agent data as a dict, or None if not found or error.
        """
        letta = get_letta_client()
        try:
            response = await letta.agents.retrieve(agent_id)
            return response.model_dump() if response else None
        except Exception as e:
            print(f"Error retrieving agent: {str(e)}")
            return None


    @staticmethod
    async def delete_agent(agent_id: str) -> None:
        letta = get_letta_client()
        await letta.agents.delete(agent_id)


    # AGENT - MEMORY BLOCKS
    
    @staticmethod
    async def get_memory_block(agent_id: str, block_label: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific memory block from an agent
        
        Args:
            agent_id: The ID of the agent
            block_label: The label of the memory block to retrieve
        
        Returns:
            The memory block content or None if not found
        """
        letta = get_letta_client()
        
        try:
            response = await letta.agents.blocks.retrieve(
                agent_id=agent_id,
                block_label=block_label
            )
            
            return response.model_dump() if response else None
            
        except Exception as e:
            print(f"Error retrieving memory block: {str(e)}")
            return None


    @staticmethod
    async def create_and_attach_memory_block(agent_id: str, label: str, value: str, description: str = None, limit: int = None) -> Optional[Dict[str, Any]]:
        """
        Create a memory block and attach it to an agent.
        Args:
            agent_id: The agent to attach the block to
            label: The label for the block (required)
            value: The value/content for the block (required)
            description: Optional description for the block
            limit: Optional character limit for the block
        Returns:
            The attached block as a dict, or None if error.
        """
        letta = get_letta_client()
        try:
            # Create the block
            block = await letta.blocks.create(
                label=label,
                value=value,
                description=description,
                limit=limit
            )
            if not block or not hasattr(block, 'id'):
                return None
            # Attach the block to the agent
            attached = await letta.agents.blocks.attach(
                agent_id=agent_id,
                block_id=block.id,
            )
            return attached.model_dump() if attached else None
        except Exception as e:
            print(f"Error creating and attaching memory block: {str(e)}")
            return None

    @staticmethod
    async def attach_memory_block_to_agent(agent_id: str, block_id: str) -> Optional[Dict[str, Any]]:
        """
        Attach an existing memory block to an agent
        
        Args:
            agent_id: The ID of the agent
            block_id: The ID of the memory block to attach
        
        Returns:
            The updated agent data as a dict, or None if failed
        """
        letta = get_letta_client()
        
        try:
            response = await letta.agents.blocks.attach(
                agent_id=agent_id,
                block_id=block_id
            )
            return response.model_dump() if response else None
            
        except Exception as e:
            print(f"Error attaching memory block to agent: {str(e)}")
            return None

    @staticmethod
    async def detach_memory_block_from_agent(agent_id: str, block_id: str) -> Optional[Dict[str, Any]]:
        """
        Detach a memory block from an agent
        
        Args:
            agent_id: The ID of the agent
            block_id: The ID of the memory block to detach
        
        Returns:
            The updated agent data as a dict, or None if failed
        """
        letta = get_letta_client()
        
        try:
            response = await letta.agents.blocks.detach(
                agent_id=agent_id,
                block_id=block_id
            )
            return response.model_dump() if response else None
            
        except Exception as e:
            print(f"Error detaching memory block from agent: {str(e)}")
            return None


    @staticmethod
    async def edit_memory_block(agent_id: str, block_label: str, value: str = None, limit: int = None, 
                                name: str = None, is_template: bool = None, preserve_on_migration: bool = None,
                                label: str = None, read_only: bool = None, description: str = None,
                                metadata: Dict[str, Any] = None) -> bool:
        """
        Edit a memory block by name using the Letta modify endpoint
        
        Args:
            agent_id: The ID of the agent
            block_label: The label of the memory block to edit
            value: The new value/content for the block
            limit: Character limit of the block
            name: Name of the block if it is a template
            is_template: Whether the block is a template
            preserve_on_migration: Preserve the block on template migration
            label: Label of the block in the context window
            read_only: Whether the agent has read-only access to the block
            description: Description of the block
            metadata: Metadata of the block
        
        Returns:
            True if successful, False otherwise
        """
        letta = get_letta_client()
        
        try:
            # Build the parameters dict, only including non-None values
            params = {
                "agent_id": agent_id,
                "block_label": block_label
            }
            
            if value is not None:
                params["value"] = value
            if limit is not None:
                params["limit"] = limit
            if name is not None:
                params["name"] = name
            if is_template is not None:
                params["is_template"] = is_template
            if preserve_on_migration is not None:
                params["preserve_on_migration"] = preserve_on_migration
            if label is not None:
                params["label"] = label
            if read_only is not None:
                params["read_only"] = read_only
            if description is not None:
                params["description"] = description
            if metadata is not None:
                params["metadata"] = metadata
            
            await letta.agents.blocks.modify(**params)
            return True
            
        except Exception as e:
            print(f"Error editing memory block: {str(e)}")
            return False


    @staticmethod
    async def clear_agent_memory_contents(agent_id: str) -> bool:
        """
        Clear all memory contents of an agent
        
        Args:
            agent_id: The ID of the agent
        
        Returns:
            True if successful, False otherwise
        """
        letta = get_letta_client()
        
        try:
            # Get all memory blocks first
            blocks_response = await letta.agents.blocks.list(agent_id)
            if not blocks_response:
                return True
                
            # Delete each memory block except protected ones
            for block in blocks_response:
                block_label = block.block_label if hasattr(block, 'block_label') else str(block)
                if block_label.lower() not in ["human", "persona"]:
                    try:
                        await letta.agents.blocks.delete(
                            agent_id=agent_id,
                            block_label=block_label
                        )
                    except Exception as e:
                        print(f"Error deleting memory block {block_label}: {str(e)}")
                        continue
                        
            return True
            
        except Exception as e:
            print(f"Error clearing agent memory contents: {str(e)}")
            return False

    # AGENT - MESSAGES

    @staticmethod
    async def clear_agent_conversation_history(agent_id: str) -> bool:
        """
        Clear conversation history of an agent
        
        Args:
            agent_id: The ID of the agent
        
        Returns:
            True if successful, False otherwise
        """
        letta = get_letta_client()
        
        try:
            await letta.agents.messages.delete(agent_id)
            return True
            
        except Exception as e:
            print(f"Error clearing agent conversation history: {str(e)}")
            return False

    # AGENT - SOURCES

    @staticmethod
    async def attach_source_to_agent(agent_id: str, source_id: str) -> Optional[Dict[str, Any]]:
        """
        Attach a source to an agent
        
        Args:
            agent_id: The ID of the agent
            source_id: The ID of the source to attach
        
        Returns:
            The updated agent data as a dict, or None if failed
        """
        letta = get_letta_client()
        
        try:
            response = await letta.agents.sources.attach(
                agent_id=agent_id,
                source_id=source_id
            )
            return response.model_dump() if response else None
            
        except Exception as e:
            print(f"Error attaching source to agent: {str(e)}")
            return None

    @staticmethod
    async def detach_source_from_agent(agent_id: str, source_id: str) -> Optional[Dict[str, Any]]:
        """
        Detach a source from an agent
        
        Args:
            agent_id: The ID of the agent
            source_id: The ID of the source to detach
        
        Returns:
            The updated agent data as a dict, or None if failed
        """
        letta = get_letta_client()
        
        try:
            response = await letta.agents.sources.detach(
                agent_id=agent_id,
                source_id=source_id
            )
            return response.model_dump() if response else None
            
        except Exception as e:
            print(f"Error detaching source from agent: {str(e)}")
            return None

    # AGENT - TOOLS

    @staticmethod
    async def list_agent_tools(agent_id: str) -> List[Dict[str, Any]]:
        """
        Get tools from an existing agent
        
        Args:
            agent_id: The ID of the agent
        
        Returns:
            List of tools attached to the agent or empty list if error
        """
        letta = get_letta_client()
        
        try:
            response = await letta.agents.tools.list(agent_id=agent_id)
            return [tool.model_dump() for tool in response] if response else []
            
        except Exception as e:
            print(f"Error listing agent tools: {str(e)}")
            return []

    @staticmethod
    async def attach_tool_to_agent(agent_id: str, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Attach a tool to an agent
        
        Args:
            agent_id: The ID of the agent
            tool_id: The ID of the tool to attach
        
        Returns:
            The updated agent data as a dict, or None if failed
        """
        letta = get_letta_client()
        
        try:
            response = await letta.agents.tools.attach(
                agent_id=agent_id,
                tool_id=tool_id
            )
            return response.model_dump() if response else None
            
        except Exception as e:
            print(f"Error attaching tool to agent: {str(e)}")
            return None

    @staticmethod
    async def detach_tool_from_agent(agent_id: str, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Detach a tool from an agent
        
        Args:
            agent_id: The ID of the agent
            tool_id: The ID of the tool to detach
        
        Returns:
            The updated agent data as a dict, or None if failed
        """
        letta = get_letta_client()
        
        try:
            response = await letta.agents.tools.detach(
                agent_id=agent_id,
                tool_id=tool_id
            )
            return response.model_dump() if response else None
            
        except Exception as e:
            print(f"Error detaching tool from agent: {str(e)}")
            return None

    
    @staticmethod
    async def remove_tool_from_agent(agent_id: str, tool_id: str) -> bool:
        """
        Remove a tool from an agent
        
        Args:
            agent_id: The ID of the agent
            tool_id: The ID of the tool to remove
        
        Returns:
            True if successful, False otherwise
        """
        letta = get_letta_client()
        
        try:
            await letta.agents.tools.detach(
                agent_id=agent_id,
                tool_id=tool_id
            )
            return True
            
        except Exception as e:
            print(f"Error removing tool from agent: {str(e)}")
            return False


    # MEMORY BLOCKS

    @staticmethod
    async def create_memory_block(label: str, value: str, name: str = None, description: str = None, limit: int = None, is_template: bool = None) -> Optional[Dict[str, Any]]:
        """
        Create a memory block in Letta.
        Args:
            label: The label for the block (required)
            value: The value/content for the block (required)
            description: Optional description for the block
            limit: Optional character limit for the block
            is_template: Optional boolean to indicate if the block is a template
        Returns:
            The created block as a dict, or None if error.
        """
        letta = get_letta_client()
        try:
            response = await letta.blocks.create(
                label=label,
                value=value,
                name=name,
                description=description,
                limit=limit,
                is_template=is_template
            )
            return response.model_dump() if response else None
        except Exception as e:
            print(f"Error creating memory block: {str(e)}")
            return None


    @staticmethod
    async def delete_memory_block(block_id: str, block_label: str) -> bool:
        """
        Delete a memory block by name unless the name is "human" or "persona"
        
        Args:
            agent_id: The ID of the agent
            block_label: The label of the memory block to delete
        
        Returns:
            True if successful, False otherwise
        """
        if block_label.lower() in ["human", "persona"]:
            print(f"Cannot delete protected memory block: {block_label}")
            return False
            
        letta = get_letta_client()
        
        try:
            await letta.blocks.delete(
                block_id=block_id
            )
            return True
            
        except Exception as e:
            print(f"Error deleting memory block: {str(e)}")
            return False


    @staticmethod
    async def modify_block(block_id: str, value: str = None, limit: int = None, 
                          name: str = None, is_template: bool = None, preserve_on_migration: bool = None,
                          label: str = None, read_only: bool = None, description: str = None,
                          metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Modify a memory block directly by block_id
        
        Args:
            block_id: The ID of the block to modify
            value: The new value/content for the block
            limit: Character limit of the block
            name: Name of the block if it is a template
            is_template: Whether the block is a template
            preserve_on_migration: Preserve the block on template migration
            label: Label of the block in the context window
            read_only: Whether the agent has read-only access to the block
            description: Description of the block
            metadata: Metadata of the block
        
        Returns:
            The modified block data as a dict, or None if failed
        """
        letta = get_letta_client()
        
        try:
            # Build the parameters dict, only including non-None values
            params = {
                "block_id": block_id
            }
            
            if value is not None:
                params["value"] = value
            if limit is not None:
                params["limit"] = limit
            if name is not None:
                params["name"] = name
            if is_template is not None:
                params["is_template"] = is_template
            if preserve_on_migration is not None:
                params["preserve_on_migration"] = preserve_on_migration
            if label is not None:
                params["label"] = label
            if read_only is not None:
                params["read_only"] = read_only
            if description is not None:
                params["description"] = description
            if metadata is not None:
                params["metadata"] = metadata
            
            response = await letta.blocks.modify(**params)
            return response.model_dump() if response else None
            
        except Exception as e:
            print(f"Error modifying block: {str(e)}")
            return None


    @staticmethod
    async def list_all_blocks(templates_only: bool = True) -> List[Dict[str, Any]]:
        """
        List all memory blocks in the system
        
        Returns:
            List of memory blocks or empty list if error
        """
        letta = get_letta_client()
        
        try:
            response = await letta.blocks.list(
                templates_only=templates_only
            )
            return [block.model_dump() for block in response] if response else []
            
        except Exception as e:
            print(f"Error listing all blocks: {str(e)}")
            return []

    @staticmethod
    async def list_agents_for_block(block_id: str) -> List[Dict[str, Any]]:
        """
        List all agents associated with a specific memory block
        
        Args:
            block_id: The ID of the memory block
        
        Returns:
            List of agents (minimal info) or empty list if error
        """
        letta = get_letta_client()
        
        try:
            # Use include_relationships=[] to omit relational properties for better performance
            response = await letta.blocks.agents.list(
                block_id=block_id,
                include_relationships=[]
            )
            return [agent.model_dump() for agent in response] if response else []
            
        except Exception as e:
            print(f"Error listing agents for block: {str(e)}")
            return []
            

    # SOURCES

    @staticmethod
    async def create_source(name: str, description: str = None, instructions: str = None, 
                           metadata: Dict[str, Any] = None, embedding: str = None,
                           embedding_chunk_size: int = None, embedding_config: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new data source in Letta
        
        Args:
            name: The name of the source (required)
            description: Optional description of the source
            instructions: Optional instructions for how to use the source
            metadata: Optional metadata associated with the source
            embedding: Optional handle for the embedding config used by the source
            embedding_chunk_size: Optional chunk size of the embedding
            embedding_config: Optional embedding configuration (legacy)
        
        Returns:
            The created source data as a dict, or None if failed
        """
        letta = get_letta_client()
        
        try:
            # Build the parameters dict, only including non-None values
            params = {
                "name": name
            }
            
            if description is not None:
                params["description"] = description
            if instructions is not None:
                params["instructions"] = instructions
            if metadata is not None:
                params["metadata"] = metadata
            if embedding is not None:
                params["embedding"] = embedding
            elif os.getenv("DEFAULT_SOURCE_EMBEDDING_LLM"):
                params["embedding"] = os.getenv("DEFAULT_SOURCE_EMBEDDING_LLM")
            else:
                params["embedding"] = "openai/text-embedding-3-small"
            # if embedding_chunk_size is not None:
            #     params["embedding_chunk_size"] = embedding_chunk_size
            # if embedding_config is not None:
            #     params["embedding_config"] = embedding_config
            
            response = await letta.sources.create(**params)
            return response.model_dump() if response else None
            
        except Exception as e:
            print(f"Error creating source: {str(e)}")
            return None

    @staticmethod
    async def delete_source(source_id: str) -> bool:
        """
        Delete a data source
        
        Args:
            source_id: The ID of the source to delete
        
        Returns:
            True if successful, False otherwise
        """
        letta = get_letta_client()
        
        try:
            await letta.sources.delete(source_id)
            return True
            
        except Exception as e:
            print(f"Error deleting source: {str(e)}")
            return False

    @staticmethod
    async def modify_source(source_id: str, name: str = None, description: str = None, 
                           instructions: str = None, metadata: Dict[str, Any] = None,
                           embedding_config: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Update the name or documentation of an existing data source
        
        Args:
            source_id: The ID of the source to modify
            name: Optional new name of the source
            description: Optional new description of the source
            instructions: Optional new instructions for how to use the source
            metadata: Optional new metadata associated with the source
            embedding_config: Optional new embedding configuration
        
        Returns:
            The modified folder data as a dict, or None if failed
        """
        letta = get_letta_client()
        
        try:
            # Build the parameters dict, only including non-None values
            params = {
                "source_id": source_id
            }
            
            if name is not None:
                params["name"] = name
            if description is not None:
                params["description"] = description
            if instructions is not None:
                params["instructions"] = instructions
            if metadata is not None:
                params["metadata"] = metadata
            if embedding_config is not None:
                params["embedding_config"] = embedding_config
            
            response = await letta.sources.modify(**params)
            return response.model_dump() if response else None
            
        except Exception as e:
            print(f"Error modifying source: {str(e)}")
            return None

    @staticmethod
    async def list_sources() -> List[Dict[str, Any]]:
        """
        List all data sources in the system
        
        Returns:
            List of sources or empty list if error
        """
        letta = get_letta_client()
        
        try:
            response = await letta.sources.list()
            return [source.model_dump() for source in response] if response else []
            
        except Exception as e:
            print(f"Error listing sources: {str(e)}")
            return []

    @staticmethod
    async def get_agents_for_source(source_id: str) -> List[str]:
        """
        Get all agents associated with a specific source
        
        Args:
            source_id: The ID of the source
        
        Returns:
            List of agent IDs or empty list if error
        """
        letta = get_letta_client()
        
        try:
            response = await letta.sources.get_agents_for_source(source_id)
            return response
            
        except Exception as e:
            print(f"Error getting agents for source: {str(e)}")
            return []

    @staticmethod
    async def list_source_files(source_id: str, limit: int = 1000, after: str = None, 
                               include_content: bool = False) -> List[Dict[str, Any]]:
        """
        List paginated files associated with a data source
        
        Args:
            source_id: The ID of the source
            limit: Number of files to return (default: 1000)
            after: Pagination cursor to fetch the next set of results
            include_content: Whether to include full file content (default: False)
        
        Returns:
            List of files or empty list if error
        """
        letta = get_letta_client()
        
        try:
            # Build the parameters dict, only including non-None values
            params = {
                "source_id": source_id,
                "limit": limit,
                "include_content": include_content
            }
            
            if after is not None:
                params["after"] = after
            
            response = await letta.sources.files.list(**params)
            return [file.model_dump() for file in response] if response else []
            
        except Exception as e:
            print(f"Error listing source files: {str(e)}")
            return []

    @staticmethod
    async def delete_source_file(source_id: str, file_id: str) -> bool:
        """
        Delete a file from a data source
        
        Args:
            source_id: The ID of the source
            file_id: The ID of the file to delete
        
        Returns:
            True if successful, False otherwise
        """
        letta = get_letta_client()
        
        try:
            await letta.sources.files.delete(
                source_id=source_id,
                file_id=file_id
            )
            return True
            
        except Exception as e:
            print(f"Error deleting source file: {str(e)}")
            return False

    @staticmethod
    async def upload_file_to_source(source_id: str, uploaded_file, duplicate_handling: str = "error") -> Optional[Dict[str, Any]]:
        """
        Upload a file to a data source
        
        Args:
            source_id: The ID of the source
            uploaded_file: Django UploadedFile object
            duplicate_handling: How to handle duplicate files (default: "error")
        
        Returns:
            The uploaded file data as a dict, or None if failed
        """
        letta = get_letta_client()
        
        try:
            # The Letta SDK expects the file to be passed directly, not as raw bytes
            # We need to pass the Django uploaded file in a format the SDK can handle
            response = await letta.sources.files.upload(
                source_id=source_id,
                file=uploaded_file,
                duplicate_handling=duplicate_handling
            )
            
            return response.model_dump() if response else None
            
        except Exception as e:
            print(f"Error uploading file to source: {str(e)}")
            return None


    # MCP SERVERS

    @staticmethod
    async def list_mcp_servers() -> List[Dict[str, Any]]:
        """
        List custom MCP servers available
        
        Returns:
            List of MCP servers or empty list if error
        """
        letta = get_letta_client()
        
        try:
            response = await letta.tools.list_mcp_servers()
            return [server.model_dump() for server in response] if response else []
            
        except Exception as e:
            print(f"Error listing MCP servers: {str(e)}")
            return []

    @staticmethod
    async def add_mcp_server(server_config: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Add a new MCP server to the Letta MCP server config
        
        Args:
            server_config: The MCP server configuration (StdioServerConfig, SSEServerConfig, or StreamableHTTPServerConfig)
        
        Returns:
            List of MCP server configurations or None if failed
        """
        letta = get_letta_client()
        
        try:
            response = await letta.tools.add_mcp_server(request=server_config)
            return [server.model_dump() for server in response] if response else None
            
        except Exception as e:
            print(f"Error adding MCP server: {str(e)}")
            return None

    @staticmethod
    async def list_mcp_tools_by_server(mcp_server_name: str) -> List[Dict[str, Any]]:
        """
        Get a list of all tools for a specific MCP server
        
        Args:
            mcp_server_name: The name of the MCP server
        
        Returns:
            List of MCP tools for the server or empty list if error
        """
        letta = get_letta_client()
        
        try:
            response = await letta.tools.list_mcp_tools_by_server(mcp_server_name=mcp_server_name)
            return [tool.model_dump() for tool in response] if response else []
            
        except Exception as e:
            print(f"Error listing MCP tools by server: {str(e)}")
            return []

    @staticmethod
    async def delete_mcp_server(server_name: str) -> bool:
        """
        Delete a MCP server from the config
        
        Args:
            server_name: The name of the MCP server to delete
        
        Returns:
            True if successful, False otherwise
        """
        letta = get_letta_client()
        
        try:
            await letta.tools.delete_mcp_server(mcp_server_name=server_name)
            return True
            
        except Exception as e:
            print(f"Error deleting MCP server: {str(e)}")
            return False

    @staticmethod
    async def update_mcp_server(server_name: str, server_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a MCP server configuration
        
        Args:
            server_name: The name of the MCP server to update
            server_config: The updated MCP server configuration
        
        Returns:
            Updated MCP server configuration or None if failed
        """
        letta = get_letta_client()
        
        try:
            response = await letta.tools.update_mcp_server(
                mcp_server_name=server_name,
                request=server_config
            )
            return response.model_dump() if response else None
            
        except Exception as e:
            print(f"Error updating MCP server: {str(e)}")
            return None


    # TOOLS

    @staticmethod
    async def list_all_tools(after: str = None, limit: int = 1000, name: str = None) -> List[Dict[str, Any]]:
        """
        List all tools
        
        Returns:
            List of tools or empty list if error
        """
        letta = get_letta_client()
        
        try:
            response = await letta.tools.list(
                after=after,
                limit=limit,
                name=name
            )
            return [tool.model_dump() for tool in response] if response else []
            
        except Exception as e:
            print(f"Error listing tools: {str(e)}")
            return []


    @staticmethod
    async def list_composio_apps() -> List[Dict[str, Any]]:
        """
        List all Composio apps available
        
        Returns:
            List of Composio apps or empty list if error
        """
        letta = get_letta_client()
        
        try:
            response = await letta.tools.list_composio_apps()
            return [app.model_dump() for app in response] if response else []
            
        except Exception as e:
            print(f"Error listing Composio apps: {str(e)}")
            return []


    @staticmethod
    async def list_composio_actions_by_app(app_name: str) -> List[Dict[str, Any]]:
        """
        List all Composio actions by app
        
        Returns:
            List of Composio actions or empty list if error
        """
        letta = get_letta_client()
        
        try:
            response = await letta.tools.list_composio_actions_by_app(
                composio_app_name=app_name,
            )
            return [action.model_dump() for action in response] if response else []
            
        except Exception as e:
            print(f"Error listing Composio actions by app: {str(e)}")
            return []


    # @staticmethod
    # async def add_composio_tool_to_agent(agent_id: str, tool_action_name: str) -> bool:
    #     """
    #     Add a Composio tool to an agent
        
    #     Args:
    #         agent_id: The ID of the agent
    #         tool_action_name: The name of the Composio tool to add
        
    #     Returns:
    #         True if successful, False otherwise
    #     """
    #     letta = get_letta_client()
        
    #     try:
    #         await letta.agents.tools.add_composio_tool(
    #             composio_action_name=tool_action_name
    #         )
    #         return True
            
    #     except Exception as e:
    #         print(f"Error adding Composio tool to agent: {str(e)}")
    #         return False


    # @staticmethod
    # async def remove_composio_tool_from_agent(agent_id: str, tool_id: str) -> bool:
    #     """
    #     Remove a Composio tool from an agent
        
    #     Args:
    #         agent_id: The ID of the agent
    #         tool_id: The ID of the Composio tool to remove
        
    #     Returns:
    #         True if successful, False otherwise
    #     """
    #     letta = get_letta_client()
        
    #     try:
    #         await letta.agents.tools.detach_composio_tool(
    #             agent_id=agent_id,
    #             tool_id=tool_id
    #         )
    #         return True
            
    #     except Exception as e:
    #         print(f"Error removing Composio tool from agent: {str(e)}")
    #         return False


    # IDENTITIES

    @staticmethod
    async def create_user_identity(user_id: str, user_full_name: str) -> Optional[str]:
        """
        Create a user identity in Letta system
        
        Args:
            user_id: The unique user ID from the calling app
            user_full_name: The user's full name
        
        Returns:
            The Letta identity ID or None if failed
        """
        letta = get_letta_client()
        
        try:
            response = await letta.identities.create(
                identifier_key=user_id,
                name=user_full_name,
                identity_type="user"
            )
            return response.id if response else None
            
        except Exception as e:
            print(f"Error creating user identity: {str(e)}")
            return None


    @staticmethod
    async def get_user_identity(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user identity by user_id
        
        Args:
            user_id: The unique user ID from the calling app
        
        Returns:
            The identity data or None if not found
        """
        letta = get_letta_client()
        
        try:
            identities = await letta.identities.list(
                identifier_key=user_id,
                identity_type="user"
            )
            
            for identity in identities:
                if hasattr(identity, 'identifier_key') and user_id in identity.identifier_key:
                    return identity.model_dump()
            
            return None
            
        except Exception as e:
            print(f"Error retrieving user identity: {str(e)}")
            return None


    @staticmethod
    async def get_or_create_user_identity(user_id: str, user_full_name: str) -> Optional[str]:
        """
        Get existing user identity or create a new one
        
        Args:
            user_id: The unique user ID from the calling app
            user_full_name: The user's full name
        
        Returns:
            The Letta identity ID or None if failed
        """
        # First try to get existing identity
        existing_identity = await AgentService.get_user_identity(user_id)
        if existing_identity:
            return existing_identity.get('id')
        
        # If not found, create new identity
        return await AgentService.create_user_identity(user_id, user_full_name)


    

