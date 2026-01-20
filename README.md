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

