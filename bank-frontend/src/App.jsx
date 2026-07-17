import { useState, useEffect } from 'react'

function App() {
  // Directory States
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    fname: '',
    lname: '',
    email: '',
    passwd: ''
  });

  // Banking States
  const [selectedUser, setSelectedUser] = useState(null);
  const [userAccounts, setUserAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [accountType, setAccountType] = useState('checking');
  const [txAmount, setTxAmount] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // --- Core Profile Methods ---
  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_URL}/api/users`);
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
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    if (Object.values(formData).some(field => !field)) {
      return alert('All fields are required!');
    }

    try {
      const response = await fetch(`${API_URL}/api/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.username,
          fname: formData.fname,
          lname: formData.lname,
          email: formData.email,
          passwd: formData.passwd
        }),
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
      const response = await fetch(`${API_URL}/api/users/${username}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete user');
      }
      
      if (selectedUser === username) {
        setSelectedUser(null);
        setUserAccounts([]);
        setSelectedAccount(null);
        setTransactions([]);
      }

      fetchUsers();
    } catch (err) {
      alert(err.message);
    }
  };

  // --- Core Banking Methods ---
  const handleSelectUser = async (username) => {
    setSelectedUser(username);
    setSelectedAccount(null);
    setTransactions([]);
    await fetchUserAccounts(username);
  };

  const fetchUserAccounts = async (username) => {
    try {
      // Hits the new prefix-safe filter endpoint on the backend
      const response = await fetch(`${API_URL}/bank/account?owner_id=${username}`);
      if (!response.ok) throw new Error('Failed to load user accounts');
      
      const data = await response.json();
      setUserAccounts(data); 
    } catch (err) {
      console.error(err);
      setUserAccounts([]);
    }
  };

  const handleCreateAccount = async () => {
    if (!selectedUser) return;
    try {
      const response = await fetch(`${API_URL}/bank/account?owner_id=${selectedUser}&account_type=${accountType}`, {
        method: 'POST'
      });
      if (!response.ok) throw new Error('Failed to create bank account');
      
      alert('Account Created Successfully!');
      // Refresh user account dashboard
      await fetchUserAccounts(selectedUser);
    } catch (err) {
      alert(err.message);
    }
  };

  const handleSelectAccount = async (account) => {
    setSelectedAccount(account);
    await fetchTransactions(account._id);
  };

  const fetchTransactions = async (accountId) => {
    try {
      const response = await fetch(`${API_URL}/bank/account/${accountId}/transactions`);
      if (!response.ok) throw new Error('Failed to load ledger records');
      const data = await response.json();
      setTransactions(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleTransaction = async (actionType) => {
    if (!selectedAccount || !txAmount || parseFloat(txAmount) <= 0) {
      return alert('Please enter a valid positive amount.');
    }

    try {
      const response = await fetch(`${API_URL}/bank/account/${selectedAccount._id}/${actionType}?amount=${txAmount}`, {
        method: 'POST'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Transaction failed`);
      }

      setTxAmount('');
      alert('Transaction Successful!');
      
      // Refresh current account details, balance, and ledger history
      const updatedAccRes = await fetch(`${API_URL}/bank/account/${selectedAccount._id}`);
      const updatedAcc = await updatedAccRes.json();
      setSelectedAccount(updatedAcc);
      
      // Update the account list array in the background so balances match at a glance
      await fetchUserAccounts(selectedUser);
      await fetchTransactions(selectedAccount._id);
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="app-layout" style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif' }}>
      <header className="app-header" style={{ borderBottom: '2px solid #eaeaea', paddingBottom: '10px', marginBottom: '20px' }}>
        <h1>Central Operations</h1>
        <p>Unified User Directory & Banking Ledger Console</p>
      </header>

      <div className="grid-container" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        
        {/* LEFT COLUMN: USER MANAGEMENT */}
        <div className="sub-column" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <section className="panel-card" style={{ border: '1px solid #ccc', padding: '20px', borderRadius: '4px' }}>
            <h2 className="panel-title" style={{ marginTop: 0 }}>Create Profile</h2>
            <form onSubmit={handleCreateUser} className="minimal-form" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <input type="text" name="username" placeholder="Username ID" value={formData.username} onChange={handleInputChange} style={{ padding: '8px' }} />
              <input type="text" name="fname" placeholder="First Name" value={formData.fname} onChange={handleInputChange} style={{ padding: '8px' }} />
              <input type="text" name="lname" placeholder="Last Name" value={formData.lname} onChange={handleInputChange} style={{ padding: '8px' }} />
              <input type="email" name="email" placeholder="Email Address" value={formData.email} onChange={handleInputChange} style={{ padding: '8px' }} />
              <input type="password" name="passwd" placeholder="Account Password" value={formData.passwd} onChange={handleInputChange} style={{ padding: '8px' }} />
              <button type="submit" className="btn btn-submit" style={{ padding: '10px', cursor: 'pointer', background: '#0056b3', color: 'white', border: 'none', borderRadius: '4px' }}>Register User</button>
            </form>
          </section>

          <section className="panel-card" style={{ border: '1px solid #ccc', padding: '20px', borderRadius: '4px' }}>
            <h2 className="panel-title" style={{ marginTop: 0 }}>Active Registry</h2>
            {loading && <p className="status-msg">Syncing records...</p>}
            {error && <p className="status-msg error-msg" style={{ color: 'red' }}>System Error: {error}</p>}
            
            <ul className="user-list" style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {users.map((user) => (
                <li key={user._id} className={`user-item ${selectedUser === user._id ? 'selected' : ''}`} 
                    style={{ border: '1px solid #ccc', padding: '12px', marginBottom: '10px', borderRadius: '4px', cursor: 'pointer', background: selectedUser === user._id ? '#f0f4f8' : 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                    onClick={() => handleSelectUser(user._id)}>
                  <div className="user-details">
                    <strong className="user-fullname">{user.fname} {user.lname}</strong>
                    <div className="user-subtext" style={{ fontSize: '0.85em', color: '#666' }}>@{user._id} | {user.email}</div>
                  </div>
                  <div>
                    <button onClick={(e) => { e.stopPropagation(); handleDeleteUser(user._id); }} className="btn btn-delete" style={{ padding: '6px 12px', background: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                      Remove
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        </div>

        {/* RIGHT COLUMN: BANKING CORE */}
        <div className="sub-column">
          <section className="panel-card" style={{ border: '1px solid #ccc', padding: '20px', borderRadius: '4px', minHeight: '100%' }}>
            <h2 className="panel-title" style={{ marginTop: 0 }}>Financial Control Panel</h2>
            
            {!selectedUser ? (
              <p className="status-msg" style={{ color: '#666' }}>Select a profile from the registry to manage financial accounts.</p>
            ) : (
              <div>
                <h3 style={{ margin: '0 0 15px 0' }}>Managing: @{selectedUser}</h3>
                
                {/* Account Creator Section */}
                <div style={{ background: '#f9f9f9', padding: '15px', borderRadius: '4px', marginBottom: '20px', border: '1px solid #eee' }}>
                  <h4 style={{ margin: '0 0 10px 0' }}>Open New Vault Account</h4>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <select value={accountType} onChange={(e) => setAccountType(e.target.value)} style={{ flex: 1, padding: '8px' }}>
                      <option value="checking">Checking Account</option>
                      <option value="savings">Savings Account</option>
                    </select>
                    <button onClick={handleCreateAccount} className="btn btn-submit" style={{ padding: '8px 16px', background: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                      Provision
                    </button>
                  </div>
                </div>

                {/* Account Selector (Dynamically Rendered List) */}
                <div style={{ marginBottom: '25px' }}>
                  <h4 style={{ margin: '0 0 10px 0' }}>Select Active Account</h4>
                  {userAccounts.length === 0 ? (
                    <p style={{ fontSize: '0.9em', color: '#888', fontStyle: 'italic' }}>No open vault accounts found for this user profile.</p>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                      {userAccounts.map((acc) => (
                        <div 
                          key={acc._id} 
                          onClick={() => handleSelectAccount(acc)}
                          style={{
                            padding: '12px',
                            border: selectedAccount?._id === acc._id ? '2px solid #28a745' : '1px solid #ccc',
                            background: selectedAccount?._id === acc._id ? '#eaf4ea' : '#fff',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                            <strong style={{ color: '#333' }}>{acc.account_type.toUpperCase()}</strong> 
                            <span style={{ fontSize: '0.8em', color: '#777' }}>ID: {acc._id}</span>
                          </div>
                          <div style={{ fontSize: '1.2em', fontWeight: 'bold', color: '#2e7d32' }}>
                            ${parseFloat(acc.balance).toFixed(2)}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Transaction and History Desk */}
                {selectedAccount && (
                  <div style={{ borderTop: '2px solid #eaeaea', paddingTop: '20px' }}>
                    <div style={{ background: '#eaf4ea', padding: '15px', borderRadius: '4px', marginBottom: '20px', border: '1px solid #c3e6cb' }}>
                      <strong>Active Target:</strong> {selectedAccount.account_type.toUpperCase()} Account ({selectedAccount._id})<br/>
                      <strong>Current Balance:</strong> ${parseFloat(selectedAccount.balance).toFixed(2)}
                    </div>

                    {/* Transaction Desk */}
                    <div style={{ marginBottom: '25px' }}>
                      <h4 style={{ margin: '0 0 10px 0' }}>Transaction Desk</h4>
                      <input 
                        type="number" 
                        placeholder="Transaction Amount ($)" 
                        value={txAmount} 
                        onChange={(e) => setTxAmount(e.target.value)}
                        style={{ width: '100%', padding: '10px', marginBottom: '10px', boxSizing: 'border-box', borderRadius: '4px', border: '1px solid #ccc' }} 
                      />
                      <div style={{ display: 'flex', gap: '10px' }}>
                        <button onClick={() => handleTransaction('deposit')} style={{ flex: 1, padding: '10px', background: '#2e7d32', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Deposit</button>
                        <button onClick={() => handleTransaction('withdraw')} style={{ flex: 1, padding: '10px', background: '#d32f2f', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Withdraw</button>
                      </div>
                    </div>

                    {/* Transaction History Ledger */}
                    <div>
                      <h4 style={{ margin: '0 0 10px 0' }}>Account Ledger History</h4>
                      {transactions.length === 0 ? <p style={{ color: '#777', fontStyle: 'italic', fontSize: '0.9em' }}>No statement entries found.</p> : (
                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9em' }}>
                          <thead>
                            <tr style={{ borderBottom: '2px solid #ccc' }}>
                              <th style={{ paddingBottom: '6px' }}>Date</th>
                              <th style={{ paddingBottom: '6px' }}>Type</th>
                              <th style={{ paddingBottom: '6px' }}>Amount</th>
                            </tr>
                          </thead>
                          <tbody>
                            {transactions.map((tx) => (
                              <tr key={tx.transaction_id} style={{ borderBottom: '1px solid #eee' }}>
                                <td style={{ padding: '8px 0' }}>{new Date(tx.date_time).toLocaleDateString()}</td>
                                <td style={{ padding: '8px 0' }}><span style={{ color: tx.type === 'deposit' ? 'green' : 'red', fontWeight: 'bold' }}>{tx.type.toUpperCase()}</span></td>
                                <td style={{ padding: '8px 0', fontWeight: '500' }}>${parseFloat(tx.amount).toFixed(2)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      )}
                    </div>

                  </div>
                )}
              </div>
            )}
          </section>
        </div>

      </div>
    </div>
  );
}

export default App;