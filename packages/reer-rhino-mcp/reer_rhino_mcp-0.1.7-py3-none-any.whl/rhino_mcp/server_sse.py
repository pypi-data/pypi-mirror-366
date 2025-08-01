"""Rhino integration through the Model Context Protocol."""
from mcp.server.fastmcp import FastMCP, Context, Image
import logging
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List, Optional
from pathlib import Path
from rhino_mcp.rhino_tools import RhinoTools, get_rhino_connection
from typing import Any
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logging.info(f"Loaded environment variables from {env_path}")
except ImportError:
    logging.warning("python-dotenv not installed. Install it to use .env files: pip install python-dotenv")



# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RhinoMCPServer")

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    rhino_conn = None
    gh_conn = None
    
    try:
        logger.info("RhinoMCP server starting up")
        
        # Try to connect to Rhino script
        try:
            rhino_conn = get_rhino_connection()
            rhino_conn.connect()
            logger.info("Successfully connected to Rhino script")
        except Exception as e:
            logger.warning("Could not connect to Rhino script: {0}".format(str(e)))
        
        yield {}
    finally:
        logger.info("RhinoMCP server shut down")
        
        # Clean up connections
        if rhino_conn:
            try:
                rhino_conn.disconnect()
                logger.info("Disconnected from Rhino script")
            except Exception as e:
                logger.warning("Error disconnecting from Rhino: {0}".format(str(e)))

# Create the MCP server with lifespan support
app = FastMCP(
    "RhinoMCP",
    description="Rhino integration through the Model Context Protocol",
    lifespan=server_lifespan
)

# Initialize tool collections
rhino_tools = RhinoTools(app)

@app.prompt()
def rhino_creation_strategy() -> str:
    """Defines the preferred strategy for creating and managing objects in Rhino"""
    return """When working with Rhino through MCP, follow these guidelines:

    Especially when working with geometry, iterate with smaller steps and check the scene state from time to time.
    Act strategically with a long-term plan, think about how to organize the data and scene objects in a way that is easy to maintain and extend, by using layers and metadata (name, description),
    with the get_rhino_objects_with_metadata() function you can filter and select objects based on this metadata. You can access objects, and with the "type" attribute you can check their geometry type and
    access the geometry specific properties (such as corner points etc.) to create more complex scenes with spatial consistency. Start from sparse to detail (e.g. first the building plot, then the wall, then the window etc. - it is crucial to use metadata to be able to do that)

    1. Scene Context Awareness:
       - Always start by checking the scene using get_rhino_scene_info() for basic overview
       - Use the capture_rhino_viewport to get an image from viewport to get a quick overview of the scene
       - Use get_rhino_objects_with_metadata() for detailed object information and filtering
       - The short_id in metadata can be displayed in viewport using capture_rhino_viewport()

    2. Object Creation and Management:
       - When creating objects, ALWAYS call add_rhino_object_metadata() after creation (The add_rhino_object_metadata() function is provided in the code context)   
       - Use meaningful names for objects to help with you with later identification, organize the scenes with layers (but not too many layers)
       - Think about grouping objects (e.g. two planes that form a window)
    
    3. Always check the bbox for each item so that (it's stored as list of points in the metadata under the key "bbox"):
            - Ensure that all objects that should not be clipping are not clipping.
            - Items have the right spatial relationship.

    4. Code Execution:
       - This is Rhino 7 with IronPython 2.7 - no f-strings or modern Python features etc
       - Please use the Irhono python 2.7 library to access rhino functions
       - DONT FORGET NO f-strings! No f-strings, No f-strings!
       - Prefer automated solutions over user interaction, unless its requested or it makes sense or you struggle with errors
       - You can use rhino command syntax to ask the user questions e.g. "should i do "A" or "B"" where A,B are clickable options

    5. Best Practices:
       - Keep objects organized in appropriate layers
       - Use meaningful names and descriptions
       - Use viewport captures to verify visual results
    """

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

# Replace the main function
def main():
    """Run the MCP server with SSE transport"""
    mcp_server = app._mcp_server

    # Define default settings
    HOST = "127.0.0.1"  
    PORT = 8080      

    # Create and run the Starlette app
    starlette_app = create_starlette_app(mcp_server, debug=True)
    logger.info(f"Starting RhinoMCP server on {HOST}:{PORT}")
    uvicorn.run(starlette_app, host=HOST, port=PORT)

if __name__ == "__main__":
    main()