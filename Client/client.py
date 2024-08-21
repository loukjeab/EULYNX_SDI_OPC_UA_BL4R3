from opcua import Client, ua, Node
import time

class RailwayOpcUaClient:
    def __init__(self, server_urls):
        self.clients = [Client(url) for url in server_urls]
        self.connected_clients = []

    def connect_to_servers(self):
        """Connect to all OPC UA servers."""
        for client in self.clients:
            try:
                client.connect()
                self.connected_clients.append(client)
                print(f"Connected to {client.server_url}")
            except Exception as e:
                print(f"Failed to connect to {client.server_url}: {e}")

    def fetch_namespace(self, client):
        """Fetch the namespace array from the client."""
        return client.get_namespace_array()

    def compare_namespaces(self):
        """Compare namespaces across connected servers."""
        namespace_dict = {}
        for client in self.connected_clients:
            namespaces = self.fetch_namespace(client)
            for ns in namespaces:
                if ns not in namespace_dict:
                    namespace_dict[ns] = []
                namespace_dict[ns].append(client)
        return namespace_dict

    def summarize_nodes(self, client):
        """Recursively browse and summarize nodes."""
        root = client.get_root_node()
        print(f"Summarizing nodes for server: {client.server_url}")
        self._recursive_browse(root)

    def _recursive_browse(self, node, depth=0):
        """Helper method to recursively browse nodes."""
        try:
            for child in node.get_children():
                print("  " * depth, f"{child.get_browse_name()}: {child.nodeid}")
                self._recursive_browse(child, depth + 1)
        except Exception as e:
            print(f"Error browsing node {node}: {e}")

    def play_scenario(self, client, scenario_number):
        """Invoke SetScenario method on a server."""
        try:
            scenario_node = client.get_node("ns=1;i=7003")  # Assuming based on provided files
            input_arguments = [ua.Variant(scenario_number, ua.VariantType.Int32)]
            scenario_node.call_method("SetScenario", *input_arguments)
            print(f"Scenario {scenario_number} played on {client.server_url}")
        except Exception as e:
            print(f"Failed to play scenario {scenario_number}: {e}")

    def collect_diagnostics(self, client):
        """Collect diagnostics data from relevant nodes."""
        try:
            diagnostic_nodes = {
                "IsMaintenanceMode": "ns=1;i=6012",  # Example NodeIds
                "OperationStatus": "ns=1;i=6078"
            }

            print(f"Collecting diagnostics from {client.server_url}")
            for name, nodeid in diagnostic_nodes.items():
                node = client.get_node(nodeid)
                value = node.get_value()
                print(f"{name}: {value}")

        except Exception as e:
            print(f"Error collecting diagnostics: {e}")

    def collect_historical_data(self, client, nodeid):
        """Collect historical data for a given node."""
        try:
            node = client.get_node(nodeid)
            history = node.read_raw_history(None, None)
            print(f"Historical data for {nodeid} on {client.server_url}:")
            for entry in history:
                print(entry)
        except Exception as e:
            print(f"Error collecting historical data: {e}")

    def disconnect(self):
        """Disconnect all clients."""
        for client in self.connected_clients:
            client.disconnect()
        print("Disconnected from all servers.")


def main():
    server_urls = [
        "opc.tcp://localhost:4840",  # Replace with actual server URLs
        "opc.tcp://localhost:4841"
    ]

    opcua_client = RailwayOpcUaClient(server_urls)
    opcua_client.connect_to_servers()

    # Compare namespaces across servers
    namespaces = opcua_client.compare_namespaces()
    print("\nNamespaces and Servers:")
    for ns, clients in namespaces.items():
        print(f"Namespace: {ns}")
        for client in clients:
            print(f"  Server: {client.server_url}")

    # Summarize nodes for each connected server
    for client in opcua_client.connected_clients:
        opcua_client.summarize_nodes(client)

    # Play a scenario on each server
    for client in opcua_client.connected_clients:
        opcua_client.play_scenario(client, scenario_number=1)

    # Collect diagnostics from each server
    for client in opcua_client.connected_clients:
        opcua_client.collect_diagnostics(client)

    # Optional: Collect historical data for a specific node (Example NodeId)
    node_id = "ns=1;i=6071"  # Example node ID, modify as necessary
    for client in opcua_client.connected_clients:
        opcua_client.collect_historical_data(client, node_id)

    # Disconnect after operations are complete
    opcua_client.disconnect()


if __name__ == "__main__":
    main()
