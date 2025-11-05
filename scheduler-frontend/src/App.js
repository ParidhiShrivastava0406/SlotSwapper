import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const savedToken = localStorage.getItem("token");

  const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
    headers: {
      Authorization: `Bearer ${savedToken}`
    }
  });

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  const [loggedInUserId, setLoggedInUserId] = useState(localStorage.getItem("user_id") || null);
  const [token, setToken] = useState(savedToken || null);

  const [notifications, setNotifications] = useState([]);

  const [date, setDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");

  const [appointments, setAppointments] = useState([]);

  const [eventTitle, setEventTitle] = useState("");
  const [events, setEvents] = useState([]);
  const [swappableSlots, setSwappableSlots] = useState([]);

  const [selectedTheirSlotId, setSelectedTheirSlotId] = useState(null);
  const [mySwappableSlots, setMySwappableSlots] = useState([]);
  const [incoming, setIncoming] = useState([]);
  const [outgoing, setOutgoing] = useState([]);

  useEffect(() => {
  if (!token) return;

  const socket = new WebSocket("ws://127.0.0.1:8000/ws", ["Bearer", token]);

  socket.onmessage = (event) => {
    const message = event.data;
    setNotifications(prev => [...prev, message]);

    setTimeout(() => {
      setNotifications(prev => prev.slice(1));
    }, 5000);
  };

  socket.onclose = () => console.log("WebSocket closed");
  socket.onerror = (e) => console.log("WebSocket error", e);

  return () => socket.close();
}, [token]);


  const handleSignup = async () => {
    try {
      await axios.post("http://127.0.0.1:8000/signup/", null, { params: { name, email, password } });
      alert("Signup successful, now login");
    } catch {
      alert("Signup failed");
    }
  };

  const handleLogin = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/login/", null, { params: { email, password } });
      const { token, user_id } = response.data;
      localStorage.setItem("user_id", user_id);
      localStorage.setItem("token", token);
      setLoggedInUserId(user_id);
      window.location.reload();
    } catch {
      alert("Login failed");
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    window.location.reload();
  };


 

  const handleCreateEvent = async () => {
    try {
      await api.post("/events/", {
        title: eventTitle,
        start_time: `${date}T${startTime}:00`,
        end_time: `${date}T${endTime}:00`,
      });
      alert("Event Created");
    } catch {
      alert("Failed");
    }
  };

  const fetchEvents = async () => {
    const res = await api.get("/events/my");
    setEvents(res.data);
  };

  const makeSwappable = async (id) => {
    await api.patch(`/events/${id}/status`, { status: "SWAPPABLE" });
    fetchEvents();
  };

  const deleteEvent = async (id) => {
    if (!window.confirm("Are you sure you want to delete this event?")) return;
    try {
      await api.delete(`/events/${id}`);
      alert("Event deleted");
      fetchEvents();
    } catch (error) {
      alert("Error" + error.response?.data?.detail || "Failed to delete");
    }
  };

  const fetchSwappableSlots = async () => {
    const res = await api.get("/swappable-slots");
    setSwappableSlots(res.data);
  };

  const selectSwapTarget = async (slotId) => {
    setSelectedTheirSlotId(slotId);
    const res = await api.get("/events/my");
    setMySwappableSlots(res.data.filter(e => e.status === "SWAPPABLE"));
  };

  const sendSwapRequest = async (mySlotId) => {
    try {
      await api.post("/swap-request", null, { params: { my_slot_id: mySlotId, their_slot_id: selectedTheirSlotId } });
      alert("Swap Request Sent");
      setSelectedTheirSlotId(null);
      fetchEvents();
      fetchSwappableSlots();
    } catch {
      alert("Failed to send request");
    }
  };

  const loadRequests = async () => {
    const inc = await api.get("/swap-requests/incoming");
    const out = await api.get("/swap-requests/outgoing");
    setIncoming(inc.data);
    setOutgoing(out.data);
  };

  const respondSwap = async (requestId, accept) => {
    await api.post("/swap-response", null, { params: { request_id: requestId, accept } });
    alert(accept ? "Swap Accepted" : "Swap Rejected");
    loadRequests();
    fetchEvents();
    fetchSwappableSlots();
  };

  return (
    <div style={{ padding: 20 }}>

      {/*Notification Banner */}
      {notifications.length > 0 && (
        <div style={{ background: "#fff3cd", padding: 10, border: "1px solid #ffeeba", marginBottom: 20 }}>
          <strong> {notifications[0]}</strong>
        </div>
      )}

      {!loggedInUserId ? (
        <>
          <h2>Signup</h2>
          <input placeholder="Name" onChange={(e) => setName(e.target.value)} /><br /><br />
          <input placeholder="Email" onChange={(e) => setEmail(e.target.value)} /><br /><br />
          <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} /><br /><br />
          <button onClick={handleSignup}>Signup</button>

          <hr />

          <h2>Login</h2>
          <input placeholder="Email" onChange={(e) => setEmail(e.target.value)} /><br /><br />
          <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} /><br /><br />
          <button onClick={handleLogin}>Login</button>
        </>
      ) : (
        <>
          <h3>Logged in as User {loggedInUserId}</h3>
          <button onClick={handleLogout}>Logout</button>

          <hr />

          <h2>Create Event</h2>
          <input placeholder="Event Title" onChange={(e) => setEventTitle(e.target.value)} /><br /><br />
          <input type="date" onChange={(e) => setDate(e.target.value)} /><br /><br />
          <input type="time" onChange={(e) => setStartTime(e.target.value)} /><br /><br />
          <input type="time" onChange={(e) => setEndTime(e.target.value)} /><br /><br />
          <button onClick={handleCreateEvent}>Create Event</button>
          <button onClick={fetchEvents}>Load My Events</button>

          <table border="1" cellPadding="8" style={{ marginTop: 20 }}>
            <thead><tr><th>ID</th><th>Title</th><th>Status</th><th>Action</th></tr></thead>
            <tbody>
              {events.map(e => (
                <tr key={e.id}>
                  <td>{e.id}</td><td>{e.title}</td><td>{e.status}</td>
                  <td>
                    {e.status === "BUSY" && <button onClick={() => makeSwappable(e.id)}>Make Swappable</button>}
                    <button style={{ marginLeft: "10px", color: "red" }} onClick={() => deleteEvent(e.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <hr />

          <h2>Marketplace</h2>
          <button onClick={fetchSwappableSlots}>Refresh Marketplace</button>

          <table border="1" cellPadding="8" style={{ marginTop: 20 }}>
            <thead><tr><th>ID</th><th>User</th><th>Title</th><th>Start</th><th>End</th><th>Action</th></tr></thead>
            <tbody>
              {swappableSlots.map(s => (
                <tr key={s.id}>
                  <td>{s.id}</td><td>{s.user_id}</td><td>{s.title}</td><td>{s.start_time}</td><td>{s.end_time}</td>
                  <td><button onClick={() => selectSwapTarget(s.id)}>Request Swap</button></td>
                </tr>
              ))}
            </tbody>
          </table>

          <hr />

          <h2>Swap Requests</h2>
          <button onClick={loadRequests}>Load Requests</button>

          <h3>Incoming Requests</h3>
          <table border="1" cellPadding="8">
            <thead><tr><th>ID</th><th>My Slot</th><th>Their Slot</th><th>Action</th></tr></thead>
            <tbody>
              {incoming.map(r => (
                <tr key={r.id}>
                  <td>{r.id}</td><td>{r.their_slot_id}</td><td>{r.my_slot_id}</td>
                  <td>
                    <button onClick={() => respondSwap(r.id, true)}>Accept</button>
                    <button onClick={() => respondSwap(r.id, false)}>Reject</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <h3>Outgoing Requests</h3>
          <table border="1" cellPadding="8">
            <thead><tr><th>ID</th><th>Status</th></tr></thead>
            <tbody>
              {outgoing.map(r => (
                <tr key={r.id}><td>{r.id}</td><td>{r.status}</td></tr>
              ))}
            </tbody>
          </table>

          {selectedTheirSlotId && (
            <>
              <hr />
              <h3>Select your slot to swap:</h3>
              <table border="1" cellPadding="8">
                <thead><tr><th>ID</th><th>Title</th><th>Action</th></tr></thead>
                <tbody>
                  {mySwappableSlots.map(m => (
                    <tr key={m.id}>
                      <td>{m.id}</td><td>{m.title}</td>
                      <td><button onClick={() => sendSwapRequest(m.id)}>Swap This Slot</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <button onClick={() => setSelectedTheirSlotId(null)}>Cancel</button>
            </>
          )}
        </>
      )}
    </div>
  );
}

export default App;
