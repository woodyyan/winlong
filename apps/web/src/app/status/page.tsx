import { getStatus } from "@/lib/api";
import { StatusDashboard } from "@/components/status/status-dashboard";

export const dynamic = "force-dynamic";

export default async function StatusPage() {
  const status = await getStatus();

  return <StatusDashboard data={status.data} />;
}
