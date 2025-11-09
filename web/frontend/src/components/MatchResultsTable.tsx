import { Table } from "antd";
import type { ColumnsType } from "antd/es/table";
import type { Match } from "../types/biometric";

interface MatchResultsTableProps {
  matches: Match[];
  loading?: boolean;
}

const columns: ColumnsType<Match> = [
  {
    title: "User ID",
    dataIndex: "user_id",
    key: "user_id",
  },
  {
    title: "Score",
    dataIndex: "score",
    key: "score",
    render: (score: number) => score.toFixed(4),
  },
  {
    title: "Metadata",
    dataIndex: "metadata",
    key: "metadata",
    render: (metadata: Record<string, unknown>) => (
      <pre style={{ margin: 0 }}>{JSON.stringify(metadata ?? {}, null, 2)}</pre>
    ),
  },
];

export function MatchResultsTable({ matches, loading }: MatchResultsTableProps) {
  return (
    <Table
      rowKey={(record) => record.user_id}
      columns={columns}
      dataSource={matches}
      pagination={false}
      loading={loading}
    />
  );
}

