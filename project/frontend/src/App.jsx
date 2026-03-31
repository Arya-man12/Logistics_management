import { useEffect, useState } from "react";

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "/api").replace(/\/$/, "");
const storageKey = "logistics-frontend-auth";

const initialAuth = loadStoredAuth();

const registerDefaults = {
  name: "",
  email: "",
  password: "",
  role: "customer",
  phone: "",
  address: "",
};

const loginDefaults = {
  email: "",
  password: "",
};

const shipmentDefaults = {
  source_address: "",
  destination_address: "",
  package_description: "",
  weight_kg: "",
  service_type: "standard",
  origin_hub_id: "",
  destination_hub_id: "",
};

const statusDefaults = {
  shipment_id: "",
  status: "in_transit",
  location: "",
  note: "",
};

const assignDefaults = {
  shipment_id: "",
  agent_id: "",
};

const hubDefaults = {
  name: "",
  code: "",
  address: "",
  city: "",
  state: "",
  country: "India",
  status: "active",
};

function loadStoredAuth() {
  if (typeof window === "undefined") {
    return { token: "", user: null };
  }

  try {
    const parsed = JSON.parse(window.localStorage.getItem(storageKey) || "null");
    if (parsed?.token) {
      return { token: parsed.token, user: parsed.user || null };
    }
  } catch (error) {
    console.warn("Could not read saved auth state", error);
  }

  return { token: "", user: null };
}

function App() {
  const [auth, setAuth] = useState(initialAuth);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [registerForm, setRegisterForm] = useState(registerDefaults);
  const [loginForm, setLoginForm] = useState(loginDefaults);
  const [shipmentForm, setShipmentForm] = useState(shipmentDefaults);
  const [trackingNumber, setTrackingNumber] = useState("");
  const [statusForm, setStatusForm] = useState(statusDefaults);
  const [assignForm, setAssignForm] = useState(assignDefaults);
  const [hubForm, setHubForm] = useState(hubDefaults);

  const [profile, setProfile] = useState(auth.user);
  const [shipments, setShipments] = useState([]);
  const [selectedShipment, setSelectedShipment] = useState(null);
  const [trackingEvents, setTrackingEvents] = useState([]);
  const [users, setUsers] = useState([]);
  const [hubs, setHubs] = useState([]);
  const [report, setReport] = useState(null);

  const currentRole = auth.user?.role || "";
  const selectedShipmentId = selectedShipment?.id || "";

  useEffect(() => {
    window.localStorage.setItem(storageKey, JSON.stringify(auth));
  }, [auth]);

  useEffect(() => {
    if (!auth.token) {
      return;
    }

    void loadProfile();
    void loadShipments();
    if (currentRole === "admin") {
      void loadAdminData();
    }
  }, [auth.token, currentRole]);

  useEffect(() => {
    if (!auth.token || !selectedShipmentId) {
      setTrackingEvents([]);
      return;
    }

    setStatusForm((current) => ({ ...current, shipment_id: selectedShipmentId }));
    setAssignForm((current) => ({
      ...current,
      shipment_id: selectedShipmentId,
      agent_id: current.agent_id || selectedShipment?.assigned_agent_id || "",
    }));
    void loadTrackingHistory(selectedShipmentId);
  }, [auth.token, selectedShipmentId, selectedShipment?.assigned_agent_id]);

  async function apiRequest(path, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };

    if (auth.token) {
      headers.Authorization = `Bearer ${auth.token}`;
    }

    const response = await fetch(`${apiBaseUrl}${path}`, {
      ...options,
      headers,
    });

    const text = await response.text();
    const data = text ? safeJsonParse(text) : null;

    if (!response.ok) {
      throw new Error(extractErrorMessage(data, response.status));
    }

    return data;
  }

  async function handleRegister(event) {
    event.preventDefault();
    await runAction(async () => {
      const response = await apiRequest("/auth/register", {
        method: "POST",
        body: JSON.stringify(withoutEmptyFields(registerForm)),
      });
      applyAuth(response);
      setRegisterForm(registerDefaults);
      setMessage("Registered");
    });
  }

  async function handleLogin(event) {
    event.preventDefault();
    await runAction(async () => {
      const response = await apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify(loginForm),
      });
      applyAuth(response);
      setLoginForm(loginDefaults);
      setMessage("Logged in");
    });
  }

  async function loadProfile() {
    await runAction(async () => {
      const response = await apiRequest("/auth/me");
      setProfile(response);
      setAuth((current) => ({ ...current, user: response }));
    }, { keepMessage: true });
  }

  async function loadShipments() {
    await runAction(async () => {
      const response = await apiRequest("/shipments");
      setShipments(response || []);
      setSelectedShipment((current) => pickShipment(current, response || []));
    }, { keepMessage: true });
  }

  async function loadTrackingHistory(shipmentId) {
    await runAction(async () => {
      const response = await apiRequest(`/tracking/shipment/${shipmentId}`);
      setTrackingEvents(response || []);
    }, { keepMessage: true });
  }

  async function loadAdminData() {
    await runAction(async () => {
      const [userResponse, hubResponse, reportResponse] = await Promise.all([
        apiRequest("/admin/users"),
        apiRequest("/hubs"),
        apiRequest("/admin/reports"),
      ]);

      setUsers(userResponse || []);
      setHubs(hubResponse || []);
      setReport(reportResponse || null);
    }, { keepMessage: true });
  }

  async function handleCreateShipment(event) {
    event.preventDefault();
    await runAction(async () => {
      const payload = {
        ...withoutEmptyFields(shipmentForm),
        weight_kg: Number(shipmentForm.weight_kg),
      };
      const response = await apiRequest("/shipments", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setShipmentForm(shipmentDefaults);
      setSelectedShipment(response);
      setTrackingNumber(response.tracking_number);
      await loadShipments();
      setMessage("Shipment created");
    });
  }

  async function handleTrackingLookup(event) {
    event.preventDefault();
    await runAction(async () => {
      const response = await apiRequest(`/shipments/${encodeURIComponent(trackingNumber)}`);
      setSelectedShipment(response);
      setMessage("Shipment found");
    });
  }

  async function handleStatusUpdate(event) {
    event.preventDefault();
    await runAction(async () => {
      const response = await apiRequest(`/shipments/${statusForm.shipment_id}/status`, {
        method: "PUT",
        body: JSON.stringify(withoutEmptyFields({
          status: statusForm.status,
          location: statusForm.location,
          note: statusForm.note,
        })),
      });
      setSelectedShipment(response);
      await loadShipments();
      await loadTrackingHistory(response.id);
      setStatusForm((current) => ({ ...current, location: "", note: "" }));
      setMessage("Status updated");
    });
  }

  async function handleAssignAgent(event) {
    event.preventDefault();
    await runAction(async () => {
      const response = await apiRequest(`/admin/shipments/${assignForm.shipment_id}/assign-agent`, {
        method: "PUT",
        body: JSON.stringify({ agent_id: assignForm.agent_id }),
      });
      setSelectedShipment(response);
      await loadShipments();
      await loadTrackingHistory(response.id);
      setMessage("Agent assigned");
    });
  }

  async function handleCreateHub(event) {
    event.preventDefault();
    await runAction(async () => {
      await apiRequest("/admin/hubs", {
        method: "POST",
        body: JSON.stringify(withoutEmptyFields(hubForm)),
      });
      setHubForm(hubDefaults);
      await loadAdminData();
      setMessage("Hub created");
    });
  }

  async function handleDeleteHub(hubId) {
    await runAction(async () => {
      await apiRequest(`/admin/hubs/${hubId}`, { method: "DELETE" });
      await loadAdminData();
      setMessage("Hub deleted");
    });
  }

  async function handleDeleteUser(userId) {
    await runAction(async () => {
      await apiRequest(`/admin/users/${userId}`, { method: "DELETE" });
      await loadAdminData();
      setMessage("User deleted");
    });
  }

  function applyAuth(response) {
    setAuth({
      token: response.access_token,
      user: response.user,
    });
    setProfile(response.user);
    setError("");
  }

  async function runAction(action, options = {}) {
    setLoading(true);
    if (!options.keepMessage) {
      setMessage("");
    }
    setError("");

    try {
      await action();
    } catch (actionError) {
      setError(actionError.message || "Request failed");
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    setAuth({ token: "", user: null });
    setProfile(null);
    setShipments([]);
    setSelectedShipment(null);
    setTrackingEvents([]);
    setUsers([]);
    setHubs([]);
    setReport(null);
    setTrackingNumber("");
    setStatusForm(statusDefaults);
    setAssignForm(assignDefaults);
    setHubForm(hubDefaults);
    setMessage("Logged out");
    setError("");
  }

  const agents = users.filter((user) => user.role === "agent");

  return (
    <div className="page">
      <h1>Logistics Platform</h1>
      <p>Customer, Delivery Agent, and Admin features only.</p>

      <div className="box">
        <p>Current role: {currentRole || "none"}</p>
        {message && <p>{message}</p>}
        {error && <p className="error">{error}</p>}
      </div>

      <div className="box">
        <h2>Login and Register</h2>
        <div className="buttons">
          <button disabled={!auth.token || loading} onClick={() => void loadProfile()} type="button">Load profile</button>
          <button disabled={!auth.token || loading} onClick={logout} type="button">Logout</button>
        </div>
        <form onSubmit={handleRegister} className="form">
          <h3>Register</h3>
          <input placeholder="Name" value={registerForm.name} onChange={(event) => updateForm(setRegisterForm, "name", event.target.value)} />
          <input placeholder="Email" value={registerForm.email} onChange={(event) => updateForm(setRegisterForm, "email", event.target.value)} />
          <input placeholder="Password" type="password" value={registerForm.password} onChange={(event) => updateForm(setRegisterForm, "password", event.target.value)} />
          <select value={registerForm.role} onChange={(event) => updateForm(setRegisterForm, "role", event.target.value)}>
            <option value="customer">customer</option>
            <option value="agent">agent</option>
            <option value="admin">admin</option>
          </select>
          <input placeholder="Phone" value={registerForm.phone} onChange={(event) => updateForm(setRegisterForm, "phone", event.target.value)} />
          <input placeholder="Address" value={registerForm.address} onChange={(event) => updateForm(setRegisterForm, "address", event.target.value)} />
          <button disabled={loading} type="submit">Register</button>
        </form>
        <form onSubmit={handleLogin} className="form">
          <h3>Login</h3>
          <input placeholder="Email" value={loginForm.email} onChange={(event) => updateForm(setLoginForm, "email", event.target.value)} />
          <input placeholder="Password" type="password" value={loginForm.password} onChange={(event) => updateForm(setLoginForm, "password", event.target.value)} />
          <button disabled={loading} type="submit">Login</button>
        </form>
        <pre>{formatJson(profile || {})}</pre>
      </div>

      <div className="box">
        <h2>Customer</h2>
        <p>Create shipments and track deliveries.</p>
        <form onSubmit={handleCreateShipment} className="form">
          <input placeholder="Source address" value={shipmentForm.source_address} onChange={(event) => updateForm(setShipmentForm, "source_address", event.target.value)} />
          <input placeholder="Destination address" value={shipmentForm.destination_address} onChange={(event) => updateForm(setShipmentForm, "destination_address", event.target.value)} />
          <input placeholder="Package description" value={shipmentForm.package_description} onChange={(event) => updateForm(setShipmentForm, "package_description", event.target.value)} />
          <input placeholder="Weight" value={shipmentForm.weight_kg} onChange={(event) => updateForm(setShipmentForm, "weight_kg", event.target.value)} />
          <input placeholder="Origin hub id" value={shipmentForm.origin_hub_id} onChange={(event) => updateForm(setShipmentForm, "origin_hub_id", event.target.value)} />
          <input placeholder="Destination hub id" value={shipmentForm.destination_hub_id} onChange={(event) => updateForm(setShipmentForm, "destination_hub_id", event.target.value)} />
          <select value={shipmentForm.service_type} onChange={(event) => updateForm(setShipmentForm, "service_type", event.target.value)}>
            <option value="standard">standard</option>
            <option value="express">express</option>
          </select>
          <button disabled={loading || !auth.token} type="submit">Create shipment</button>
        </form>

        <div className="buttons">
          <button disabled={!auth.token || loading} onClick={() => void loadShipments()} type="button">Load shipments</button>
        </div>
        <form onSubmit={handleTrackingLookup} className="form">
          <input placeholder="Tracking number" value={trackingNumber} onChange={(event) => setTrackingNumber(event.target.value)} />
          <button disabled={!auth.token || !trackingNumber || loading} type="submit">Track shipment</button>
        </form>
        <div className="simpleList">
          {shipments.map((shipment) => (
            <button
              key={shipment.id || shipment.tracking_number}
              type="button"
              className="shipmentButton"
              onClick={() => {
                setSelectedShipment(shipment);
                setTrackingNumber(shipment.tracking_number || "");
              }}
            >
              {shipment.tracking_number} - {shipment.status}
            </button>
          ))}
        </div>
        <pre>{formatJson(selectedShipment || {})}</pre>
        <pre>{formatJson(trackingEvents)}</pre>
      </div>

      <div className="box">
        <h2>Delivery Agent</h2>
        <p>Update shipment status.</p>
        <form onSubmit={handleStatusUpdate} className="form">
          <input placeholder="Shipment id" value={statusForm.shipment_id} onChange={(event) => updateForm(setStatusForm, "shipment_id", event.target.value)} />
          <select value={statusForm.status} onChange={(event) => updateForm(setStatusForm, "status", event.target.value)}>
            <option value="in_transit">in_transit</option>
            <option value="out_for_delivery">out_for_delivery</option>
            <option value="delivered">delivered</option>
            <option value="delayed">delayed</option>
          </select>
          <input placeholder="Location" value={statusForm.location} onChange={(event) => updateForm(setStatusForm, "location", event.target.value)} />
          <input placeholder="Note" value={statusForm.note} onChange={(event) => updateForm(setStatusForm, "note", event.target.value)} />
          <button disabled={loading || !auth.token || !statusForm.shipment_id} type="submit">Update status</button>
        </form>
      </div>

      <div className="box">
        <h2>Admin</h2>
        <p>Manage hubs, users, assign agents, and monitor the system.</p>

        <div className="buttons">
          <button disabled={!auth.token || loading} onClick={() => void loadAdminData()} type="button">Load admin data</button>
        </div>

        <form onSubmit={handleAssignAgent} className="form">
          <h3>Assign agent</h3>
          <input placeholder="Shipment id" value={assignForm.shipment_id} onChange={(event) => updateForm(setAssignForm, "shipment_id", event.target.value)} />
          <input placeholder="Agent id" value={assignForm.agent_id} onChange={(event) => updateForm(setAssignForm, "agent_id", event.target.value)} />
          <button disabled={loading || !auth.token || !assignForm.shipment_id || !assignForm.agent_id} type="submit">Assign agent</button>
        </form>

        <form onSubmit={handleCreateHub} className="form">
          <h3>Create hub</h3>
          <input placeholder="Name" value={hubForm.name} onChange={(event) => updateForm(setHubForm, "name", event.target.value)} />
          <input placeholder="Code" value={hubForm.code} onChange={(event) => updateForm(setHubForm, "code", event.target.value)} />
          <input placeholder="Address" value={hubForm.address} onChange={(event) => updateForm(setHubForm, "address", event.target.value)} />
          <input placeholder="City" value={hubForm.city} onChange={(event) => updateForm(setHubForm, "city", event.target.value)} />
          <input placeholder="State" value={hubForm.state} onChange={(event) => updateForm(setHubForm, "state", event.target.value)} />
          <input placeholder="Country" value={hubForm.country} onChange={(event) => updateForm(setHubForm, "country", event.target.value)} />
          <select value={hubForm.status} onChange={(event) => updateForm(setHubForm, "status", event.target.value)}>
            <option value="active">active</option>
            <option value="inactive">inactive</option>
          </select>
          <button disabled={loading || !auth.token} type="submit">Create hub</button>
        </form>

        <h3>Users</h3>
        <div className="simpleList">
          {users.map((user) => (
            <div key={user.id} className="itemRow">
              <span>{user.name} - {user.role}</span>
              <button disabled={loading || !auth.token} onClick={() => void handleDeleteUser(user.id)} type="button">Delete user</button>
            </div>
          ))}
        </div>

        <h3>Hubs</h3>
        <div className="simpleList">
          {hubs.map((hub) => (
            <div key={hub.id} className="itemRow">
              <span>{hub.name} - {hub.code}</span>
              <button disabled={loading || !auth.token} onClick={() => void handleDeleteHub(hub.id)} type="button">Delete hub</button>
            </div>
          ))}
        </div>

        <h3>Agents</h3>
        <pre>{formatJson(agents)}</pre>

        <h3>System report</h3>
        <pre>{formatJson(report || {})}</pre>
      </div>
    </div>
  );
}

function pickShipment(currentSelection, shipmentList) {
  if (!shipmentList.length) {
    return null;
  }

  if (!currentSelection?.id) {
    return shipmentList[0];
  }

  return shipmentList.find((shipment) => shipment.id === currentSelection.id) || shipmentList[0];
}

function updateForm(setter, key, value) {
  setter((current) => ({
    ...current,
    [key]: value,
  }));
}

function withoutEmptyFields(objectValue) {
  return Object.fromEntries(
    Object.entries(objectValue).filter(([, value]) => value !== "" && value !== null && value !== undefined),
  );
}

function formatJson(value) {
  return JSON.stringify(value, null, 2);
}

function safeJsonParse(value) {
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

function extractErrorMessage(data, status) {
  if (typeof data === "string" && data.trim()) {
    return data;
  }
  if (data?.detail) {
    return typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
  }
  if (data?.message) {
    return data.message;
  }
  return `Request failed with status ${status}`;
}

export default App;
