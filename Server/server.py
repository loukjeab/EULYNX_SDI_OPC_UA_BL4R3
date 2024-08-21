import asyncio
import pandas as pd
from asyncua import Server, ua

# Constants for event-specific node names
EVENT_SPECIFIC_NODES = ["isEndpositionReached", "commandedPosition", "failureReason"]

# Load node information from Excel file
def load_node_info(file_path, sheet_name):
    """
    Load node information from an Excel file.

    Parameters:
        file_path (str): The path to the Excel file.
        sheet_name (str): The name of the sheet to read from.

    Returns:
        list[dict]: A list of dictionaries containing node information.
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
    if sheet_name == 'default':
        return [
            {
                "name": row["Name"],
                "datatype": row["DataType"].replace("(Enumeration)", "").strip(),
                "ns": int(row["ns"]),
                "i": int(row["i"]),
                "value": row["Value"]
            }
            for _, row in df.iterrows()
            if row["NodeClass"] == "Variable"
        ]
    else:
        return [
            {
                "name": row["Name"],
                "datatype": row["DataType"].replace("(Enumeration)", "").strip(),
                "ns": int(row["ns"]),
                "i": int(row["i"])
            }
            for _, row in df.iterrows()
            if row["NodeClass"] == "Variable"
        ]

# Clean values from the Excel file
def clean_value(value, datatype):
    """
    Clean and convert the value from the Excel file based on its datatype.

    Parameters:
        value: The value to be cleaned.
        datatype (str): The datatype of the value.

    Returns:
        The cleaned value in its appropriate type or None if not applicable.
    """
    if pd.isnull(value) or value == "Null":
        return None

    if "Enumeration" in datatype or "Int32" in datatype or "UInt16" in datatype or "UInt64" in datatype:
        try:
            return int(''.join(filter(str.isdigit, str(value).split()[0])))
        except ValueError:
            return None
    elif "Boolean" in datatype:
        return value.lower() == "true" if isinstance(value, str) else bool(value)
    elif "Double" in datatype or "Real" in datatype:
        return float(value)
    elif "String" in datatype:
        return str(value)
    elif "DateTime" in datatype:
        try:
            dt = pd.to_datetime(value)
            if dt.year < 1601:
                return None
            return dt
        except (ValueError, OverflowError, pd.errors.OutOfBoundsDatetime):
            return None
    return value

# Load scenario steps from Excel file
def load_scenario_steps(file_path, sheet_name):
    """
    Load scenario steps from an Excel file.

    Parameters:
        file_path (str): The path to the Excel file.
        sheet_name (str): The name of the sheet to read from.

    Returns:
        list[dict]: A list of dictionaries containing scenario step data.
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
    steps = []
    for step_column in df.columns:
        if step_column.startswith("Step"):
            step_data = {row["Name"]: clean_value(row[step_column], row["DataType"]) for _, row in df.iterrows()}
            steps.append(step_data)
    return steps

# Generate and trigger events for scenario
async def generate_event(server, source_node, event_type_node, step_data):
    """
    Generate and trigger an event for the given scenario step data.

    Parameters:
        server (Server): The OPC UA server instance.
        source_node (Node): The source node for the event.
        event_type_node (Node): The event type node.
        step_data (dict): The data for the current scenario step.

    Returns:
        None
    """
    event = await server.get_event_generator(event_type_node, source_node)
    event.event.Severity = 5555
    event.event.Message = ua.LocalizedText("Event triggered with scenario values")
    
    # Set event-specific node values
    for attr in EVENT_SPECIFIC_NODES:
        event.event.SetValue(attr, ua.Variant(step_data.get(attr, False), ua.VariantType.Boolean))

    await event.trigger()
    print(f"Scenario Event triggered: {step_data}")

# Update Data Access View nodes
async def update_node_value(server, node_info, value):
    """
    Update the value of a specific node on the server.

    Parameters:
        server (Server): The OPC UA server instance.
        node_info (dict): Information about the node to be updated.
        value: The value to be written to the node.

    Returns:
        None
    """
    node = server.get_node(ua.NodeId(node_info["i"], node_info["ns"]))
    try:
        data_type = await node.read_data_type_as_variant_type()
        cleaned_value = clean_value(value, data_type.name)
        if cleaned_value is None and data_type != ua.VariantType.String:
            print(f"Skipping node: {node_info['name']} due to None value and incompatible type.")
            return

        if isinstance(cleaned_value, pd.Timestamp):
            cleaned_value = cleaned_value.to_pydatetime()

        variant_value = ua.Variant(cleaned_value, data_type)
        await node.write_value(variant_value)
        print(f"Updated {node_info['name']} (ns={node_info['ns']}; i={node_info['i']}) to {cleaned_value}")
    except Exception as e:
        print(f"Error writing to {node_info['name']} (ns={node_info['ns']}; i={node_info['i']}): {e}")

# Update Data Access View nodes for a scenario step
async def update_data_access_view(server, nodes, scenario_step=None):
    """
    Update Data Access View nodes for a given scenario step.

    Parameters:
        server (Server): The OPC UA server instance.
        nodes (list[dict]): A list of node information dictionaries.
        scenario_step (dict, optional): The data for the current scenario step.

    Returns:
        None
    """
    for node_info in nodes:
        if node_info["name"] in EVENT_SPECIFIC_NODES:
            continue
        value = scenario_step.get(node_info["name"], node_info.get("value")) if scenario_step else node_info.get("value")
        if value is not None:
            await update_node_value(server, node_info, value)

# Asynchronous input function
async def async_input(prompt: str) -> str:
    """
    Asynchronous input function to handle user input.

    Parameters:
        prompt (str): The prompt message to display.

    Returns:
        str: The user input.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, input, prompt)

# Trigger events for event-specific nodes
async def trigger_event(server, event_type_node, instance, step_data, nodes):
    """
    Trigger events for event-specific nodes.

    Parameters:
        server (Server): The OPC UA server instance.
        event_type_node (Node): The event type node.
        instance (Node): The instance node.
        step_data (dict): The data for the current scenario step.
        nodes (list[dict]): A list of dictionaries containing node information from the Excel file.

    Returns:
        None
    """
    event = await server.get_event_generator(event_type_node, instance)
    event.event.Severity = 500
    event.event.Message = ua.LocalizedText("Event triggered with scenario values")
    
    for node_info in nodes:
        if node_info["name"] in EVENT_SPECIFIC_NODES:
            value = step_data.get(node_info["name"], False if node_info["datatype"] == "Boolean" else 0)
            variant_type = ua.VariantType.Boolean if node_info["datatype"] == "Boolean" else ua.VariantType.Int32
            setattr(event.event, node_info["name"].capitalize(), ua.Variant(value, variant_type))

            # Print the update in the desired format
            print(f"Updated {node_info['name']} (ns={node_info['ns']}; i={node_info['i']}) to {value}")

    await event.trigger()

# Main server setup and scenario handling
async def main():

    """
    Main server setup and scenario handling function.

    Returns:
        None
    """
    
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/EULYNX")
    server.set_server_name("BL4R3 SDI OPC UA")

    await server.import_xml("eulynx.generic.bl4r3.rev01.xml")
    await server.import_xml("eulynx.manufacturer.example.bl4r3.rev01.xml")
    await server.import_xml("mdm.rev01.xml")

    point_turn_event_type_node = server.get_node("ns=2;i=1123")
    # Define S10 instance object 
    instance_objects = [server.get_node("ns=4;i=5057")]

    print("OPC UA Server is running...")

    # # Automatically play the default scenario at startup
    # print("Automatically playing the 'default' scenario...")
    # nodes = load_node_info("BL4R3-rev01-Diagnostic_NodeID_List-scenario.xlsx", sheet_name="default")
    # await update_data_access_view(server, nodes)
    # print("Default scenario completed. Waiting for scenario selection...")

    """
    ***TEMPORARY***
    Define the scenarios to run in sequence
    """
    scenarios = ["default", "1", "default", "2"]
    
    async with server:
        while True:
            """
             ***TEMPORARY***
             Loop scenario
            """
            for scenario_choice in scenarios:
                print(f"Playing scenario: {scenario_choice}")
                nodes = load_node_info("BL4R3-rev01-Diagnostic_NodeID_List-scenario.xlsx", sheet_name=scenario_choice)

                if scenario_choice == "default":
                    await update_data_access_view(server, nodes)
                else:
                    scenario_steps = load_scenario_steps("BL4R3-rev01-Diagnostic_NodeID_List-scenario.xlsx", sheet_name=scenario_choice)
                    for step_data in scenario_steps:
                        await update_data_access_view(server, nodes, step_data)
                        for instance in instance_objects:
                            await trigger_event(server, point_turn_event_type_node, instance, step_data, nodes)
                        await asyncio.sleep(5)
                print(f"Scenario {scenario_choice} completed.")
                await asyncio.sleep(5)

            print("Completed all scenarios, starting over...")
            
            
            # scenario_choice = await async_input("Enter scenario sheet name ('default', '1', '2', 'exit' to shut down): ")
            # if scenario_choice.lower() == "exit":
            #     print("Shutting down the server...")
            #     break
            # elif scenario_choice in ["default", "1", "2"]:
            #     print(f"Playing scenario: {scenario_choice}")
            #     nodes = load_node_info("BL4R3-rev01-Diagnostic_NodeID_List-scenario.xlsx", sheet_name=scenario_choice)

            #     if scenario_choice == "default":
            #         await update_data_access_view(server, nodes)
            #     else:
            #         scenario_steps = load_scenario_steps("BL4R3-rev01-Diagnostic_NodeID_List-scenario.xlsx", sheet_name=scenario_choice)
            #         for step_data in scenario_steps:
            #             await update_data_access_view(server, nodes, step_data)
            #             for instance in instance_objects:
            #                 await trigger_event(server, point_turn_event_type_node, instance, step_data, nodes)
            #             await asyncio.sleep(1)
            #     print(f"Scenario {scenario_choice} completed.")

            #     # Automatically run the default scenario after scenario 1 or 2
            #     if scenario_choice in ["1", "2"]:
            #         print("Running 'default' scenario after completing scenario:", scenario_choice)
            #         nodes = load_node_info("BL4R3-rev01-Diagnostic_NodeID_List-scenario.xlsx", sheet_name="default")
            #         await update_data_access_view(server, nodes)
            #         print("Default scenario completed.")
                    
            # else:
            #     print("Invalid choice. Please enter a valid scenario sheet name ('default', '1', '2', or 'exit').")

    # print("Server stopped.")
    # await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
