"""Comprehensive regression tests for duplication module."""

import os
import json
import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
import importlib


class TestDuplicationFeatureToggle:
    """Test feature toggle functionality to prevent regression."""
    
    def test_feature_disabled_by_default(self):
        """Ensure duplication is disabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            # Force reload to pick up environment changes
            import importlib
            from meta_ads_mcp.core import duplication
            importlib.reload(duplication)
            
            assert not duplication.ENABLE_DUPLICATION
            # Note: Functions may persist in module namespace due to previous test runs
            # The important thing is that ENABLE_DUPLICATION flag is False
    
    def test_feature_enabled_with_env_var(self):
        """Ensure duplication is enabled when environment variable is set."""
        with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": "1"}):
            # Force reload to pick up environment changes
            import importlib
            from meta_ads_mcp.core import duplication
            importlib.reload(duplication)
            
            assert duplication.ENABLE_DUPLICATION
            assert hasattr(duplication, 'duplicate_campaign')
            assert hasattr(duplication, 'duplicate_adset')
            assert hasattr(duplication, 'duplicate_ad')
            assert hasattr(duplication, 'duplicate_creative')
    
    def test_feature_enabled_with_various_truthy_values(self):
        """Test that various truthy values enable the feature."""
        truthy_values = ["1", "true", "TRUE", "yes", "YES", "on", "ON", "enabled"]
        
        for value in truthy_values:
            with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": value}):
                import importlib
                from meta_ads_mcp.core import duplication
                importlib.reload(duplication)
                
                assert duplication.ENABLE_DUPLICATION, f"Value '{value}' should enable the feature"
    
    def test_feature_disabled_with_empty_string(self):
        """Test that empty string disables the feature."""
        with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": ""}):
            import importlib
            from meta_ads_mcp.core import duplication
            importlib.reload(duplication)
            
            assert not duplication.ENABLE_DUPLICATION


class TestDuplicationDecorators:
    """Test that decorators are applied correctly to prevent regression."""
    
    @pytest.fixture(autouse=True)
    def enable_feature(self):
        """Enable the duplication feature for these tests."""
        with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": "1"}):
            import importlib
            from meta_ads_mcp.core import duplication
            importlib.reload(duplication)
            yield duplication
    
    def test_functions_have_meta_api_tool_decorator(self, enable_feature):
        """Ensure all duplication functions have @meta_api_tool decorator."""
        duplication = enable_feature
        
        functions = ['duplicate_campaign', 'duplicate_adset', 'duplicate_ad', 'duplicate_creative']
        
        for func_name in functions:
            func = getattr(duplication, func_name)
            
            # Check that function has been wrapped by meta_api_tool
            # The meta_api_tool decorator should add access token handling
            assert callable(func), f"{func_name} should be callable"
            
            # Check function signature includes access_token parameter
            import inspect
            sig = inspect.signature(func)
            assert 'access_token' in sig.parameters, f"{func_name} should have access_token parameter"
            assert sig.parameters['access_token'].default is None, f"{func_name} access_token should default to None"
    
    @pytest.mark.asyncio
    async def test_functions_are_mcp_tools(self, enable_feature):
        """Ensure all duplication functions are registered as MCP tools."""
        # This test ensures the @mcp_server.tool() decorator is working
        from meta_ads_mcp.core.server import mcp_server
        
        # Get all registered tool names (list_tools is async)
        tools = await mcp_server.list_tools()
        tool_names = [tool.name for tool in tools]
        
        expected_tools = ['duplicate_campaign', 'duplicate_adset', 'duplicate_ad', 'duplicate_creative']
        
        for tool_name in expected_tools:
            assert tool_name in tool_names, f"{tool_name} should be registered as an MCP tool"


class TestDuplicationAPIContract:
    """Test API contract to prevent regression in external API calls."""
    
    @pytest.fixture(autouse=True)
    def enable_feature(self):
        """Enable the duplication feature for these tests."""
        with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": "1"}):
            import importlib
            from meta_ads_mcp.core import duplication
            importlib.reload(duplication)
            yield duplication
    
    @pytest.mark.asyncio
    async def test_api_endpoint_construction(self, enable_feature):
        """Test that API endpoints are constructed correctly."""
        duplication = enable_feature
        
        test_cases = [
            ("campaign", "123456789", "https://mcp.pipeboard.co/api/meta/duplicate/campaign/123456789"),
            ("adset", "987654321", "https://mcp.pipeboard.co/api/meta/duplicate/adset/987654321"),
            ("ad", "555666777", "https://mcp.pipeboard.co/api/meta/duplicate/ad/555666777"),
            ("creative", "111222333", "https://mcp.pipeboard.co/api/meta/duplicate/creative/111222333"),
        ]
        
        for resource_type, resource_id, expected_url in test_cases:
            with patch("meta_ads_mcp.core.duplication.httpx.AsyncClient") as mock_client:
                mock_response = AsyncMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"success": True}
                mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
                
                await duplication._forward_duplication_request(
                    resource_type, resource_id, "test_token", {}
                )
                
                # Verify the correct URL was called
                call_args = mock_client.return_value.__aenter__.return_value.post.call_args
                actual_url = call_args[0][0]
                assert actual_url == expected_url, f"Expected {expected_url}, got {actual_url}"
    
    @pytest.mark.asyncio
    async def test_request_headers_format(self, enable_feature):
        """Test that request headers are formatted correctly."""
        duplication = enable_feature
        
        with patch("meta_ads_mcp.core.duplication.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            await duplication._forward_duplication_request(
                "campaign", "123456789", "test_token_12345", {"name_suffix": " - Test"}
            )
            
            # Verify headers
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            headers = call_args[1]["headers"]
            
            assert headers["Authorization"] == "Bearer test_token_12345"
            assert headers["Content-Type"] == "application/json"
            assert headers["User-Agent"] == "meta-ads-mcp/1.0"
    
    @pytest.mark.asyncio
    async def test_request_timeout_configuration(self, enable_feature):
        """Test that request timeout is configured correctly."""
        duplication = enable_feature
        
        with patch("meta_ads_mcp.core.duplication.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            await duplication._forward_duplication_request(
                "campaign", "123456789", "test_token", {}
            )
            
            # Verify timeout is set to 30 seconds
            mock_client.assert_called_once_with(timeout=30.0)


class TestDuplicationErrorHandling:
    """Test error handling to prevent regression in error scenarios."""
    
    @pytest.fixture(autouse=True)
    def enable_feature(self):
        """Enable the duplication feature for these tests."""
        with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": "1"}):
            import importlib
            from meta_ads_mcp.core import duplication
            importlib.reload(duplication)
            yield duplication
    
    @pytest.mark.asyncio
    async def test_missing_access_token_error(self, enable_feature):
        """Test error handling when access token is missing."""
        duplication = enable_feature
        
        result = await duplication._forward_duplication_request("campaign", "123", None, {})
        result_json = json.loads(result)
        
        assert result_json["error"] == "authentication_required"
        assert "access token not found" in result_json["message"]
        assert result_json["details"]["required"] == "Valid access token from authenticated session"
    
    @pytest.mark.asyncio
    async def test_http_status_code_handling(self, enable_feature):
        """Test handling of various HTTP status codes."""
        duplication = enable_feature
        
        status_code_tests = [
            (200, "success_response", "json"),
            (401, "authentication_failed", "error"),
            (403, "premium_feature_required", "error"),
            (429, "rate_limit_exceeded", "error"),
            (500, "duplication_failed", "error"),
        ]
        
        for status_code, expected_error_type, response_type in status_code_tests:
            with patch("meta_ads_mcp.core.duplication.httpx.AsyncClient") as mock_client:
                # Use MagicMock instead of AsyncMock for more predictable behavior
                mock_response = MagicMock()
                mock_response.status_code = status_code
                
                if status_code == 200:
                    mock_response.json.return_value = {"success": True, "id": "new_123"}
                elif status_code == 429:
                    mock_response.headers.get.return_value = "60"
                    mock_response.json.side_effect = Exception("No JSON")
                    mock_response.text = "Rate limited"
                else:
                    mock_response.json.side_effect = Exception("No JSON")
                    mock_response.text = f"Error {status_code}"
                
                mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
                
                result = await duplication._forward_duplication_request(
                    "campaign", "123", "token", {}
                )
                result_json = json.loads(result)
                
                if response_type == "error":
                    assert result_json["error"] == expected_error_type
                else:
                    assert "success" in result_json or "id" in result_json
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, enable_feature):
        """Test handling of network errors."""
        duplication = enable_feature
        
        network_errors = [
            (httpx.TimeoutException("Timeout"), "request_timeout"),
            (httpx.RequestError("Connection failed"), "network_error"),
            (Exception("Unexpected error"), "unexpected_error"),
        ]
        
        for exception, expected_error in network_errors:
            with patch("meta_ads_mcp.core.duplication.httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.post.side_effect = exception
                
                result = await duplication._forward_duplication_request(
                    "campaign", "123", "token", {}
                )
                result_json = json.loads(result)
                
                assert result_json["error"] == expected_error


class TestDuplicationParameterHandling:
    """Test parameter handling to prevent regression in data processing."""
    
    @pytest.fixture(autouse=True)
    def enable_feature(self):
        """Enable the duplication feature for these tests."""
        with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": "1"}):
            import importlib
            from meta_ads_mcp.core import duplication
            importlib.reload(duplication)
            yield duplication
    
    @pytest.mark.asyncio
    async def test_none_values_filtered_from_options(self, enable_feature):
        """Test that None values are filtered from options."""
        duplication = enable_feature
        
        with patch("meta_ads_mcp.core.duplication.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Test with options containing None values
            options_with_none = {
                "name_suffix": " - Test",
                "new_daily_budget": None,
                "new_status": "PAUSED",
                "new_headline": None,
            }
            
            await duplication._forward_duplication_request(
                "campaign", "123", "token", options_with_none
            )
            
            # Verify None values were filtered out
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            json_payload = call_args[1]["json"]
            
            expected_payload = {
                "name_suffix": " - Test",
                "new_status": "PAUSED"
            }
            assert json_payload == expected_payload
    
    @pytest.mark.asyncio
    async def test_campaign_duplication_parameter_forwarding(self, enable_feature):
        """Test that campaign duplication forwards all parameters correctly."""
        duplication = enable_feature
        
        with patch("meta_ads_mcp.core.duplication._forward_duplication_request") as mock_forward:
            mock_forward.return_value = '{"success": true}'
            
            # Test with all parameters
            result = await duplication.duplicate_campaign(
                campaign_id="123456789",
                access_token="test_token",
                name_suffix=" - New Copy",
                include_ad_sets=False,
                include_ads=True,
                include_creatives=False,
                copy_schedule=True,
                new_daily_budget=100.50,
                new_status="ACTIVE"
            )
            
            # Verify parameters were forwarded correctly
            mock_forward.assert_called_once_with(
                "campaign",
                "123456789",
                "test_token",
                {
                    "name_suffix": " - New Copy",
                    "include_ad_sets": False,
                    "include_ads": True,
                    "include_creatives": False,
                    "copy_schedule": True,
                    "new_daily_budget": 100.50,
                    "new_status": "ACTIVE"
                }
            )
    
    def test_estimated_components_calculation(self, enable_feature):
        """Test that estimated components are calculated correctly."""
        duplication = enable_feature
        
        test_cases = [
            # Campaign with all components
            ("campaign", {"include_ad_sets": True, "include_ads": True, "include_creatives": True}, 
             {"campaigns": 1, "ad_sets": "3-5 (estimated)", "ads": "5-15 (estimated)", "creatives": "5-15 (estimated)"}),
            
            # Campaign with no sub-components
            ("campaign", {"include_ad_sets": False, "include_ads": False, "include_creatives": False},
             {"campaigns": 1}),
            
            # Ad set with ads
            ("adset", {"include_ads": True, "include_creatives": True},
             {"ad_sets": 1, "ads": "2-5 (estimated)", "creatives": "2-5 (estimated)"}),
            
            # Ad set without ads
            ("adset", {"include_ads": False, "include_creatives": False},
             {"ad_sets": 1}),
            
            # Single ad with creative
            ("ad", {"duplicate_creative": True},
             {"ads": 1, "creatives": 1}),
            
            # Single ad without creative
            ("ad", {"duplicate_creative": False},
             {"ads": 1}),
            
            # Single creative
            ("creative", {},
             {"creatives": 1}),
        ]
        
        for resource_type, options, expected in test_cases:
            result = duplication._get_estimated_components(resource_type, options)
            assert result == expected, f"Failed for {resource_type} with {options}"


class TestDuplicationIntegration:
    """Integration tests to prevent regression in end-to-end functionality."""
    
    @pytest.fixture(autouse=True)
    def enable_feature(self):
        """Enable the duplication feature for these tests."""
        with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": "1"}):
            import importlib
            from meta_ads_mcp.core import duplication
            importlib.reload(duplication)
            yield duplication
    
    @pytest.mark.asyncio
    async def test_end_to_end_successful_duplication(self, enable_feature):
        """Test complete successful duplication flow."""
        duplication = enable_feature
        
        # Mock the auth system completely to bypass the @meta_api_tool decorator checks
        with patch("meta_ads_mcp.core.auth.get_current_access_token") as mock_get_token:
            with patch("meta_ads_mcp.core.auth.auth_manager") as mock_auth_manager:
                with patch("meta_ads_mcp.core.auth.meta_config") as mock_meta_config:
                    # Setup complete auth mocking
                    mock_get_token.return_value = "valid_token"
                    mock_auth_manager.app_id = "valid_app_id"
                    mock_auth_manager.use_pipeboard = False
                    mock_meta_config.get_app_id.return_value = "valid_app_id"
                    
                    with patch("meta_ads_mcp.core.duplication.httpx.AsyncClient") as mock_client:
                        # Mock successful response
                        mock_response = MagicMock()
                        mock_response.status_code = 200
                        mock_response.json.return_value = {
                            "success": True,
                            "new_campaign_id": "987654321",
                            "duplicated_components": {
                                "campaigns": 1,
                                "ad_sets": 3,
                                "ads": 8,
                                "creatives": 8
                            }
                        }
                        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
                        
                        # Call the function with explicit token
                        result = await duplication.duplicate_campaign(
                            campaign_id="123456789",
                            access_token="valid_token",
                            name_suffix=" - Test Copy"
                        )
                        
                        # Verify result - handle @meta_api_tool wrapper
                        result_json = json.loads(result)
                        if "data" in result_json:
                            actual_result = json.loads(result_json["data"])
                        else:
                            actual_result = result_json
                            
                        assert actual_result["success"] is True
                        assert actual_result["new_campaign_id"] == "987654321"
                        assert "duplicated_components" in actual_result
    
    @pytest.mark.asyncio
    async def test_premium_feature_upgrade_flow(self, enable_feature):
        """Test premium feature upgrade message flow."""
        duplication = enable_feature
        
        # Mock the auth system completely to bypass the @meta_api_tool decorator checks
        with patch("meta_ads_mcp.core.auth.get_current_access_token") as mock_get_token:
            with patch("meta_ads_mcp.core.auth.auth_manager") as mock_auth_manager:
                with patch("meta_ads_mcp.core.auth.meta_config") as mock_meta_config:
                    # Setup complete auth mocking
                    mock_get_token.return_value = "valid_token"
                    mock_auth_manager.app_id = "valid_app_id"
                    mock_auth_manager.use_pipeboard = False
                    mock_meta_config.get_app_id.return_value = "valid_app_id"
                    
                    with patch("meta_ads_mcp.core.duplication.httpx.AsyncClient") as mock_client:
                        # Mock 403 response (premium feature required)
                        mock_response = MagicMock()
                        mock_response.status_code = 403
                        mock_response.json.return_value = {"error": "premium_feature"}
                        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
                        
                        result = await duplication.duplicate_campaign(
                            campaign_id="123456789",
                            access_token="valid_token"
                        )
                        
                        # The @meta_api_tool decorator wraps the result in a data field
                        result_json = json.loads(result)
                        if "data" in result_json:
                            actual_result = json.loads(result_json["data"])
                        else:
                            actual_result = result_json
                            
                        assert actual_result["error"] == "premium_feature_required"
                        assert "premium feature" in actual_result["message"]
                        assert "upgrade_url" in actual_result["details"]
                        assert actual_result["details"]["upgrade_url"] == "https://pipeboard.co/upgrade"
                        assert "request_parameters" in actual_result
                        assert "preview" in actual_result


class TestDuplicationTokenHandling:
    """Test access token handling to prevent auth regression."""
    
    @pytest.fixture(autouse=True)
    def enable_feature(self):
        """Enable the duplication feature for these tests."""
        with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": "1"}):
            import importlib
            from meta_ads_mcp.core import duplication
            importlib.reload(duplication)
            yield duplication
    
    @pytest.mark.asyncio
    async def test_meta_api_tool_decorator_token_handling(self, enable_feature):
        """Test that @meta_api_tool decorator properly handles explicit tokens."""
        duplication = enable_feature
        
        # Test with explicit token - this should bypass auth system entirely
        with patch("meta_ads_mcp.core.duplication._forward_duplication_request") as mock_forward:
            mock_forward.return_value = '{"success": true}'
            
            # Call with explicit access_token
            await duplication.duplicate_campaign(
                campaign_id="123456789",
                access_token="explicit_token_12345"
            )
            
            # Verify the explicit token was passed through
            mock_forward.assert_called_once()
            call_args = mock_forward.call_args[0]
            assert call_args[2] == "explicit_token_12345"  # access_token is 3rd argument
    
    @pytest.mark.asyncio
    async def test_explicit_token_overrides_injection(self, enable_feature):
        """Test that explicit token overrides auto-injection."""
        duplication = enable_feature
        
        with patch("meta_ads_mcp.core.auth.get_current_access_token") as mock_get_token:
            mock_get_token.return_value = "injected_token"
            
            with patch("meta_ads_mcp.core.duplication._forward_duplication_request") as mock_forward:
                mock_forward.return_value = '{"success": true}'
                
                # Call with explicit access_token
                await duplication.duplicate_campaign(
                    campaign_id="123456789",
                    access_token="explicit_token_12345"
                )
                
                # Verify the explicit token was used, not the injected one
                mock_forward.assert_called_once()
                call_args = mock_forward.call_args[0]
                assert call_args[2] == "explicit_token_12345"  # access_token is 3rd argument


class TestDuplicationRegressionEdgeCases:
    """Test edge cases that could cause regressions."""
    
    @pytest.fixture(autouse=True)
    def enable_feature(self):
        """Enable the duplication feature for these tests."""
        with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": "1"}):
            import importlib
            from meta_ads_mcp.core import duplication
            importlib.reload(duplication)
            yield duplication
    
    @pytest.mark.asyncio
    async def test_empty_string_parameters(self, enable_feature):
        """Test handling of empty string parameters."""
        duplication = enable_feature
        
        with patch("meta_ads_mcp.core.duplication._forward_duplication_request") as mock_forward:
            mock_forward.return_value = '{"success": true}'
            
            # Test with empty strings
            await duplication.duplicate_campaign(
                campaign_id="123456789",
                access_token="token",
                name_suffix="",  # Empty string
                new_status=""    # Empty string
            )
            
            # Verify empty strings are preserved (not filtered like None)
            call_args = mock_forward.call_args[0]
            options = call_args[3]
            assert options["name_suffix"] == ""
            assert options["new_status"] == ""
    
    @pytest.mark.asyncio
    async def test_unicode_parameters(self, enable_feature):
        """Test handling of unicode parameters."""
        duplication = enable_feature
        
        with patch("meta_ads_mcp.core.duplication.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Test with unicode characters
            unicode_suffix = " - 复制版本 🚀"
            await duplication._forward_duplication_request(
                "campaign", "123", "token", {"name_suffix": unicode_suffix}
            )
            
            # Verify unicode is preserved in the request
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            json_payload = call_args[1]["json"]
            assert json_payload["name_suffix"] == unicode_suffix
    
    @pytest.mark.asyncio
    async def test_large_parameter_values(self, enable_feature):
        """Test handling of large parameter values."""
        duplication = enable_feature
        
        with patch("meta_ads_mcp.core.duplication.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Test with very large budget value
            large_budget = 999999999.99
            await duplication._forward_duplication_request(
                "campaign", "123", "token", {"new_daily_budget": large_budget}
            )
            
            # Verify large values are preserved
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            json_payload = call_args[1]["json"]
            assert json_payload["new_daily_budget"] == large_budget
    
    def test_module_reload_safety(self):
        """Test that module can be safely reloaded without side effects."""
        # This tests for common issues like global state pollution
        
        # Enable feature
        with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": "1"}):
            import importlib
            from meta_ads_mcp.core import duplication
            importlib.reload(duplication)
            
            assert duplication.ENABLE_DUPLICATION
            assert hasattr(duplication, 'duplicate_campaign')
        
        # Disable feature and reload
        with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": ""}):
            importlib.reload(duplication)
            
            assert not duplication.ENABLE_DUPLICATION
            # Note: Functions may still exist in the module namespace due to Python's 
            # module loading behavior, but they won't be registered as MCP tools
            # This is expected behavior and not a problem for the feature toggle
        
        # Re-enable feature and reload
        with patch.dict(os.environ, {"META_ADS_ENABLE_DUPLICATION": "1"}):
            importlib.reload(duplication)
            
            assert duplication.ENABLE_DUPLICATION
            assert hasattr(duplication, 'duplicate_campaign') 