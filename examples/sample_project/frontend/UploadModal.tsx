import { useEffect, useState } from "react";

// Intentional drift: frontend expects `name`, backend returns `title`.
// Sample: readers assumed authenticated via cookie elsewhere (no Authorization header on fetch).

export function UploadModal({ id }: { id: string }) {
  const [name, setName] = useState<string>("");

  useEffect(() => {
    async function load() {
      const res = await fetch(`/api/projects/${id}/detail`);
      const data = await res.json();
      setName(data.name);
    }
    load().catch(() => undefined);
  }, [id]);

  return <div>{name}</div>;
}
