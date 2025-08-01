from typing import Optional, Any
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import os
import asyncio
import httpx
import logging
from subprocess import Popen
from contextlib import AsyncExitStack
from pydantic import BaseModel

from ..config import global_config as gconfig
from ..orchestration.agents import config as agent_config


# --------------------------------------------------------------------------------------------
# Config -------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


TOOL_NAME_ORIGIN_SEPARATOR = '09090'
MASTER_TOOL_DESCRIPTION_HEADER = (
    'Automatically interface with other MCP servers for the following tools. Be sure to include as much detail as '
    'possible, so other AI agents can make the best decision as to what MCP server best fits your request. The tools '
    'are as follows:'
)
MASTER_DISPATCHER_SYSTEM_HEADER = (
    "You are a tool dispatcher agent who decides which tools to dispatch to based on the user's input. Depending on "
    "your answer, question will be routed to the right tools, so your task is crucial."
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# --------------------------------------------------------------------------------------------
# Sub-Server Class ---------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


class SubServer(BaseModel):
    url: str
    identifier: str
    headers: dict | None = None

    def __init__(self, /, **data: Any):
        super().__init__(**data)


# --------------------------------------------------------------------------------------------
# Master Server Client Class -----------------------------------------------------------------
# --------------------------------------------------------------------------------------------


class MasterServerClient:
    def __init__(self, app):
        # All streamable-http sessions by server_filename
        self.sessions = {}

        # All streamable-http streams by server_filename
        self._streams_contexts = {}

        # All streamable-http contexts by server_filename
        self._session_contexts = {}

        # Available tools from each server
        self.available_tools = {}

        # self.available_tools,  disregarding what server each tool is served from
        self.available_tools_flattened = []

        # Popens used to start local sub servers automatically
        self._sub_server_popens = {}

        # FastMCP app
        self._app = app

        # Exit stack for clients and sessions
        self._exit_stack = AsyncExitStack()

    async def check_if_server_running(self, server: SubServer):
        try:
            # Send request to see if the server is already running
            async with httpx.AsyncClient(timeout=30.0) as client:
                logging.info(f"HTTP GET attempt to {server.url}")

                response = await client.get(server.url)
                response.raise_for_status()

                # Exit if already running
                return True

        except httpx.HTTPStatusError:
            # Exit if sent a redirect error (standard behavior)
            return True

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            logging.warning(f"HTTP request attempt failed: {type(e).__name__}: {e}")

            # Exit if gconfig.autostart_abspath is None
            if gconfig.autostart_abspath is None:
                logging.info(f"No autostart path provided.")
                return False

            # Exit if the server_path is not absolute
            server_dir = str(os.path.join(gconfig.autostart_abspath))
            os.chdir(server_dir)
            if not os.path.isabs(server_dir):
                logging.info(f"{server_dir} is not an absolute path.")
                return False

            # Exit if the server is not present in the folder
            server_path = os.path.normpath(os.path.join(server_dir, f'{server.identifier}.py'))
            if not os.path.exists(server_path):
                logging.info(f"Unable to find server {server.identifier} in {server_path}.")
                return False

            # Run start command to start the server
            logging.info(f"Sending start command for {server.identifier}...")
            start_popen = Popen(['python', f'{server.identifier}.py'])
            self._sub_server_popens[server.identifier] = start_popen

            # Wait for the server to start, abort after 10 seconds
            attempt_count = 1
            async with httpx.AsyncClient(timeout=10.0) as client:
                while attempt_count <= 20:
                    try:
                        logging.debug(f"HTTP GET attempt to {server.url}")

                        response = await client.get(server.url)
                        response.raise_for_status()

                        # Exit if running
                        return True

                    except (httpx.TimeoutException, httpx.ConnectError) as e:
                        # Try again in 0.5 seconds if the request failed
                        logging.warning(f"HTTP request attempt {attempt_count} failed: {type(e).__name__}: {e}")
                        logging.info(f"Waiting 0.5 seconds...")
                        attempt_count += 1
                        await asyncio.sleep(0.5)

                    except httpx.HTTPStatusError:
                        # Exit if sent a redirect error (normal behavior)
                        return True

                    except Exception as e:
                        # Abort if an unusual error is caught
                        logging.error(f"Unexpected error in HTTP request: {e}")
                        return False

        except Exception as e:
            # Abort if an unusual error is caught
            logging.error(f"Unexpected error in HTTP request: {e}")
            return False

    async def connect_to_server(self, server: SubServer):
        if server.headers is None:
            server.headers = {}

        # Exit if the server_filename is a duplicate
        if server.identifier in self.sessions:
            logging.warning(f"Connection to {server.identifier} aborted as it mirrors an existing server_filename.")
            return

        # Exit if the server is not running despite attempts to start it
        if not await self.check_if_server_running(server):
            logging.error(f"Failed to connect to server {server.identifier} at {server.url}.")
            return

        # Initialize client and session
        client = await self._exit_stack.enter_async_context(streamablehttp_client(url=server.url, headers=server.headers))
        self._streams_contexts[server.identifier] = client
        read_stream, write_stream, _ = client

        session = await self._exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        self._session_contexts[server.identifier] = session
        self.sessions[server.identifier] = session

        await self.sessions[server.identifier].initialize()

        # Save the sub server's available tools
        await self.get_available_tools(server.identifier)

        logging.info(f"Connected to server {server.identifier} at {server.url}.")

    async def get_available_tools(self, server_filename: str):
        """Get available tools from the server"""
        try:
            # Fetch tools
            logging.info(f"Fetching available server tools from {server_filename}...")
            response = await self.sessions[server_filename].list_tools()
            logging.info(f"Connected to MCP server {server_filename} with tools {[tool.name for tool in response.tools]}.")

            # Format tools for OpenAI
            available_tools = [
                {
                    "type": 'function',
                    "function": {
                        "name": f"{tool.name}{TOOL_NAME_ORIGIN_SEPARATOR}{server_filename}",
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                    "strict": True,
                }
                for tool in response.tools
            ]

            # Save tools
            self.available_tools[server_filename] = available_tools
            self.available_tools_flattened.extend(available_tools)

            # Compile tool descriptions into the master server tool description
            self.compile_tool_descriptions()

        except Exception as e:
            logging.error(f'Tool fetch for server {server_filename} failed: {e}')

            # Blank list failsafe in case the tool fetch fails
            self.available_tools[server_filename] = []

    def compile_tool_descriptions(self):
        logging.info("Compiling all available tool descriptions...")

        # Generate description based on sub mcp server tool descriptions
        tool_description = MASTER_TOOL_DESCRIPTION_HEADER
        dispatcher_system_message = f'{MASTER_DISPATCHER_SYSTEM_HEADER}\nThere are {len(self.available_tools_flattened)} possible tools to use:'

        for server in self.available_tools:
            for tool in self.available_tools[server]:
                tool_description += f'\n{tool['function']['description']}'
                dispatcher_system_message += f'\n - {tool['function']['name']}: {tool['function']['description']}'

        # Save description directly to tool
        logging.info(f"Compiled description:\n{tool_description}")
        self._app._tool_manager._tools.get('access_sub_mcp').description = tool_description

        # Save dispatcher node system message to orchestration
        dispatcher_system_message += "Always call at least one tool. Do not attempt to generate your own response to the user's query."
        agent_config.dispatcher_system_message = dispatcher_system_message

    async def call_tool(self, tool_name: str, tool_args: Optional[dict]):
        tool_name, server_filename = tool_name.split(TOOL_NAME_ORIGIN_SEPARATOR)
        logging.info(f"Calling tool {tool_name} from {server_filename} with args {tool_args}...")

        try:
            # Call tool
            result = await self.sessions[server_filename].call_tool(tool_name, tool_args)
            return result
        except Exception:
            # Remove tool from server tool list
            if tool_name in self.available_tools[server_filename]:
                self.available_tools[server_filename].remove(tool_name)

            logging.error(f"Tool {tool_name} from {server_filename} is currently unavailable:")

    async def server_loop(self):
        while True:
            try:
                await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"\nServer loop error: {str(e)}")

    async def cleanup(self):
        """Properly clean up the sessions and streams"""
        if self._sub_server_popens:
            for popen_id in self._sub_server_popens:
                self._sub_server_popens[popen_id].terminate()

        await self._exit_stack.aclose()
