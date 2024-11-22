# OPC UA Diagnostics System Repository

This repository contains the implementation for a diagnostics system based on OPC UA. It is designed for efficient deployment, configuration, and automation, structured into five main directories to streamline real-time operations.

---

## Table of Contents
1. [Student Information](#student-information)
2. [Repository Structure](#repository-structure)
    - [`.github`](#1-github)
    - [`Client`](#2-client)
    - [`Kubernetes/opcua-server`](#3-kubernetesopcua-server)
    - [`Server`](#4-server)
    - [`Document`](#5-document)
3. [System Prerequisites](#system-prerequisites)
4. [Installation and Setup](#installation-and-setup)
5. [Configuration Details](#configuration-details)
    - [CI/CD Integration](#cicd-integration)
    - [Kubernetes & Helm](#kubernetes--helm)
    - [Docker](#docker)
6. [Appendix and References](#appendix-and-references)
7. [Future Outlook](#future-outlook)

---

## Student Information

- **Name:** Peeranut Noonurak  
- **Matriculation No.:** 7023582  
- **Course of Studies:** M.Eng. in Industrial Informatics  
- **Thesis Title:**  
  _Design and Implementation of Standard Diagnostics Interface for Railway Control-Command and Signalling: OPC UA Server Approach Based on EULYNX Field Elements_  
- **Supervisors:**
  - Academic Supervisor: Prof. Dr.-Ing. Armando Walter Colombo
  - First Industry Supervisor: Ralph R. Müller
  - Second Industry Supervisor: Ibtihel Cherif
  - Third Industry Supervisor: Prof. Dr. Karl-Albrecht Klinge  
- **Submission Date:** 29.11.2024  
---

## Repository Structure

### 1. `.github`
- **Purpose:** Contains configurations for the CI/CD pipeline integrated with GitHub Actions.
- **Key File:**
  - `ci-cd-pipeline.yml`: Automates testing, building, and deployment of the OPC UA diagnostics system.
  - **Pipeline stages include:**
    1. Building the Docker image.
    2. Pushing to the container registry.
    3. Deploying to a Kubernetes environment.

### 2. `Client`
- **Purpose:** Included for reference but not actively used in this implementation.
- **Key Files:**
  - `Advanced_Client.py`: A Python script for advanced client-side interaction (not actively used).
  - `BL4R3-rev01-Diagnostic_NodeID_List-scenario.xlsx`: An Excel file defining diagnostic scenarios.
  - `Dockerfile`: Contains instructions for building a client-side Docker container.
  - `opcua_data_log.csv`: A sample log for OPC UA client data.
  - `requirements.txt`: Lists Python dependencies for client interaction.

### 3. `Kubernetes/opcua-server`
- **Purpose:** Hosts Kubernetes configurations and Helm charts for deploying the OPC UA server.
- **Key Files:**
  - `Chart.yaml`: Metadata for the Helm chart.
  - `values.yaml`: Configuration values for parameterized deployments, such as replica count and update strategy.
  - Templates:
    - `deployment.yaml`: Configures the deployment of OPC UA server pods.
    - `service.yaml`: Configures the NodePort service for external access to the server.
    - `hpa.yaml`: Enables horizontal pod autoscaling (HPA) based on resource utilization.
    - `ingress.yaml`: Defines ingress rules for external HTTP/HTTPS access (if enabled).
    - `serviceaccount.yaml`: Configures service accounts for Kubernetes.
  - Tests:
    - `helpers.tpl`: A Helm helper template for testing and reusability in templates.
  - `.helmignore`: Excludes specific files from the Helm package.
  - `NOTES.txt`: Deployment notes and tips generated post-installation.

### 4. `Server`
- **Purpose:** Contains the source code, configuration files, and dependencies for the OPC UA server.
- **Key Files:**
  - `Dockerfile`: Steps to build the OPC UA server container.
  - `access_registry_docker.txt`: Credentials for Docker registry access.
  - `BL4R3-rev01-Diagnostic_NodeID_List-scenario.xlsx`: Excel file for diagnostic node scenarios.
  - XML Files:
    - `eulynx.generic.bl4r3.rev01.xml`: The generic namespace for the OPC UA Information Model.
    - `eulynx.manufacturer.example.bl4r3.rev01.xml`: A sample manufacturer-specific namespace.
    - `mdm.rev01.xml`: Defines the Maintenance Data Management (MDM) namespace. Represents the Maintenance Data Management (MDM) namespace. **This was added as part of additional implementation work for InnoTrans, building on top of the thesis requirements. It is not documented in the thesis report.**
  - `opcua_data_log.csv`: Example diagnostic data logs.
  - `server.py`: The main Python script implementing the OPC UA server.
  - `.gitignore`: Specifies files and directories to be ignored by version control.
  - `requirements.txt`: Lists Python dependencies for running the OPC UA server.

### 5. `Document`
- **Purpose:** Stores supporting documentation and supplementary materials.
- **Key Files:**
  - `MII_Master_Thesis_HSEL_DB_InfraGO_RevDraft.pdf`: Draft version of the master's thesis report.
  - `Supplymentary_EURAIL EULYNX Interface Specification SDI - List of Data Points.xlsx`: Supplementary documentation with data points for EULYNX SDI.


## System Prerequisites

To ensure consistent and functioning deployment of the OPC UA-based diagnostics system, several tools and components must be preinstalled and correctly configured. Below is an overview of the software, versions, and purposes of each component:

| **Component**             | **Version**     | **Purpose and Notes**                                                                                                        |
|----------------------------|-----------------|-----------------------------------------------------------------------------------------------------------------------------|
| Helm                      | 3.15.4         | Manages Kubernetes configuration and deployments, allowing templated and version-controlled setups for safe updates.         |
| Kubernetes (kubectl)      | 1.30.2         | Command-line client for managing Kubernetes clusters, nodes, services, updates, and monitoring.                              |
| Kustomize                 | 5.0.4          | Overlays configurations without touching base files, enabling resource customization for Kubernetes.                         |
| Visual Studio Code        | 1.94.2         | Recommended IDE for reading and editing code and configuration files. Integrated extensions improve the development process. |
| Docker                    | 27.1.1         | Used for containerizing the OPC UA server. Enables WSL 2 integration and Resource Saver for efficient operations.            |
| Ubuntu (WSL 2)            | 22.04          | A Docker-compatible Linux distribution running on Windows. Ensures compatibility with containerized environments locally.    |
| Python                    | 3.12           | Executes the OPC UA server script, supporting async libraries and data handling packages.                                    |
| UaModeler                 | 1.6.4 459      | An Information Model design tool for CCS system elements that structures diagnostic data.                                    |
| GitHub Container Registry | Required       | Stores Docker images with version control, ensuring easy access for Kubernetes deployments.                                  |

These tools and configurations form the foundational setup required to deploy the OPC UA-based diagnostics system. Ensuring compatibility and the correct versions will guarantee smooth integration and optimal performance.



## Installation and Setup

Follow these steps to install and deploy the OPC UA diagnostics system:

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/your-repo/OPCUA_Diagnostics.git
    cd OPCUA_Diagnostics
    ```

2. **Build the Docker Image:**
    ```bash 
    docker build -t opcua-server ./Server
    ```

3. **Tag and Push the Docker Image:**
   - **Tag the Image:**
    ```bash
    docker tag opcua-server ghcr.io/username/repository/server:v1
    ```
   - **Push the Image to the Registry:**
    ```bash
    docker login ghcr.io -u <username> -p <token>
    docker push ghcr.io/username/repository/server:v1
    ```

4. **Set Up Kubernetes Deployment:**
   - Navigate to the `Kubernetes/opcua-server` directory:
    ```bash
    cd Kubernetes/opcua-server
    ```
   - Install the Helm chart:
    ```bash
    helm upgrade --install opcua-server .
    ``` 

5. **Verify Deployment:**
   - Check the status of pods and services:
    ```bash
    kubectl get pods
    kubectl get svc
    ``` 
   - Test the connection using the `test-connection.yaml` file:
    ```bash
    kubectl apply -f templates/test-connection.yaml
    ``` 

6. **Access the System:**
   - The OPC UA server is accessible via the NodePort service within the local machine. External access is not enabled by default.

---

## Configuration Details

### CI/CD Integration
- The pipeline automates:
  1. Testing: Validates the functionality of the server.
  2. Building: Creates a containerized server image.
  3. Deployment: Pushes the server to a Kubernetes cluster.

### Kubernetes & Helm
- Uses Helm charts for scalable deployments.
- Includes configuration for:
  - Pod deployment.
  - Networking (NodePort services).
  - Resource management (HPA).

### Docker
- Builds a lightweight, containerized OPC UA server for seamless deployment.

---

## Future Outlook
- **External Access:** Currently, the server is accessible only within the local machine. Future work includes enabling external access via a LoadBalancer or cloud deployment.
- **Backup & Disaster Recovery:** Planning to implement and test backup strategies to enhance system resilience.

This repository provides a scalable and maintainable solution for managing diagnostics in railway control-command and signaling systems.
