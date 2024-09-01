
# OPC UA Client

This project provides an advanced OPC UA client that connects to one or more OPC UA servers, summarizes namespaces, subscribes to node changes, and logs events. It is designed to provide more insights than typical OPC UA client - COTS product such as UA Expert from UA Automation. (opc.tcp://localhost:4840/EULYNX)

## Features

- **Namespace Recognition and Summarization**: Automatically scans and summarizes identical or similar namespaces across connected OPC UA servers.
- **Subscription and Monitoring**: Monitors nodes for value changes and event triggers in real-time, providing detailed logs for further analysis.
- **Data Logging and Reporting**: Real-time logging of node data and event triggers, stored in a CSV file for easy reporting and analysis.
- **Interactive GUI**: A user-friendly GUI built with Tkinter to select scenarios, monitor nodes, and visualize logs.

## Installation

To set up the project, follow these steps:

### Clone the Repository

Start by cloning the repository to your local machine:

```bash
git clone https://github.com/loukjeab/EULYNX_SDI_OPC_UA_BL4R3.git
cd EULYNX_SDI_OPC_UA_BL4R3
```


### Build and Run with Docker

1. **Build the Docker Image** :

Navigate to the `Client` directory and build the Docker image:

```bash
docker build -t opcua-client .
```

2.  **Run the Docker Container** :

Run the Docker container using the built image: 

```bash
docker run -it opcua-client
```


### Deployment on Kubernetes

For deploying this client in a Kubernetes environment:

1. **Push Docker Image to Registry** :
   Tag and push your Docker image to the GitHub Container Registry:

```bash
docker tag opcua-client ghcr.io/loukjeab/opcua-client:latest
docker push ghcr.io/loukjeab/opcua-client:latest
```

2. **Create Kubernetes Deployment** :

Use the following Kubernetes deployment configuration to deploy the client:

```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opcua-client
  labels:
    app: opcua-client
spec:
  replicas: 1
  selector:
    matchLabels:
      app: opcua-client
  template:
    metadata:
      labels:
        app: opcua-client
    spec:
      containers:
      - name: opcua-client
        image: ghcr.io/loukjeab/opcua-client:latest
        env:
        - name: SERVER_URL
          value: "opc.tcp://opcua-server-service:4840"
```

3. **Apply the Deployment** :

```bash
kubectl apply -f client-deployment.yaml
```
