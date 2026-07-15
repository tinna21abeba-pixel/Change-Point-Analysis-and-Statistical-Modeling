import { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
} from 'recharts';

function App() {
  const [summary, setSummary] = useState(null);
  const [prices, setPrices] = useState([]);
  const [returns, setReturns] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch('/api/summary').then(res => res.json()),
      fetch('/api/prices').then(res => res.json()),
      fetch('/api/returns').then(res => res.json()),
      fetch('/api/events').then(res => res.json()),
    ])
      .then(([summaryData, pricesData, returnsData, eventsData]) => {
        setSummary(summaryData);
        setPrices(pricesData);
        setReturns(returnsData);
        setEvents(eventsData);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="app-shell"><p>Loading dashboard…</p></div>;
  }

  const metrics = summary?.metrics || {};
  const eventRows = Array.isArray(events) ? events : [];

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Task 3 • Interactive Dashboard</p>
          <h1>Brent Oil Change Point Dashboard</h1>
          <p className="lead">
            Explore structural breaks in Brent oil log returns and compare them with the key events catalog.
          </p>
        </div>
      </header>

      <section className="cards">
        <article className="card">
          <h3>Detected change point</h3>
          <p className="value">{summary?.change_point_date || '—'}</p>
        </article>
        <article className="card">
          <h3>Observations</h3>
          <p className="value">{metrics.n_observations || 0}</p>
        </article>
        <article className="card">
          <h3>Mean return</h3>
          <p className="value">{(metrics.mean_return || 0).toFixed(6)}</p>
        </article>
        <article className="card">
          <h3>Std. return</h3>
          <p className="value">{(metrics.std_return || 0).toFixed(6)}</p>
        </article>
      </section>

      <section className="panel-grid">
        <div className="panel">
          <h2>Historical Brent price series</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={prices.slice(0, 500)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={false} />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="price" stroke="#2563eb" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="panel">
          <h2>Log returns</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={returns.slice(0, 500)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={false} />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="log_return" stroke="#dc2626" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="panel">
        <h2>Nearby events</h2>
        <div className="event-list">
          {eventRows.length ? eventRows.slice(0, 8).map((event, index) => (
            <div key={`${event.event_name}-${index}`} className="event-card">
              <strong>{event.event_name || 'Event'}</strong>
              <p>{event.description || 'No description provided.'}</p>
            </div>
          )) : <p>No event matches were found for the detected change point.</p>}
        </div>
      </section>
    </div>
  );
}

export default App;
