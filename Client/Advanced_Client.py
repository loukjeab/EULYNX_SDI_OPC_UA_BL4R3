import asyncio
import pandas as pd
from asyncua import Client, ua
import datetime
import csv
import tkinter as tk
from tkinter import ttk, messagebox

class OPCUAClient:
    def __init__(self, excel_file):
        self.servers = []
        self.subscriptions = []
        self.csv_file = 'opcua_data_log.csv'
        self.node_info = self.load_node_info(excel_file)
        self.logged_data = []

    def load_node_info(self, file_path):
        """
        Load node information from the Excel file.
        """
        df = pd.read_excel(file_path, sheet_name='default', engine='openpyxl')
        nodes = []
        for _, row in df.iterrows():
            nodes.append({
                "Name": row["Name"],
                "ns": int(row["ns"]),
                "i": int(row["i"]),
                "Value": row.get("Value", None)
            })
        return nodes

    async def connect_to_server(self, server_url):
        """
        Connects to the given OPC UA server and returns the client object.
        """
        try:
            client = Client(server_url)
            await client.connect()
            print(f"Connected to server: {server_url}")
            return client
        except Exception as e:
            print(f"Failed to connect to {server_url}. Error: {e}")
            return None

    async def disconnect_from_server(self):
        """
        Disconnects from all connected servers.
        """
        for client in self.servers:
            try:
                await client.disconnect()
                print(f"Disconnected from server: {client.server_url}")
            except Exception as e:
                print(f"Failed to disconnect from server: {e}")
        self.servers.clear()
        messagebox.showinfo("Disconnected", "Successfully disconnected from all servers.")

    async def add_server(self, server_url):
        """
        Adds a server to the list of servers and connects to it.
        """
        client = await self.connect_to_server(server_url)
        if client:
            self.servers.append(client)
            await self.recognize_and_summarize_namespaces(client)

    async def recognize_and_summarize_namespaces(self, client):
        """
        Scans and summarizes namespaces across the connected servers.
        """
        try:
            namespaces = await client.get_namespace_array()
            print(f"Namespaces for {client.server_url}:")
            for index, ns in enumerate(namespaces):
                print(f"Namespace Index {index} (URI: {ns})")
            return namespaces
        except Exception as e:
            print(f"Error summarizing namespaces for {client.server_url}: {e}")

    async def subscribe_and_monitor_nodes(self):
        """
        Subscribes to nodes for each connected server and monitors them in real-time.
        """
        tasks = [self.monitor_nodes(client) for client in self.servers]
        await asyncio.gather(*tasks)

    async def monitor_nodes(self, client):
        """
        Subscribes to nodes based on the information loaded from the Excel file.
        """
        try:
            handler = self.SubscriptionHandler(self)
            subscription = await client.create_subscription(500, handler)
            self.subscriptions.append(subscription)

            for node_info in self.node_info:
                node = client.get_node(ua.NodeId(node_info["i"], node_info["ns"]))
                try:
                    node_class = await node.read_node_class()
                    if node_class == ua.NodeClass.Variable:
                        print(f"Subscribed to node: {node_info['Name']} (NodeId: ns={node_info['ns']};i={node_info['i']})")
                        await subscription.subscribe_data_change(node)
                except Exception as e:
                    print(f"Failed to subscribe to node {node_info['Name']}: {e}")
        except Exception as e:
            print(f"Error setting up subscription for {client.server_url}: {e}")

    def log_data(self, node, val):
        """
        Logs node value changes to a CSV file in real-time with a timestamp.
        """
        timestamp = datetime.datetime.now()
        node_info = next((info for info in self.node_info if info['i'] == node.nodeid.Identifier and info['ns'] == node.nodeid.NamespaceIndex), {"Name": "Unknown", "Node": str(node)})

        data_entry = {
            "timestamp": timestamp,
            "Name": node_info["Name"],
            "Node": f"ns={node.nodeid.NamespaceIndex};i={node.nodeid.Identifier}",
            "value": val
        }
        self.logged_data.append(data_entry)
        print(f"Logged data: {data_entry}")

        # Append to CSV file
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, node_info["Name"], data_entry["Node"], val])

        # Update the GUI with the latest logged data
        app.update_log_display(data_entry)

    class SubscriptionHandler:
        def __init__(self, client_obj):
            self.client_obj = client_obj

        def datachange_notification(self, node, val, data):
            """
            Handles data change notifications.
            """
            print(f"Data change detected for node: {node}")
            self.client_obj.log_data(node, val)

        def event_notification(self, event):
            """
            Handles events.
            """
            print(f"New event: {event}")

class OPCUAGUI(tk.Tk):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.title("MDM - Maintenance and Data Management System")
        self.geometry("600x400")

        # Create GUI components
        self.create_widgets()

        # Create an asyncio loop for running async tasks
        self.loop = asyncio.get_event_loop()

        # Run the loop in the background
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.periodic_async_call()

    def create_widgets(self):
        # Server Entry Field and Button
        self.server_entry_label = tk.Label(self, text="Server URL:")
        self.server_entry_label.pack(pady=5)

        self.server_entry = tk.Entry(self, width=50)
        self.server_entry.pack(pady=5)

        self.add_server_button = tk.Button(self, text="Add Server", command=self.add_server)
        self.add_server_button.pack(pady=5)

        # Monitoring Button
        self.monitor_button = tk.Button(self, text="Start Monitoring (30s)", command=self.start_monitoring)
        self.monitor_button.pack(pady=5)

        # Disconnect Button
        self.disconnect_button = tk.Button(self, text="Disconnect from Server", command=self.disconnect_from_server)
        self.disconnect_button.pack(pady=5)

        # Log Display
        self.log_display_label = tk.Label(self, text="Monitored Data:")
        self.log_display_label.pack(pady=5)

        self.log_display = tk.Text(self, height=10, width=70)
        self.log_display.pack(pady=5)

        # Export to CSV Button
        self.export_button = tk.Button(self, text="Save Data to CSV", command=self.export_to_csv)
        self.export_button.pack(pady=5)

    def add_server(self):
        server_url = self.server_entry.get().strip()
        if server_url:
            self.loop.create_task(self.client.add_server(server_url))
            messagebox.showinfo("Server Added", f"Successfully connected to {server_url}")

    def start_monitoring(self):
        # Start monitoring for 60 seconds, then disconnect
        self.loop.create_task(self.monitor_for_interval())

    async def monitor_for_interval(self):
        await self.client.subscribe_and_monitor_nodes()
        await asyncio.sleep(60)  # Monitor for 60 seconds
        await self.client.disconnect_from_server()

    def disconnect_from_server(self):
        self.loop.create_task(self.client.disconnect_from_server())

    def update_log_display(self, data_entry):
        """
        Updates the log display in the GUI with new data.
        """
        self.log_display.insert(tk.END, f"{data_entry['timestamp']} - {data_entry['Name']} - {data_entry['Node']} - {data_entry['value']}\n")
        self.log_display.see(tk.END)  # Scroll to the latest entry

    def export_to_csv(self):
        """
        Export the logged data to a CSV file.
        """
        messagebox.showinfo("Export", "Data saved to opcua_data_log.csv")

    def periodic_async_call(self):
        """
        Periodically runs the asyncio event loop while the Tkinter main loop is running.
        """
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()
        self.after(100, self.periodic_async_call)  # Adjust the timing as needed

    def on_closing(self):
        """
        Clean up when the GUI window is closed.
        """
        self.loop.stop()
        self.destroy()

if __name__ == "__main__":
    # Update the path to your Excel file here
    excel_file = r'BL4R3-rev01-Diagnostic_NodeID_List-scenario.xlsx'
    client = OPCUAClient(excel_file)

    # Create the CSV file with headers
    with open(client.csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "Name", "Node", "value"])

    # Create and start the GUI
    app = OPCUAGUI(client)
    app.mainloop()
