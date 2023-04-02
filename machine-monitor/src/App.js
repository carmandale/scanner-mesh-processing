import React, { useEffect, useState } from 'react';
import './App.css';
import { BounceLoader } from "react-spinners";

export function App() {
  const [machines, setMachines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedMachine, setSelectedMachine] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const handleShowOutput = async (ip) => {
    setSelectedMachine(ip);
    const output = await fetchScanDbOutput(ip);
    alert(output); // Display the output in an alert box, or use a modal to show the output
  };

  useEffect(() => {
    fetchMachines();

    // Set up polling to fetch machines data every 30 seconds (adjust interval as needed)
    const interval = setInterval(fetchMachines, 5000);

    // Clean up the interval when the component is unmounted
    return () => clearInterval(interval);
  }, []);

  // useEffect(() => {
  //   console.log("Machines state:", machines);
  // }, [machines]);

  // Update lastUpdated state when new data is fetched
  useEffect(() => {
    if (machines.length > 0) {
      setLastUpdated(new Date());
    }
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
    setLoading(true); // Set loading state to true before fetching data
    try {
      const machineIPs = await fetchMachineIPs();
      console.log("Fetched IPs:", machineIPs); // Debug output

      const machineDataPromises = machineIPs.map(async (ip) => {
        try {
          // Add a timestamp to the API request URL
          const timestamp = Date.now();
          const response = await fetch(
            `http://${ip}:5001/api/check_machines?_=${timestamp}`,
            {
              headers: {
                "Cache-Control": "no-cache",
              },
            }
          );
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

  const fetchScanDbOutput = async (ip) => {
    try {
      const timestamp = Date.now();
      const response = await fetch(
        `http://${ip}:5001/api/scan_db_output?_=${timestamp}`
      );
      const data = await response.json();
      return data.output;
    } catch (error) {
      console.error(`Error fetching machine data for IP ${ip}:`, error);
      return null;
    } finally {
      setLoading(false); // Set loading state to false after data is fetched, regardless of success or failure
    }
  };

  return (
    <div className="App">
      <h1>Groove Jones XR Scanner Machine Monitor</h1>
      <button onClick={fetchMachines}>Refresh</button>
      {lastUpdated && <p>Last updated: {lastUpdated.toLocaleString()}</p>}
      <div className="spinner-container">
        <BounceLoader color={"#123abc"} loading={loading} size={30} />
      </div>
      <div className="machine-list">
        <ul className="no-bullets">
          {machines
            .filter((machine) => machine !== null)
            .map((machine, index) => (
              <li
                key={index}
                onClick={() => handleShowOutput(machine.ip_address)}
                style={{ cursor: "pointer" }}
              >
                <h2 className="machine-name">
                  {machine.hostname} ({machine.ip_address})
                </h2>
                <ul className="no-bullets">
                  <li>
                    <strong>Blender:</strong>{" "}
                    {machine.running_processes.blender ? (
                      <span style={{ color: "green" }}>
                        Running (Scan ID: {machine.running_processes.scan_id})
                      </span>
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
                    <strong>Groove Mesher:</strong>{" "}
                    {machine.running_processes.groove_mesher ? (
                      <span style={{ color: "green" }}>
                        Running (Scan ID: {machine.running_processes.scan_id})
                      </span>
                    ) : (
                      <span style={{ color: "red" }}>Not Running</span>
                    )}
                  </li>
                </ul>
              </li>
            ))}
        </ul>
      </div>
    </div>
  );
}  









