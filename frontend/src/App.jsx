import { useEffect, useState } from "react";

const API = "/api/books";
const STATUSES = ["to-read", "reading", "finished"];
const empty = { title: "", author: "", status: "to-read", rating: "" };

async function request(url, options) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return res.status === 204 ? null : res.json();
}

const payload = (b) => ({ ...b, rating: b.rating === "" ? null : Number(b.rating) });

export default function App() {
  const [books, setBooks] = useState([]);
  const [form, setForm] = useState(empty);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  const load = () =>
    request(API).then(setBooks).catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      if (editingId) {
        await request(`${API}/${editingId}`, { method: "PUT", body: JSON.stringify(payload(form)) });
      } else {
        await request(API, { method: "POST", body: JSON.stringify(payload(form)) });
      }
      setForm(empty);
      setEditingId(null);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const edit = (b) => {
    setEditingId(b.id);
    setForm({ title: b.title, author: b.author, status: b.status, rating: b.rating ?? "" });
  };

  const remove = async (id) => {
    await request(`${API}/${id}`, { method: "DELETE" }).catch((e) => setError(e.message));
    load();
  };

  return (
    <main className="container">
      <h1>Reading List</h1>
      {error && <p className="error">{error}</p>}

      <form onSubmit={submit} className="card form">
        <input
          required
          placeholder="Title"
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
        />
        <input
          required
          placeholder="Author"
          value={form.author}
          onChange={(e) => setForm({ ...form, author: e.target.value })}
        />
        <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
          {STATUSES.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
        <input
          type="number"
          min="1"
          max="5"
          placeholder="Rating 1-5"
          value={form.rating}
          onChange={(e) => setForm({ ...form, rating: e.target.value })}
        />
        <button type="submit">{editingId ? "Save" : "Add book"}</button>
      </form>

      <ul className="list">
        {books.length === 0 && <li className="card muted">No books yet. Add your first one above.</li>}
        {books.map((b) => (
          <li key={b.id} className="card row">
            <div>
              <strong>{b.title}</strong>
              <div className="muted">
                {b.author} · <span className={`badge ${b.status}`}>{b.status}</span>
                {b.rating ? ` · ${"★".repeat(b.rating)}` : ""}
              </div>
            </div>
            <div className="actions">
              <button onClick={() => edit(b)}>Edit</button>
              <button className="danger" onClick={() => remove(b.id)}>
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </main>
  );
}
