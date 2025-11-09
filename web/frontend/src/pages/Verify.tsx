import { useState } from "react";
import { Button, Card, Form, Input, InputNumber, Select, Space, Typography, notification } from "antd";
import { useModalities } from "../hooks/useModalities";
import { useVerify } from "../hooks/useVerify";
import { MatchResultsTable } from "../components/MatchResultsTable";
import type { VerificationResponse } from "../types/biometric";

interface VerifyFormValues {
  modality: string;
  sample: string;
  topK?: number;
}

export function VerifyPage() {
  const [form] = Form.useForm<VerifyFormValues>();
  const [result, setResult] = useState<VerificationResponse | null>(null);
  const { data: modalitiesData, isLoading: loadingModalities } = useModalities();

  const verifyMutation = useVerify(
    (data) => {
      setResult(data);
      notification.success({
        message: "Verification completed",
        description: data.decision ? "Match found above threshold" : "No match above threshold",
      });
    },
    (error) => {
      notification.error({ message: "Verification failed", description: error.message });
    },
  );

  const onFinish = (values: VerifyFormValues) => {
    verifyMutation.mutate({
      modality: values.modality,
      sample: values.sample,
      topK: values.topK,
    });
  };

  const modalities = modalitiesData?.modalities ?? [];

  return (
    <Space direction="vertical" style={{ width: "100%" }} size="large">
      <Typography.Title level={4}>Verify Sample</Typography.Title>
      <Card>
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item
            name="modality"
            label="Modality"
            rules={[{ required: true, message: "Please select modality" }]}
          >
            <Select
              placeholder="Select modality"
              loading={loadingModalities}
              options={modalities.map((modality) => ({ label: modality, value: modality }))}
            />
          </Form.Item>

          <Form.Item
            name="sample"
            label="Sample"
            rules={[{ required: true, message: "Please input sample" }]}
          >
            <Input.TextArea placeholder="sample_frame_1" rows={4} />
          </Form.Item>

          <Form.Item name="topK" label="Top K">
            <InputNumber min={1} max={10} style={{ width: 120 }} placeholder="5" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={verifyMutation.isPending}>
              Verify
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {result && (
        <Card title="Verification Results">
          <Space direction="vertical" style={{ width: "100%" }}>
            <Typography.Text>
              Decision: <strong>{result.decision ? "MATCH" : "NO MATCH"}</strong>
            </Typography.Text>
            <Typography.Text>Threshold: {result.threshold}</Typography.Text>
            <MatchResultsTable matches={result.matches} />
          </Space>
        </Card>
      )}
    </Space>
  );
}

