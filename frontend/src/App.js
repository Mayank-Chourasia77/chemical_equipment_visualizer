import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, Download, BarChart3, FileSpreadsheet } from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import './App.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const API_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchLatestData();
    fetchHistory();
  }, []);

  const fetchLatestData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_URL}/api/latest/`);
      setData(response.data);
    } catch (err) {
      if (err.response?.status !== 404) {
        setError(err.response?.data?.error || 'Failed to fetch data');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      setError('Please upload a CSV file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      setError(null);
      setUploadSuccess(false);
      const response = await axios.post(`${API_URL}/api/upload/`, formData);
      setData(response.data);
      fetchHistory();
      setUploadSuccess(true);
      setTimeout(() => setUploadSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload file');
    } finally {
      setLoading(false);
      event.target.value = '';
    }
  };

  const fetchHistory = async () => {
    try {
      // Load the last 5 uploads for the history section.
      const response = await axios.get(`${API_URL}/api/history/`);
      setHistory(response.data);
    } catch (err) {
      setHistory([]);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/pdf/`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'equipment_report.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to download PDF');
    }
  };

  const chartData = data?.stats?.equipment_distribution
    ? {
        labels: Object.keys(data.stats.equipment_distribution),
        datasets: [
          {
            label: 'Equipment Count',
            data: Object.values(data.stats.equipment_distribution),
            backgroundColor: 'rgba(59, 130, 246, 0.8)',
            borderColor: 'rgba(59, 130, 246, 1)',
            borderWidth: 2,
          },
        ],
      }
    : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            family: 'Inter',
            size: 12,
          },
        },
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0,
          font: {
            family: 'Inter',
          },
        },
      },
      x: {
        ticks: {
          font: {
            family: 'Inter',
          },
        },
      },
    },
  };

  const formatAverage = (value) => (Number.isFinite(value) ? value.toFixed(2) : '-');

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Chemical Equipment Visualizer</h1>
          <p className="text-lg text-gray-600">Upload and analyze chemical equipment data</p>
        </div>

        <div className="mb-6 flex flex-wrap gap-4">
          <div>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              className="hidden"
              id="csv-upload"
              data-testid="csv-upload-input"
            />
            <label htmlFor="csv-upload">
              <Button
                data-testid="upload-button"
                asChild
                className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white"
                disabled={loading}
              >
                <span>
                  <Upload className="mr-2 h-4 w-4" />
                  {loading ? 'Uploading...' : 'Upload CSV'}
                </span>
              </Button>
            </label>
          </div>

          {data && (
            <Button
              data-testid="download-pdf-button"
              onClick={handleDownloadPDF}
              variant="outline"
              className="border-blue-600 text-blue-600 hover:bg-blue-50"
            >
              <Download className="mr-2 h-4 w-4" />
              Download PDF Report
            </Button>
          )}
        </div>

        {error && (
          <div
            data-testid="error-message"
            className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700"
          >
            {error}
          </div>
        )}

        {uploadSuccess && (
          <div
            data-testid="success-message"
            className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700"
          >
            CSV uploaded successfully!
          </div>
        )}

        {loading && !data && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}

        {data && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card data-testid="total-equipment-card" className="border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <CardDescription className="text-gray-600">Total Equipment</CardDescription>
                  <CardTitle className="text-3xl font-bold text-gray-900">
                    {data.stats.total_equipment}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <FileSpreadsheet className="h-8 w-8 text-blue-600" />
                </CardContent>
              </Card>

              <Card data-testid="avg-flowrate-card" className="border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <CardDescription className="text-gray-600">Avg Flowrate</CardDescription>
                  <CardTitle className="text-3xl font-bold text-gray-900">
                    {data.stats.average_flowrate.toFixed(2)}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <BarChart3 className="h-8 w-8 text-green-600" />
                </CardContent>
              </Card>

              <Card data-testid="avg-pressure-card" className="border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <CardDescription className="text-gray-600">Avg Pressure</CardDescription>
                  <CardTitle className="text-3xl font-bold text-gray-900">
                    {data.stats.average_pressure.toFixed(2)}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <BarChart3 className="h-8 w-8 text-orange-600" />
                </CardContent>
              </Card>

              <Card data-testid="avg-temperature-card" className="border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <CardDescription className="text-gray-600">Avg Temperature</CardDescription>
                  <CardTitle className="text-3xl font-bold text-gray-900">
                    {data.stats.average_temperature.toFixed(2)}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <BarChart3 className="h-8 w-8 text-red-600" />
                </CardContent>
              </Card>
            </div>

            {chartData && (
              <Card data-testid="equipment-distribution-chart" className="mb-8 border-gray-200 shadow-sm">
                <CardHeader>
                  <CardTitle className="text-gray-900">Equipment Type Distribution</CardTitle>
                  <CardDescription className="text-gray-600">
                    Distribution of equipment by type
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-80">
                    <Bar data={chartData} options={chartOptions} />
                  </div>
                </CardContent>
              </Card>
            )}

            <Card data-testid="equipment-table" className="mb-8 border-gray-200 shadow-sm">
              <CardHeader>
                <CardTitle className="text-gray-900">Equipment Data</CardTitle>
                <CardDescription className="text-gray-600">
                  Detailed view of all equipment
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Equipment Name</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Type</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Flowrate</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Pressure</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Temperature</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.data.map((row, index) => (
                        <tr
                          key={index}
                          data-testid={`equipment-row-${index}`}
                          className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                        >
                          <td className="py-3 px-4 text-gray-900">{row['Equipment Name']}</td>
                          <td className="py-3 px-4 text-gray-700">{row['Type']}</td>
                          <td className="py-3 px-4 text-gray-700">{row['Flowrate']}</td>
                          <td className="py-3 px-4 text-gray-700">{row['Pressure']}</td>
                          <td className="py-3 px-4 text-gray-700">{row['Temperature']}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            {history.length > 0 && (
              <Card data-testid="upload-history" className="mb-8 border-gray-200 shadow-sm">
                <CardHeader>
                  <CardTitle className="text-gray-900">Upload History</CardTitle>
                  <CardDescription className="text-gray-600">
                    Last 5 uploads
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-gray-200">
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Upload Time</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Total Equipment</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Avg Flowrate</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Avg Pressure</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Avg Temperature</th>
                        </tr>
                      </thead>
                      <tbody>
                        {history.map((upload) => (
                          <tr
                            key={upload.id}
                            className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                          >
                            <td className="py-3 px-4 text-gray-900">
                              {new Date(upload.uploaded_at).toLocaleString()}
                            </td>
                            <td className="py-3 px-4 text-gray-700">
                              {Number.isFinite(upload.total_equipment) ? upload.total_equipment : '-'}
                            </td>
                            <td className="py-3 px-4 text-gray-700">
                              {formatAverage(upload.average_flowrate)}
                            </td>
                            <td className="py-3 px-4 text-gray-700">
                              {formatAverage(upload.average_pressure)}
                            </td>
                            <td className="py-3 px-4 text-gray-700">
                              {formatAverage(upload.average_temperature)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {!data && !loading && (
          <Card data-testid="empty-state" className="border-gray-200 shadow-sm">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <FileSpreadsheet className="h-16 w-16 text-gray-400 mb-4" />
              <p className="text-gray-600 text-lg mb-2">No data available</p>
              <p className="text-gray-500 text-sm">Upload a CSV file to get started</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

export default App;
