import { Card, Col, Row, Space, Statistic, Typography } from "antd";
import { Link } from "react-router-dom";
import { useModalities } from "../hooks/useModalities";

export function Dashboard() {
  const { data, isLoading } = useModalities();

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Typography.Title level={4}>Overview</Typography.Title>
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic title="Enabled Modalities" value={data?.modalities.length ?? 0} loading={isLoading} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Typography.Paragraph>
              <Link to="/enroll">Go to Enrollment</Link>
            </Typography.Paragraph>
            <Typography.Paragraph>
              <Link to="/verify">Go to Verification</Link>
            </Typography.Paragraph>
            <Typography.Paragraph>
              <Link to="/user">Lookup User</Link>
            </Typography.Paragraph>
          </Card>
        </Col>
      </Row>
      <Card title="Available Modalities">
        {isLoading ? (
          <Typography.Text>Loading...</Typography.Text>
        ) : (
          <Space direction="vertical">
            {(data?.modalities ?? []).map((modality) => (
              <Typography.Text key={modality}>{modality}</Typography.Text>
            ))}
          </Space>
        )}
      </Card>
    </Space>
  );
}

