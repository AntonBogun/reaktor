import "./App.css";
import { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [data, setData] = useState([]);
  const [showTTL, setShowTTL] = useState(false);
  function getData() {
    axios.get("/api").then((response) => {
      setData(response.data);
    });
  }
  useEffect(() => {
    getData();
    setInterval(getData, 1000);
  }, []);

  return (
    <div className="App">
      Reakt(or) App <br />
      <button onClick={() => setShowTTL(!showTTL)}>{showTTL ? "Hide" : "Show"} TTL</button>
      <Pilots data={data} showTTL={showTTL} />
    </div>
  );
}

function Pilots({ data, showTTL }) {
  return (
    <div style={{ overflow: "auto" }}>
      {data.map((pilot, index) => (
        <Pilot key={index} pilot={pilot} showTTL={showTTL} />
      ))}
    </div>
  );
}

function Pilot({ pilot, showTTL }) {
  function format_number(number) {
    return Number.parseFloat(number.toFixed(2));
  }
  return (
    <div style={{ border: "1px solid black", margin: "10px" }}>
      <ul>
        <li>First Name: {pilot.firstName}</li>
        <li>Last Name: {pilot.lastName}</li>
        <li>Email: {pilot.email}</li>
        <li>Phone: {pilot.phone}</li>
        <li>Closest Approach: {format_number(pilot.closest_dist / 1000)}m</li>
        {showTTL ? <li>TTL: {format_number((pilot.TTL - new Date().getTime()) / 1000)}s</li> : null}
      </ul>
    </div>
  );
}

export default App;
