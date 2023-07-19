import React, { useEffect, useState } from 'react';
import './App.css';

export function App() {
  const [machines, setMachines] = useState([]);

  useEffect(() => {
    fetchMachines();
  }, []);

  useEffect(() => {
    console.log("Machines state:", machines);
  }, [machines]);
  

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
  
      const machineDataPromises = machineIPs.map(async (ip) => {
        try {
          const response = await fetch(`http://${ip}:5001/api/check_machines`);
          const data = await response.json();
          return data;
        } catch (error) {
          console.error(`Error fetching machine data for IP ${ip}:`, error);
          return null;
        }
      });
  
      const machinesData = await Promise.allSettled(machineDataPromises);
      const filteredMachinesData = machinesData
        .filter((result) => result.status === "fulfilled")
        .map((result) => result.value);
  
      console.log("Fetched machines:", filteredMachinesData); // Debug output
      setMachines(filteredMachinesData);
    } catch (error) {
      console.error("Error fetching machines:", error);
    }
  };
  

  return (
    <div className="App">
      <h1>Machine Monitor</h1>
      <button onClick={fetchMachines}>Refresh</button>
      <ul>
        {machines.map((machine, index) => (
          <li key={index}>
            <h2>{machine.hostname} ({machine.ip_address})</h2>
            <ul>
              <li>
                <strong>Blender:</strong>{" "}
                {machine.running_processes.blender ? (
                  <span style={{ color: "green" }}>Running</span>
                ) : (
                  <span style={{ color: "red" }}>Not Running</span>
                )}
              </li>
              <li>
                <strong>Scan DB:</strong>{" "}
                {machine.running_processes.scan_db ? (
                  <span style={{ color: "green" }}>Running</span>
                ) : (
                  <span style={{ color: "red" }}>Not Running</span>
                )}
              </li>
              <li>
                <strong>Scan ID:</strong> {machine.running_processes.scan_id || "N/A"}
              </li>
            </ul>
          </li>
        ))}
      </ul>
    </div>
  );
}
