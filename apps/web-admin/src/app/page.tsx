export default function Home() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">
          Welcome to MCP Gateway Web Admin Interface
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border bg-card p-6">
          <h3 className="font-semibold">Feature Toggles</h3>
          <p className="text-sm text-muted-foreground mt-2">
            Manage 17 fine-grained feature flags
          </p>
          <a
            href="/admin/features"
            className="text-sm text-primary hover:underline mt-4 inline-block"
          >
            View Features →
          </a>
        </div>

        <div className="rounded-lg border bg-card p-6">
          <h3 className="font-semibold">Virtual Servers</h3>
          <p className="text-sm text-muted-foreground mt-2">
            Manage virtual server lifecycle
          </p>
          <a
            href="/admin/servers"
            className="text-sm text-primary hover:underline mt-4 inline-block"
          >
            View Servers →
          </a>
        </div>

        <div className="rounded-lg border bg-card p-6">
          <h3 className="font-semibold">Gateway Status</h3>
          <p className="text-sm text-muted-foreground mt-2">
            Monitor gateway health and metrics
          </p>
          <a
            href="/admin/gateways"
            className="text-sm text-primary hover:underline mt-4 inline-block"
          >
            View Status →
          </a>
        </div>
      </div>
    </div>
  );
}
