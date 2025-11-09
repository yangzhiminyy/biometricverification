import { useState } from "react";
import { Button, Card, Form, Input, Select, Space, notification, Typography } from "antd";
import { MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";
import { useModalities } from "../hooks/useModalities";
import { useEnroll } from "../hooks/useEnroll";

interface EnrollFormValues {
  modality: string;
  userId: string;
  samples: string[];
}

export function EnrollPage() {
  const [form] = Form.useForm<EnrollFormValues>();
  const { data: modalitiesData, isLoading: loadingModalities } = useModalities();
  const [result, setResult] = useState<string | null>(null);

  const enrollMutation = useEnroll(
    (data) => {
      notification.success({ message: "Enrollment succeeded", description: `User ${data.user_id} enrolled.` });
      setResult(JSON.stringify(data, null, 2));
      form.resetFields(["samples"]);
    },
    (error) => {
      notification.error({ message: "Enrollment failed", description: error.message });
    },
  );

  const onFinish = (values: EnrollFormValues) => {
    enrollMutation.mutate({
      modality: values.modality,
      userId: values.userId,
      samples: values.samples.filter(Boolean),
    });
  };

  const modalities = modalitiesData?.modalities ?? [];

  return (
    <Space direction="vertical" style={{ width: "100%" }} size="large">
      <Typography.Title level={4}>Enroll User</Typography.Title>
      <Card>
        <Form form={form} layout="vertical" onFinish={onFinish} initialValues={{ samples: [""] }}>
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
            name="userId"
            label="User ID"
            rules={[{ required: true, message: "Please input user ID" }]}
          >
            <Input placeholder="demo_user" />
          </Form.Item>

          <Form.List name="samples" rules={[{ validator: async (_, samples) => {
              if (!samples || samples.length === 0 || samples.every((sample: string) => !sample)) {
                return Promise.reject(new Error("Please provide at least one sample"));
              }
            } }]}
          >
            {(fields, { add, remove }, { errors }) => (
              <>
                {fields.map((field, index) => (
                  <Form.Item
                    {...field}
                    key={field.key}
                    label={index === 0 ? "Samples" : ""}
                    required={false}
                  >
                    <Space align="baseline">
                      <Form.Item
                        {...field}
                        noStyle
                        rules={[{ required: true, whitespace: true, message: "Sample cannot be empty" }]}
                      >
                        <Input placeholder="sample_frame_1" style={{ width: 300 }} />
                      </Form.Item>
                      {fields.length > 1 ? (
                        <MinusCircleOutlined onClick={() => remove(field.name)} />
                      ) : null}
                    </Space>
                  </Form.Item>
                ))}
                <Form.Item>
                  <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                    Add sample
                  </Button>
                  <Form.ErrorList errors={errors} />
                </Form.Item>
              </>
            )}
          </Form.List>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={enrollMutation.isPending}>
              Enroll
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {result && (
        <Card title="Enrollment Response">
          <pre style={{ margin: 0 }}>{result}</pre>
        </Card>
      )}
    </Space>
  );
}

