import { getStatus, getWinlongList } from "@/lib/api";
import { RankingExplorer } from "@/components/pool/ranking-explorer";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [listResponse, statusResponse] = await Promise.all([getWinlongList(), getStatus()]);

  return <RankingExplorer initialList={listResponse.data} initialStatus={statusResponse.data} />;
}
