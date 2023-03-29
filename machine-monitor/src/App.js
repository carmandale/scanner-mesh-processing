import React, { useEffect, useState } from 'react';
import './App.css';

export function App() {
  const [machines, setMachines] = useState({});

  useEffect(() => {
    fetchMachines();
  }, []);

  const fetchMachineIPs = async () => {
    try {
      const response = await fetch("/machine_ip.txt");
      const ipsText = await response.text();
      const ips = ipsText.trim().split("\n");
      return ips;
    } catch (error) {
      console.error("Error fetching machine IPs:", error);
      return [];
    }
  };
  
  
  const fetchMachines = async () => {
    try {
      const machineIPs = await fetchMachineIPs();
      console.log("Fetched IPs:", machineIPs); // Debug output
  
      const machinesData = [];
  
      for (const ip of machineIPs) {
        const response = await fetch(`http://${ip}:5001/api/check_machines`);
        const data = await response.json();
        machinesData.push(data);
      }
  
      console.log("Fetched machines:", machinesData); // Debug output
      setMachines(machinesData);
    } catch (error) {
      console.error("Error fetching machines:", error);
    }
  };
  
  
  

  return (
    <div className="App">
      <h1>Machine Monitor</h1>
      <button onClick={fetchMachines}>Refresh</button>
      {machines.hostname && (
        <div>
          <h2>
            {machines.hostname} ({machines.ip_address})
          </h2>
          <div>
            <strong>scan_db running:</strong>{" "}
            <span
              style={{
                display: "inline-block",
                width: "12px",
                height: "12px",
                borderRadius: "50%",
                backgroundColor: machines.running_processes.scan_db ? "green" : "red",
              }}
            ></span>
          </div>
          <div>
            <strong>blender running:</strong>{" "}
            <span
              style={{
                display: "inline-block",
                width: "12px",
                height: "12px",
                borderRadius: "50%",
                backgroundColor: machines.running_processes.blender ? "green" : "red",
              }}
            ></span>
          </div>
          <div>
            <strong>scan ID:</strong> {machines.running_processes.scan_id || "Not available"}
          </div>
        </div>
      )}
    </div>
  );
    
}
