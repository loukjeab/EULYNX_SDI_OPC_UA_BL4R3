import asyncio
import pandas as pd
from asyncua import Client, ua
from asyncua.common.subscription import Subscription
from collections import defaultdict

class AdvancedOpcUaClient:
    def __init__(self, server_urls):
        """
        Initialize the OPC UA Client and connect to the servers.
        """
        self.clients = [Client(url) for url in server_urls]
        self.connected_clients = []
        self.namespaces = defaultdict(list)

    async def connect(self):
        """
        Connect to all the servers and retrieve namespace information.
        """
        for client in self.clients:
            await client.connect()
            self.connected_clients.append(client)
            print(f"Connected to server: {client.server_url}")
            await self.fetch_namespaces(client)

    async def fetch_namespaces(self, client):
        """
        Fetch and summarize namespaces for each connected server.
        """
        idx_to_namespace = {}
        for idx in range(100):  # assuming up to 100 namespaces, can be increased
            try:
                ns = await client.get_namespace_array()
                idx_to_namespace[idx] = ns[idx]
            except IndexError:
                break

        for idx, ns in idx_to_namespace.items():
            objects_node = client.nodes.objects
            node_list = await objects_node.get_children()
            node_names = [await node.read_display_name() for node in node_list]
            print(f"Namespace Index {idx} (URI: {ns}) has {len(node_list)} nodes.")
            self.namespaces[ns].append({"index": idx, "node_count": len(node_list), "nodes": node_names})

    def summarize_namespaces(self):
        """
        Summarize and print out identical namespaces across connected servers.
        """
        for ns, details in self.namespaces.items():
            print(f"\nNamespace URI: {ns}")
            for detail in details:
                print(f"  Index: {detail['index']} - Node Count: {detail['node_count']}")
                for node_name in detail['nodes']:
                    print(f"    Node: {node_name.Text}")

    async def monitor_nodes(self):
        """
        Set up subscriptions and monitor node values for changes.
        """
        for client in self.connected_clients:
            objects_node = client.nodes.objects
            node_list = await objects_node.get_children()

            handler = self.SubscriptionHandler()

            subscription = await client.create_subscription(500, handler)
            
            for node in node_list:
                try:
                    # Check if the node is of type `Variable`
                    node_class = await node.read_node_class()
                    if node_class == ua.NodeClass.Variable:
                        node_id = node.nodeid
                        print(f"Subscribed to node: {node_id}")
                        await subscription.subscribe_data_change(node)
                    else:
                        print(f"Skipped node {node.nodeid} as it is not a Variable node.")
                except Exception as e:
                    print(f"Failed to subscribe to node {node.nodeid}: {e}")

    class SubscriptionHandler:
        """
        Handler to manage data change notifications.
        """
        def datachange_notification(self, node, val, data):
            print(f"Data changed for Node: {node} | New Value: {val}")

        def event_notification(self, event):
            print(f"New Event: {event}")

    async def disconnect(self):
        """
        Disconnect from all servers.
        """
        for client in self.connected_clients:
            await client.disconnect()
            print(f"Disconnected from server: {client.server_url}")

if __name__ == "__main__":
    async def main():
        server_urls = ["opc.tcp://localhost:4840/EULYNX"]  # Add more server URLs if needed
        opcua_client = AdvancedOpcUaClient(server_urls)

        # Connect to servers and retrieve namespace information
        await opcua_client.connect()

        # Summarize namespaces
        opcua_client.summarize_namespaces()

        # Monitor nodes for changes
        await opcua_client.monitor_nodes()

        # Keep running for a while to capture data
        await asyncio.sleep(60)

        # Disconnect from the servers
        await opcua_client.disconnect()

    asyncio.run(main())
