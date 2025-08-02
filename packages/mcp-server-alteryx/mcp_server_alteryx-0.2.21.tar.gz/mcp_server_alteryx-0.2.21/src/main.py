import click
from src.mcp_server import MCPAlteryxServer
import logging
#import netifaces

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse", "streamable-http"]),
    default="stdio",
    help="Transport type",
)
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
def main(transport: str, log_level: str) -> None:
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Log all available IP addresses and their MAC addresses
    # def list_ip_addresses_and_mac_addresses():
    #     network_info = {}
    #     try:
    #         # Get all network interfaces
    #         interfaces = netifaces.interfaces()
    #         for interface in interfaces:
    #             try:
    #                 # Get IP addresses
    #                 ip_addresses = netifaces.ifaddresses(interface).get(netifaces.AF_INET, [])
    #                 ip_list = [addr["addr"] for addr in ip_addresses]

    #                 # Get MAC address
    #                 mac = netifaces.ifaddresses(interface).get(netifaces.AF_LINK, [])
    #                 mac_address = mac[0]["addr"] if mac else None

    #                 if ip_list or mac_address:
    #                     network_info[interface] = {"ip_addresses": ip_list, "mac_address": mac_address}
    #             except Exception as e:
    #                 logger.error(f"Error getting info for interface {interface}: {e}")
    #     except Exception as e:
    #         logger.error(f"Error listing network interfaces: {e}")
    #     return network_info

    # network_info = list_ip_addresses_and_mac_addresses()
    # for interface, info in network_info.items():
    #     logger.info(f"Interface: {interface}")
    #     logger.info(f"  IP Addresses: {info['ip_addresses']}")
    #     logger.info(f"  MAC Address: {info['mac_address']}")

    # Create and initialize the MCP server
    server = MCPAlteryxServer()
    server = server.initialize()
    server = server.register_tools()

    print("Starting Alteryx Server Client")
    match transport:
        case "stdio":
            server.app.run(transport="stdio")
        case "sse":
            server.app.run(transport="sse")
        case "streamable-http":
            server.app.run(transport="streamable-http")


if __name__ == "__main__":
    main(transport="sse", log_level="INFO")
