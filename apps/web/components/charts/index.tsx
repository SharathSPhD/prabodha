// Placeholder chart components (future: D3 or SVG rendering)

export function BarChart({
  data,
}: {
  data: Array<{ label: string; value: number }>;
}) {
  return (
    <div className="h-64 flex items-end gap-2">
      {data.map((d, i) => (
        <div key={i} className="flex-1 flex flex-col items-center">
          <div
            className="w-full bg-indigo-600 rounded-t"
            style={{ height: `${(d.value / Math.max(...data.map(x => x.value))) * 100}%` }}
          />
          <p className="text-xs text-slate-500 mt-2">{d.label}</p>
        </div>
      ))}
    </div>
  );
}

export function LineChart({
  data,
}: {
  data: Array<{ x: number; y: number }>;
}) {
  // TODO: D3 or SVG line chart
  return <div className="h-64 bg-night-800 rounded-lg flex items-center justify-center text-slate-500">Line chart (coming soon)</div>;
}
