import { useState, useEffect } from 'react'

function App() {
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false); // Default to false
  const [users, setUsers] = useState([]);

  const [formData, setFormData] = useState({
    username: '',
    fname: '',
    lname: '',
    email: '',
    passwd: ''
  });

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_URL}/users`);
      if (!response.ok) throw new Error('Failed to fetch users');
      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    if (Object.values(formData).some(field => !field)) {
      return alert('All fields are required!');
    }

    try {
      const payload = {
        username: formData.username,
        fname: formData.fname,
        lname: formData.lname,
        email: formData.email,
        passwd: formData.passwd
      };

      const response = await fetch(`${API_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create user');
      }

      setFormData({ username: '', fname: '', lname: '', email: '', passwd: '' });
      fetchUsers();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDeleteUser = async (username) => {
    try {
      const response = await fetch(`${API_URL}/users/${username}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete user');
      }

      fetchUsers();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="app-layout">
      {/* HEADER */}
      <header className="app-header">
        <h1>Directory</h1>
        <p>Database Management Console</p>
      </header>

      {/* TWO COLUMN GRID CONTENT */}
      <div className="grid-container">
        
        {/* FORM PANEL */}
        <section className="panel-card">
          <h2 className="panel-title">Create Profile</h2>
          <form onSubmit={handleCreateUser} className="minimal-form">
            <input type="text" name="username" placeholder="Username ID" value={formData.username} onChange={handleInputChange} />
            <input type="text" name="fname" placeholder="First Name" value={formData.fname} onChange={handleInputChange} />
            <input type="text" name="lname" placeholder="Last Name" value={formData.lname} onChange={handleInputChange} />
            <input type="email" name="email" placeholder="Email Address" value={formData.email} onChange={handleInputChange} />
            <input type="password" name="passwd" placeholder="Account Password" value={formData.passwd} onChange={handleInputChange} />
            <button type="submit" className="btn btn-submit">Register</button>
          </form>
        </section>

        {/* LIST PANEL */}
        <section className="panel-card">
          <h2 className="panel-title">Active Registry</h2>
          
          {loading && <p className="status-msg">Syncing records...</p>}
          {error && <p className="status-msg error-msg">System Error: {error}</p>}
          {!loading && users.length === 0 && <p className="status-msg">No active profiles found.</p>}

          <ul className="user-list">
            {users.map((user) => (
              <li key={user._id} className="user-item">
                <div className="user-details">
                  <span className="user-fullname">{user.fname} {user.lname}</span>
                  <span className="user-subtext">@{user._id}</span>
                  <span className="user-subtext">{user.email}</span>
                </div>
                <button onClick={() => handleDeleteUser(user._id)} className="btn btn-delete">
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </section>

      </div>
    </div>
  );
}

export default App;