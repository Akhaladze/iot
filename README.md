
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



