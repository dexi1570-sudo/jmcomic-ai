import unittest
from unittest.mock import Mock, patch

from mcp.server.transport_security import TransportSecurityMiddleware

from jmcomic_ai.mcp.server import run_server


class TestRailwayHost(unittest.TestCase):
    def test_public_domain_is_allowed_without_disabling_protection(self):
        with patch.dict("os.environ", {"RAILWAY_PUBLIC_DOMAIN": "example.up.railway.app"}), \
                patch("jmcomic_ai.mcp.server.FastMCP") as factory, \
                patch("jmcomic_ai.mcp.server._register_service_tools"), \
                patch("jmcomic_ai.mcp.server._register_resources"):
            run_server("http", Mock(), host="0.0.0.0", port=8080)
        kwargs = factory.call_args.kwargs
        self.assertEqual(kwargs["host"], "0.0.0.0")
        self.assertEqual(kwargs["port"], 8080)
        security = kwargs["transport_security"]
        self.assertTrue(security.enable_dns_rebinding_protection)
        middleware = TransportSecurityMiddleware(security)
        self.assertTrue(middleware._validate_host("example.up.railway.app"))
        self.assertTrue(middleware._validate_host("example.up.railway.app:443"))
        self.assertFalse(middleware._validate_host("other.up.railway.app"))
        self.assertTrue(middleware._validate_origin(None))
        self.assertTrue(middleware._validate_origin("https://example.up.railway.app"))
        self.assertFalse(middleware._validate_origin("https://other.example"))
        factory.return_value.run.assert_called_once_with(transport="streamable-http")

    def test_local_hosts_remain_allowed(self):
        with patch.dict("os.environ", {"RAILWAY_PUBLIC_DOMAIN": ""}), \
                patch("jmcomic_ai.mcp.server.FastMCP") as factory, \
                patch("jmcomic_ai.mcp.server._register_service_tools"), \
                patch("jmcomic_ai.mcp.server._register_resources"):
            run_server("stdio", Mock())
        security = factory.call_args.kwargs["transport_security"]
        middleware = TransportSecurityMiddleware(security)
        self.assertTrue(middleware._validate_host("localhost:8000"))
        self.assertTrue(middleware._validate_host("127.0.0.1:8000"))
        self.assertFalse(middleware._validate_host("example.up.railway.app"))
