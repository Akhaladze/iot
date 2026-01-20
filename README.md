## High level diagram (data source segmentation)

### - network infrastructure with entry level information (i.e. internet connection, ip addresse, device name, etc)
### - IoT devices provide power control information, user activities, energy consumption and user real time events
### - Security device provides foto/video content, AI models metadata (human and vichle activities detection events, initial recognition of objects, and real time metadata)
### - Smart home/office datacenter provice journals and metrics data.



```mermaid
---
config:
  theme: base
  themeVariables:
    fontSize: 24px
  layout: dagre
  look: handDrawn
---
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '22px'}}}%%
flowchart TB
 subgraph subGraph2["Wireless Access"]
        AP1["WiFi AP1<br>hAP ax^2"]
        AP2["WiFi AP2<br>L22UGS-5HaxD2HaxD"]
  end
 subgraph subGraph3["Kubernetes Cluster (k3s)"]
        Master["Master Node<br>Intel Core i7 16Gb"]
  end
 subgraph subGraph4["Internal Network"]
        FW["Main Firewall<br>Mikrotik RB4011"]
        SW["Cloud Switch<br>Mikrotik 610-8P-2S+OUT"]
        subGraph2
        subGraph3
  end
 subgraph s1["Security"]
        n1["Camera 1<br>HikVision DS-2CD1043G2"]
        n2["Camera 2<br>HikVision DS-2CD1043G2"]
        Lock["Door Lock"]
  end
 subgraph s3["IoT Power & Control"]
        n6["Shelly Pro 4PM"]
        n7["Shelly Pro 2PM"]
        n8["Shelly Devices<br>Uni, Switch25, Plug, Vintage, Bulb, 1PM"]
        n9["Sensors<br>Temp, Humidity, Motion"]
  end
    FW --> SW
    SW --> Master

    AP1@{ shape: rect}
    AP2@{ shape: rect}
    Master@{ shape: rect}
    FW@{ shape: rect}
    SW@{ shape: rect}
    subGraph2@{ shape: rect}
    subGraph3@{ shape: rect}
    n1@{ shape: rect}
    n2@{ shape: rect}
    Lock@{ shape: rect}
    n6@{ shape: rect}
    n7@{ shape: rect}
    n8@{ shape: rect}
    n9@{ shape: rect}
    subGraph4@{ shape: rect}
    s3@{ shape: rect}
    s1@{ shape: rect}
     AP1:::network
     AP2:::network
     Master:::server
     FW:::network
     SW:::network
     n1:::device
     n2:::device
     Lock:::device
     n6:::device
     n7:::device
     n8:::device
     n9:::device
    classDef network fill:#f9f,stroke:#333,stroke-width:2px
    classDef device fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef power fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    classDef server fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

## Detailed schema

```mermaid

%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '22px'}}}%%
graph TD
    %% Styles
    classDef network fill:#f9f,stroke:#333,stroke-width:2px;
    classDef device fill:#e1f5fe,stroke:#0277bd,stroke-width:2px;
    classDef power fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef server fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;

    subgraph Internet
        ISP[ISP 1 Main]:::network
    end

    subgraph "Internal Network"
        FW[Main Firewall<br/>Mikrotik RB4011]:::network
        SW[Cloud Switch<br/>Mikrotik 610-8P-2S+OUT]:::network
        
        subgraph "Wired Devices"
            Cam1[Camera 1<br/>HikVision DS-2CD1043G2]:::device
            Cam2[Camera 2<br/>HikVision DS-2CD1043G2]:::device
        end

        subgraph "Wireless Access"
            AP1[WiFi AP1<br/>hAP ax^2]:::network
            AP2[WiFi AP2<br/>L22UGS-5HaxD2HaxD]:::network
        end
        
        subgraph "Kubernetes Cluster (k3s)"
            Master[Master Node<br/>Intel Core i7 16Gb]:::server
            Node1[Node 1<br/>RPi 5 4GB]:::server
            Node2[Node 2<br/>RPi 5 4GB]:::server
        end
    end

    subgraph "Wireless Clients"
        subgraph "IoT Power & Control"
            ShellyPro4[Shelly Pro 4PM]:::device
            ShellyPro2[Shelly Pro 2PM]:::device
            ShellyMisc[Shelly Devices<br/>Uni, Switch25, Plug, Vintage, Bulb, 1PM]:::device
        end

        subgraph "Sensors & Security"
            Sensors[Sensors<br/>Temp, Humidity, Motion]:::device
            Lock[Door Lock]:::device
        end
        
        subgraph "User Devices"
            Users[Laptops, Phones]:::device
            Media[LED Panels, TV Boxes]:::device
        end
    end

    subgraph "Autonomous Power System"
        Inverter[Hybrid Inverter<br/>PowMR 6.5 kW]:::power
        PV[PV 5kWt]:::power
        Bat[Battery 5kWt]:::power
        Gen[Generator 5.5kWt]:::power
    end

    %% Connections
    ISP --> FW
    FW --> SW
    SW -->|PoE| Cam1
    SW -->|PoE| Cam2
    SW -->|PoE| AP1
    SW -->|PoE| AP2
    SW --> Master
    SW --> Node1
    SW --> Node2

    %% Wireless Links
    AP1 -.-> ShellyPro4
    AP1 -.-> ShellyPro2
    AP1 -.-> ShellyMisc
    AP1 -.-> Sensors
    AP1 -.-> Lock
    AP1 -.-> Users
    AP1 -.-> Media
    AP1 -.-> Inverter

    AP2 -.-> ShellyPro4
    AP2 -.-> ShellyPro2
    AP2 -.-> ShellyMisc
    AP2 -.-> Sensors
    AP2 -.-> Lock
    AP2 -.-> Users
    AP2 -.-> Media
    AP2 -.-> Inverter

    %% Power System Logic
    PV --> Inverter
    Bat <--> Inverter
    Gen --> Inverter
    Inverter -.->|Power Supply| ShellyPro4
    Inverter -.->|Power Supply| ShellyPro2
```

## Data Processing & Analytics Pipeline

We employ a hybrid data collection strategy to handle the diverse nature of our IoT and network devices, ensuring both historical depth and real-time responsiveness.

### 1. Data Collection Strategy

The system distinguishes between data that needs to be actively polled and real-time events pushed by devices.

*   **Periodic Polling (Pull):** Used for stateful information and devices without push capabilities.
    *   *Example:* Polling Mikrotik for active DHCP leases to maintain a device inventory.
*   **Event-Driven (Push):** Used for real-time telemetry and alerts.
    *   *Example:* MQTT messages from Shelly sensors (power, temperature) or HikVision camera motion alerts.

### 2. Service Integration

We are building specialized services for data ingestion and enrichment:

*   **`services/mikrotik`:** (Active) Connects to the Mikrotik REST API to fetch DHCP leases. This data is used to resolve device MAC addresses to hostnames and IP addresses, acting as the foundation for our **Device Inventory**.
*   **Future Services:**
    *   **`hik-vision`:** For retrieving camera status and snapshots.
    *   **`weather`:** External weather API integration for correlation with internal sensors.
    *   **`geoip`:** For analyzing external traffic sources.
    *   **`cloud-screenshot-analysis`:** Triggered by motion events; uploads camera snapshots to a cloud AI service for object detection/classification.

### 3. Analytics Workflow

Our data pipeline transforms raw signals into actionable insights:

1.  **Ingestion:** Data is collected via Services (API) or MQTT Brokers.
2.  **Raw Storage:** All incoming data is first saved as **Parquet** files for efficient columnar storage and history preservation.
3.  **Manual Analytics:** Data scientists/engineers can directly query Parquet files for ad-hoc analysis.
4.  **Transformation (DBT):** We use **DBT (Data Build Tool)** to define SQL models. These models clean, deduplicate, and aggregate the raw data.
    *   *Specific Use Case:* Creating the `Inventory` table by combining Mikrotik DHCP data with static device metadata.
5.  **Data Warehouse (DuckDB):** The processed models are loaded into **DuckDB** for high-performance analytical querying and dashboarding.

### 4. Architecture Diagrams

#### High-Level Data Flow

```mermaid
flowchart LR
    subgraph Sources
        Mikrotik[Mikrotik Router]
        Hik[HikVision Cameras]
        Sensors[Shelly Sensors]
        Ext[External APIs]
    end

    subgraph Ingestion
        Poller[Polling Services]
        MQTT[MQTT Broker]
    end

    subgraph Storage_Processing
        Parquet[(Raw Parquet Files)]
        DBT[DBT Transformation]
        DuckDB[(DuckDB Analytics)]
    end

    Mikrotik -->|REST API| Poller
    Ext -->|API| Poller
    Hik -->|Events| MQTT
    Sensors -->|Telemetry| MQTT

    Poller --> Parquet
    MQTT --> Parquet

    Parquet --> DBT
    DBT --> DuckDB
```

#### Detailed Processing Logic

```mermaid
sequenceDiagram
    participant Dev as IoT/Net Device
    participant Svc as Collector Service
    participant RAW as Parquet Storage
    participant DBT as DBT Models
    participant WH as DuckDB

    Note over Dev, Svc: Periodic Data (e.g. DHCP)
    Svc->>Dev: Poll Data (GET /rest/...)
    Dev-->>Svc: JSON Response
    Svc->>RAW: Write Timestamped Parquet

    Note over Dev, Svc: Event Data (e.g. Motion)
    Dev->>Svc: Publish MQTT Message
    Svc->>RAW: Append to Event Log (Parquet)

    Note over RAW, WH: Batch Processing
    RAW->>DBT: Read Raw Data
    DBT->>DBT: Apply SQL Models (Clean/Join)
    DBT->>WH: Materialize Tables/Views (e.g. Inventory)
```

### 5. Step-by-Step Implementation Example

This outlines the practical execution flow for our core use case—managing device inventory and collecting power metrics.

1.  **Fetch Device Data (Source):** The `mikrotik` service queries the router's DHCP server to get a list of all currently assigned IP addresses and associated MAC addresses.
2.  **Build Inventory (Transformation):** We create an `inventory` table. This is done by joining the live DHCP data with a static `device_metadata.csv` seed file (containing owner, location, device type). This gives us a trusted list of *what* is on the network.
3.  **Targeted Polling (Enrichment):** The system uses the `inventory` table to identify active Shelly devices. It then specifically polls these IP addresses to get detailed status (power usage, temperature, relay state).
4.  **Persist Data (Storage):** The results of these polls are immediately written to local disk as time-partitioned **Parquet** files (e.g., `data/shelly_raw.parquet`).
5.  **Analytics (Aggregation):** Finally, DBT runs scheduled transformations to read the Parquet files, aggregate the metrics (e.g., "Daily Power Consumption by Room"), and load the clean results into **DuckDB** for visualization.