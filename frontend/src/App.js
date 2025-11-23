import { useState, useEffect } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import { Upload, FileText, History, LogIn, UserPlus, Download, TrendingUp, Activity, Gauge } from 'lucide-react';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { toast } from 'sonner';
import ExcelUpload from './components/ExcelUpload';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend);

// Using environment variable for API base URL
const API = process.env.REACT_APP_BACKEND_URL || "/api";

function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // ❗ Correct endpoints (NO double /api)
      const endpoint = isLogin
        ? "/auth/login/"
        : "/auth/register/";

      // ❗ Correct payload:
      const payload = isLogin
        ? {
            username: formData.username,  // login with username
            password: formData.password,
          }
        : {
            username: formData.username,
            email: formData.email,
            password: formData.password,
          };

      console.log("POST →", `${API}${endpoint}`, payload);

      const response = await axios.post(`${API}${endpoint}`, payload);

      if (isLogin) {
        localStorage.setItem('token', response.data.token);
        toast.success("Login successful!");
        navigate("/dashboard");
      } else {
        toast.success("Registration successful! Please login.");
        setIsLogin(true);
      }
    } catch (error) {
      console.log("Registration error:", error.response?.data); // Debug log

      if (error.response?.status === 404) {
        const data = error.response.data;
        if (data.error === "user not registered") {
          alert("user not registered");
          toast.error("user not registered");
        } else {
          toast.error("User not found");
        }
        return;
      }

      if (error.response?.status === 400) {
        const data = error.response.data;

        // Check for custom error messages
        if (data.error) {
          if (data.error === "Email already registered") {
            alert("Email already registered");
            toast.error("Email already registered");
          } else if (data.error === "Username already taken") {
            toast.error("Username already taken");
          } else if (data.error === "User not found") {
            alert("User not found");
            toast.error("User not found");
          } else {
            toast.error(data.error);
          }
          return;
        }

        // Check for field-specific errors (Django REST framework format)
        if (data.email && Array.isArray(data.email)) {
          if (data.email.some(msg => msg.toLowerCase().includes('already exists') || msg.toLowerCase().includes('unique') || msg.toLowerCase().includes('already registered'))) {
            alert("Email already registered");
            toast.error("Email already registered");
          } else {
            toast.error(data.email.join(', '));
          }
          return;
        }

        if (data.username && Array.isArray(data.username)) {
          if (data.username.some(msg => msg.toLowerCase().includes('already exists') || msg.toLowerCase().includes('unique'))) {
            toast.error("Username already taken");
          } else {
            toast.error(data.username.join(', '));
          }
          return;
        }

        // Handle other validation errors
        const errorMessages = [];
        for (const [field, messages] of Object.entries(data)) {
          if (Array.isArray(messages)) {
            errorMessages.push(...messages);
          } else {
            errorMessages.push(messages);
          }
        }

        if (errorMessages.length > 0) {
          toast.error(errorMessages.join(', '));
        } else {
          toast.error("Registration failed");
        }
      } else {
        toast.error("Authentication failed");
      }
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-layout">
        {/* Left Section - Marketing */}
        <div className="marketing-section">
          <div className="marketing-content">
            <h1 className="marketing-headline">Chemical Equipment Visualizer</h1>
            <p className="marketing-subtext">Please login/register to continue</p>
          </div>
        </div>

        {/* Right Section - Form Card */}
        <div className="form-section">
          <div className="auth-card">
            <div className="auth-header">
              <div className="logo-icon">
                <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
                  <path d="M10 15 Q20 5 30 15 Q40 25 30 35 Q20 45 10 35 Z" fill="none" stroke="#8b5cf6" strokeWidth="2" opacity="0.8"/>
                  <path d="M15 20 Q20 10 25 20 Q30 30 25 40" fill="none" stroke="#06b6d4" strokeWidth="1.5" opacity="0.6"/>
                  <circle cx="20" cy="20" r="3" fill="#3b82f6" opacity="0.9"/>
                </svg>
              </div>
              <h1>Chemical Equipment Visualizer</h1>
              <p>Data-driven insights for industrial equipment</p>
            </div>

            <div className="auth-tabs">
              <button className={isLogin ? "active" : ""} onClick={() => setIsLogin(true)}>
                <LogIn size={18} /> Login
              </button>
              <button className={!isLogin ? "active" : ""} onClick={() => setIsLogin(false)}>
                <UserPlus size={18} /> Register
              </button>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              {/* Username field */}
              <div className="form-group">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  required
                />
              </div>

              {/* Email shown only during registration */}
              {!isLogin && (
                <div className="form-group">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required={!isLogin}
                  />
                </div>
              )}

              {/* Password */}
              <div className="form-group">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                />
              </div>

              <Button type="submit" className="w-full">
                {isLogin ? "Login" : "Register"}
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

function Dashboard() {
  const [datasets, setDatasets] = useState([]);
  const [currentData, setCurrentData] = useState(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/');
      return;
    }
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    const token = localStorage.getItem('token');
    try {
      const response = await axios.get(`${API}/history/`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      setDatasets(response.data);
    } catch (error) {
      console.error("Error fetching history:", error);
    }
  };

  const loadDataset = async (datasetId) => {
    const token = localStorage.getItem('token');
    try {
      const response = await axios.get(`${API}/datasets/${datasetId}/`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      setCurrentData(response.data);
    } catch (error) {
      toast.error("Error loading dataset");
    }
  };
  const handleUpload = async () => {
    if (!file) {
      toast.error("Please select a file");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    const token = localStorage.getItem('token');
    formData.append("token", token);

    try {
      const response = await axios.post(`${API}/upload/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success("File uploaded successfully!");
      setCurrentData({
        id: response.data.dataset_id,
        filename: file.name,
        summary: response.data.summary,
        data: response.data.data,
        uploaded_at: new Date().toISOString(),
      });

      setFile(null);
      fetchHistory();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = async () => {
    if (!currentData) return;

    const token = localStorage.getItem('token');

    try {
      const response = await axios.get(`${API}/report/pdf/${currentData.id}/`, {
        headers: { "Authorization": `Bearer ${token}` },
        responseType: "blob"
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `report_${currentData.filename}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success("PDF downloaded successfully!");
    } catch (error) {
      toast.error("Error generating PDF");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  const typeDistData = currentData?.summary?.type_distribution
    ? {
        labels: Object.keys(currentData.summary.type_distribution),
        datasets: [
          {
            label: "Equipment Type Distribution",
            data: Object.values(currentData.summary.type_distribution),
            backgroundColor: [
              "rgba(99, 179, 237, 0.8)",
              "rgba(88, 166, 255, 0.8)",
              "rgba(67, 147, 195, 0.8)",
              "rgba(118, 200, 255, 0.8)",
              "rgba(77, 171, 245, 0.8)",
            ],
            borderColor: [
              "rgba(99, 179, 237, 1)",
              "rgba(88, 166, 255, 1)",
              "rgba(67, 147, 195, 1)",
              "rgba(118, 200, 255, 1)",
              "rgba(77, 171, 245, 1)",
            ],
            borderWidth: 2,
          },
        ],
      }
    : null;

  const avgStatsData = currentData?.summary
    ? {
        labels: ["Flowrate", "Pressure", "Temperature"],
        datasets: [
          {
            label: "Average Values",
            data: [
              currentData.summary.avg_flowrate,
              currentData.summary.avg_pressure,
              currentData.summary.avg_temperature,
            ],
            backgroundColor: "rgba(88, 166, 255, 0.7)",
            borderColor: "rgba(88, 166, 255, 1)",
            borderWidth: 2,
          },
        ],
      }
    : null;

  return (
    <div className="dashboard">
      <nav className="navbar">
        <div className="nav-brand">
          <Activity size={32} />
          <span>EquipData Visualizer</span>
        </div>
        <div className="nav-actions">
          <Button variant="outline" onClick={handleLogout}>
            Logout
          </Button>
        </div>
      </nav>

      <div className="hero-banner">
        <div className="hero-content">
          <h1>Chemical Equipment Analytics</h1>
          <p>Advanced visualization and insights for industrial equipment performance</p>
          <div className="molecular-art">
            <svg viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="molGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style={{stopColor:'#3b82f6', stopOpacity:0.6}} />
                  <stop offset="50%" style={{stopColor:'#8b5cf6', stopOpacity:0.6}} />
                  <stop offset="100%" style={{stopColor:'#10b981', stopOpacity:0.6}} />
                </linearGradient>
              </defs>
              <path d="M50 50 Q100 20 150 50 Q200 80 250 50 Q300 20 350 50" stroke="url(#molGradient)" strokeWidth="2" fill="none" />
              <circle cx="50" cy="50" r="3" fill="#3b82f6" opacity="0.8" />
              <circle cx="150" cy="50" r="3" fill="#8b5cf6" opacity="0.8" />
              <circle cx="250" cy="50" r="3" fill="#10b981" opacity="0.8" />
              <circle cx="350" cy="50" r="3" fill="#f59e0b" opacity="0.8" />
              <line x1="50" y1="50" x2="150" y2="50" stroke="#3b82f6" strokeWidth="1" opacity="0.5" />
              <line x1="150" y1="50" x2="250" y2="50" stroke="#8b5cf6" strokeWidth="1" opacity="0.5" />
              <line x1="250" y1="50" x2="350" y2="50" stroke="#10b981" strokeWidth="1" opacity="0.5" />
            </svg>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        <aside className="sidebar">
          <div className="upload-section">
            <h3>
              <Upload size={20} /> Upload CSV
            </h3>
            <ExcelUpload onFileChange={setFile} />
            {file && <p className="file-name">{file.name}</p>}
            <Button onClick={handleUpload} disabled={loading} className="w-full">
              {loading ? "Uploading..." : "Upload & Analyze"}
            </Button>
          </div>

          <div className="history-section">
            <h3>
              <History size={20} /> Recent Datasets
            </h3>
            <div className="dataset-list">
              {datasets.map((dataset) => (
                <div
                  key={dataset.id}
                  className={`dataset-item ${currentData?.id === dataset.id ? "active" : ""}`}
                  onClick={() => loadDataset(dataset.id)}
                >
                  <FileText size={16} />
                  <div>
                    <div className="dataset-name">{dataset.filename}</div>
                    <div className="dataset-date">
                      {new Date(dataset.uploaded_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>

        <main className="main-content">
          {currentData ? (
            <>
              <div className="content-header">
                <div>
                  <h2>{currentData.filename}</h2>
                  <p>
                    Uploaded:{" "}
                    {new Date(currentData.uploaded_at || Date.now()).toLocaleString()}
                  </p>
                </div>
                <Button onClick={downloadPDF}>
                  <Download size={18} /> Download PDF Report
                </Button>
              </div>

              <div className="stats-grid">
                <Card className="stat-card">
                  <CardHeader>
                    <div className="stat-icon blue">
                      <Gauge size={24} />
                    </div>
                    <CardTitle>Equipment Count</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="stat-value">{currentData.summary.equipment_count}</div>
                  </CardContent>
                </Card>

                <Card className="stat-card">
                  <CardHeader>
                    <div className="stat-icon teal">
                      <TrendingUp size={24} />
                    </div>
                    <CardTitle>Avg Flowrate</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="stat-value">
                      {currentData.summary.avg_flowrate.toFixed(2)}
                    </div>
                  </CardContent>
                </Card>

                <Card className="stat-card">
                  <CardHeader>
                    <div className="stat-icon purple">
                      <Activity size={24} />
                    </div>
                    <CardTitle>Avg Pressure</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="stat-value">
                      {currentData.summary.avg_pressure.toFixed(2)}
                    </div>
                  </CardContent>
                </Card>

                <Card className="stat-card">
                  <CardHeader>
                    <div className="stat-icon orange">
                      <Activity size={24} />
                    </div>
                    <CardTitle>Avg Temperature</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="stat-value">
                      {currentData.summary.avg_temperature.toFixed(2)}
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="charts-grid">
                <Card className="chart-card">
                  <CardHeader>
                    <CardTitle>Equipment Type Distribution</CardTitle>
                    <CardDescription>Distribution of equipment by type</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {typeDistData && (
                      <Pie
                        data={typeDistData}
                        options={{ maintainAspectRatio: true, aspectRatio: 2 }}
                      />
                    )}
                  </CardContent>
                </Card>

                <Card className="chart-card">
                  <CardHeader>
                    <CardTitle>Average Parameter Values</CardTitle>
                    <CardDescription>Mean values across all equipment</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {avgStatsData && (
                      <Bar
                        data={avgStatsData}
                        options={{ maintainAspectRatio: true, aspectRatio: 2 }}
                      />
                    )}
                  </CardContent>
                </Card>
              </div>

              <Card className="data-table-card">
                <CardHeader>
                  <CardTitle>Equipment Data</CardTitle>
                  <CardDescription>First 100 records</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="table-container">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Equipment Name</th>
                          <th>Type</th>
                          <th>Flowrate</th>
                          <th>Pressure</th>
                          <th>Temperature</th>
                        </tr>
                      </thead>
                      <tbody>
                        {currentData.data?.slice(0, 100).map((row, idx) => (
                          <tr key={idx}>
                            <td>{row["Equipment Name"]}</td>
                            <td>{row["Type"]}</td>
                            <td>{row["Flowrate"]}</td>
                            <td>{row["Pressure"]}</td>
                            <td>{row["Temperature"]}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <div className="empty-state">
              <Upload size={64} />
              <h2>No Data Yet</h2>
              <p>Upload a CSV file to get started with equipment analysis</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AuthPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;