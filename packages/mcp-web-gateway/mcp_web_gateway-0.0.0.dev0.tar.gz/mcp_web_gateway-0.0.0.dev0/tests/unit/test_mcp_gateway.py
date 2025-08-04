"""Comprehensive tests for the MCP Web Gateway."""

from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from fastmcp.client import Client

from mcp_web_gateway import McpWebGateway


class TestMcpWebGateway:
    """Test MCP Web Gateway functionality."""

    @pytest.fixture
    async def server_and_client(self, petstore_openapi_spec, mock_http_client):
        """Create server and client for testing."""
        server = McpWebGateway(
            petstore_openapi_spec, mock_http_client, name="Pet Store API"
        )
        async with Client(server) as mcp_client:
            yield server, mcp_client

    async def test_resources_created_with_http_uris(self, petstore_openapi_spec):
        """Test that resources are created with HTTP URIs including method prefix."""
        client = httpx.AsyncClient(base_url="https://petstore.example.com/api")
        server = McpWebGateway(petstore_openapi_spec, client)

        # Check that resources were created
        resources = server._resource_manager._resources
        templates = server._resource_manager._templates

        # Should have 2 resources (GET /pets, POST /pets)
        assert len(resources) == 2

        # Should have 3 templates (GET /pets/{petId}, PUT /pets/{petId}, DELETE /pets/{petId})
        assert len(templates) == 3

        # Check resource URIs have method prefix
        assert "https+get://petstore.example.com/api/pets" in resources
        assert "https+post://petstore.example.com/api/pets" in resources

        # Check template URIs have method prefix
        assert "https+get://petstore.example.com/api/pets/{petId}" in templates
        assert "https+put://petstore.example.com/api/pets/{petId}" in templates
        assert "https+delete://petstore.example.com/api/pets/{petId}" in templates

    async def test_resources_have_annotations(self, petstore_openapi_spec):
        """Test that resources have proper annotations with HTTP metadata."""
        client = httpx.AsyncClient(base_url="https://petstore.example.com/api")
        server = McpWebGateway(petstore_openapi_spec, client)

        # Get a GET resource
        get_pets_resource = server._resource_manager._resources[
            "https+get://petstore.example.com/api/pets"
        ]

        # Check annotations
        assert get_pets_resource.annotations is not None
        assert get_pets_resource.annotations.httpMethod == "GET"
        assert get_pets_resource.annotations.httpPath == "/pets"
        assert get_pets_resource.annotations.operationId == "list_pets"

        # Check POST resource
        post_pets_resource = server._resource_manager._resources[
            "https+post://petstore.example.com/api/pets"
        ]
        assert post_pets_resource.annotations.httpMethod == "POST"
        assert post_pets_resource.annotations.operationId == "create_pet"
        assert hasattr(post_pets_resource.annotations, "requestBody")
        assert hasattr(post_pets_resource.annotations, "responses")

    async def test_resource_read_raises_error(self, petstore_openapi_spec):
        """Test that reading a resource raises NotImplementedError."""
        client = httpx.AsyncClient(base_url="https://petstore.example.com/api")
        server = McpWebGateway(petstore_openapi_spec, client)

        resource = server._resource_manager._resources[
            "https+get://petstore.example.com/api/pets"
        ]

        with pytest.raises(NotImplementedError) as exc_info:
            await resource.read()

        assert "GET endpoint" in str(exc_info.value)
        assert "use the GET tool" in str(exc_info.value)

    async def test_only_rest_tools_created(self, petstore_openapi_spec):
        """Test that only REST tools are created, no operation-specific tools."""
        client = httpx.AsyncClient(base_url="https://petstore.example.com/api")
        server = McpWebGateway(petstore_openapi_spec, client)

        tools = await server.get_tools()
        tool_names = list(tools.keys())

        # Should only have the 5 REST tools
        assert len(tool_names) == 5
        assert set(tool_names) == {"GET", "POST", "PUT", "PATCH", "DELETE"}

        # Should not have operation-specific tools
        assert "list_pets" not in tool_names
        assert "create_pet" not in tool_names
        assert "get_pet" not in tool_names
        assert "update_pet" not in tool_names
        assert "delete_pet" not in tool_names

    async def test_get_tool_execution(self, petstore_openapi_spec):
        """Test executing a GET request through the GET tool."""
        # Create a mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Fluffy", "species": "cat"},
            {"id": 2, "name": "Buddy", "species": "dog"},
        ]
        mock_response.text = '[{"id": 1, "name": "Fluffy", "species": "cat"}, {"id": 2, "name": "Buddy", "species": "dog"}]'
        mock_response.raise_for_status = Mock()

        # Create mock client
        mock_client = AsyncMock()
        mock_client.base_url = "https://petstore.example.com/api"
        mock_client.request = AsyncMock(return_value=mock_response)

        server = McpWebGateway(petstore_openapi_spec, mock_client)

        # Use in-memory client to call the tool
        async with Client(server) as client:
            result = await client.call_tool(
                "GET", {"url": "https+get://petstore.example.com/api/pets"}
            )

        # Check the request was made correctly
        mock_client.request.assert_called_once_with(
            method="GET",
            url="https://petstore.example.com/api/pets",
        )

        # Check the result (arrays are wrapped in a dict)
        assert result.structured_content == {
            "result": [
                {"id": 1, "name": "Fluffy", "species": "cat"},
                {"id": 2, "name": "Buddy", "species": "dog"},
            ]
        }

    async def test_post_tool_execution(self, petstore_openapi_spec):
        """Test executing a POST request through the POST tool."""
        # Create a mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 4,
            "name": "Max",
            "species": "dog",
            "breed": "Labrador",
        }
        mock_response.raise_for_status = Mock()

        # Create mock client
        mock_client = AsyncMock()
        mock_client.base_url = "https://petstore.example.com/api"
        mock_client.request = AsyncMock(return_value=mock_response)

        server = McpWebGateway(petstore_openapi_spec, mock_client)

        # Use in-memory client to call the tool
        async with Client(server) as client:
            result = await client.call_tool(
                "POST",
                {
                    "url": "https+post://petstore.example.com/api/pets",
                    "body": {"name": "Max", "species": "dog", "breed": "Labrador"},
                },
            )

        # Check the request was made correctly
        mock_client.request.assert_called_once_with(
            method="POST",
            url="https://petstore.example.com/api/pets",
            json={"name": "Max", "species": "dog", "breed": "Labrador"},
        )

        # Check the result
        assert result.structured_content["id"] == 4
        assert result.structured_content["name"] == "Max"

    async def test_method_mismatch_error(self, petstore_openapi_spec):
        """Test that using wrong tool for a resource raises error."""
        mock_client = AsyncMock()
        mock_client.base_url = "https://petstore.example.com/api"

        server = McpWebGateway(petstore_openapi_spec, mock_client)

        # Try to use POST tool on a GET resource
        async with Client(server) as client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "POST", {"url": "https+get://petstore.example.com/api/pets"}
                )

            assert "Method mismatch" in str(exc_info.value)

    async def test_query_parameters(self, petstore_openapi_spec):
        """Test that query parameters are passed correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.base_url = "https://petstore.example.com/api"
        mock_client.request = AsyncMock(return_value=mock_response)

        server = McpWebGateway(petstore_openapi_spec, mock_client)

        async with Client(server) as client:
            await client.call_tool(
                "GET",
                {
                    "url": "https+get://petstore.example.com/api/pets",
                    "params": {"limit": 10, "status": "available"},
                },
            )

        # Check params were passed
        mock_client.request.assert_called_once_with(
            method="GET",
            url="https://petstore.example.com/api/pets",
            params={"limit": 10, "status": "available"},
        )

    async def test_plain_url_without_method_prefix(self, petstore_openapi_spec):
        """Test that plain URLs without method prefix work correctly."""
        # Create a mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "Fluffy", "species": "cat"}
        mock_response.raise_for_status = Mock()

        # Create mock client
        mock_client = AsyncMock()
        mock_client.base_url = "https://petstore.example.com/api"
        mock_client.request = AsyncMock(return_value=mock_response)

        server = McpWebGateway(petstore_openapi_spec, mock_client)

        # Use plain URL without method prefix
        async with Client(server) as client:
            result = await client.call_tool(
                "GET", {"url": "https://petstore.example.com/api/pets/1"}  # Plain URL
            )

        # Check the request was made correctly
        mock_client.request.assert_called_once_with(
            method="GET",
            url="https://petstore.example.com/api/pets/1",
        )

        # Check the result
        assert result.structured_content["id"] == 1
        assert result.structured_content["name"] == "Fluffy"

    async def test_get_tool_with_query_params_integration(self, server_and_client):
        """Test GET tool execution with query parameters using mock HTTP client."""
        server, mcp_client = server_and_client

        result = await mcp_client.call_tool(
            "GET",
            {
                "url": "https+get://petstore.example.com/api/pets",
                "params": {"limit": 2, "status": "available"},
            },
        )

        # Arrays are wrapped
        assert "result" in result.structured_content
        pets = result.structured_content["result"]
        assert len(pets) == 2
        assert all(p["status"] == "available" for p in pets)

    async def test_post_tool_with_request_body_integration(self, server_and_client):
        """Test POST tool execution with request body using mock HTTP client."""
        server, mcp_client = server_and_client

        result = await mcp_client.call_tool(
            "POST",
            {
                "url": "https+post://petstore.example.com/api/pets",
                "body": {
                    "name": "Max",
                    "species": "dog",
                    "breed": "Labrador",
                    "age": 2,
                },
            },
        )

        assert result.structured_content["name"] == "Max"
        assert result.structured_content["species"] == "dog"
        assert "id" in result.structured_content

    async def test_put_tool_with_path_params(self, server_and_client):
        """Test PUT tool execution with path parameters."""
        server, mcp_client = server_and_client

        result = await mcp_client.call_tool(
            "PUT",
            {
                "url": "https://petstore.example.com/api/pets/1",
                "body": {"status": "pending"},
            },
        )

        assert result.structured_content["id"] == 1
        assert result.structured_content["status"] == "pending"

    async def test_delete_tool_returns_empty_content(self, server_and_client):
        """Test DELETE tool execution returns empty content for 204."""
        server, mcp_client = server_and_client

        # Delete pet
        result = await mcp_client.call_tool(
            "DELETE", {"url": "https+delete://petstore.example.com/api/pets/3"}
        )

        # Should return empty content for 204
        assert len(result.content) == 1
        assert result.content[0].text == ""

        # Verify pet is gone
        with pytest.raises(Exception) as exc_info:
            await mcp_client.call_tool(
                "GET", {"url": "https://petstore.example.com/api/pets/3"}
            )
        assert "404" in str(exc_info.value)

    async def test_list_resources_and_templates(self, server_and_client):
        """Test listing resources and templates through MCP client."""
        server, mcp_client = server_and_client

        # List resources
        resources = await mcp_client.list_resources()
        resource_uris = {str(r.uri) for r in resources}

        # Check resources exist
        assert "https+get://petstore.example.com/api/pets" in resource_uris
        assert "https+post://petstore.example.com/api/pets" in resource_uris

        # List templates
        templates = await mcp_client.list_resource_templates()
        template_uris = {str(t.uriTemplate) for t in templates}

        # Check templates exist
        assert "https+get://petstore.example.com/api/pets/{petId}" in template_uris
        assert "https+put://petstore.example.com/api/pets/{petId}" in template_uris
        assert "https+delete://petstore.example.com/api/pets/{petId}" in template_uris


class TestMcpWebGatewayEdgeCases:
    """Test edge cases and error handling."""

    async def test_url_without_annotations_warning(self):
        """Test that URLs without annotations in registry still work but log warning."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {},
        }

        # Create mock client that will return 404
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason_phrase = "Not Found"
        mock_response.json.side_effect = ValueError()
        mock_response.text = "Not found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=None, response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)

        server = McpWebGateway(spec, mock_client)

        async with Client(server) as mcp_client:
            with pytest.raises(Exception) as exc_info:
                await mcp_client.call_tool(
                    "GET", {"url": "https://api.example.com/nonexistent"}
                )

            # Should get HTTP error, not resource not found
            assert "HTTP error 404" in str(exc_info.value)
