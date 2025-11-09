import { type ComponentRef, useEffect, useRef, useState } from "react";
import { App as AntdApp, Button, Card, Divider, Form, Image, Input, List, Select, Space, Typography } from "antd";
import { CameraOutlined, DeleteOutlined, MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";
import ReactWebcam from "react-webcam";
import { useModalities } from "../hooks/useModalities";
import { useEnroll } from "../hooks/useEnroll";

interface EnrollFormValues {
  modality: string;
  userId: string;
  samples: string[];
}

export function EnrollPage() {
  const [form] = Form.useForm<EnrollFormValues>();
  const { notification } = AntdApp.useApp();
  const {
    data: modalitiesData,
    isLoading: loadingModalities,
    isError: modalitiesError,
    error: modalitiesErrorObj,
  } = useModalities();
  const [result, setResult] = useState<string | null>(null);
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const webcamRef = useRef<ComponentRef<typeof ReactWebcam>>(null);
  const [capturedSamples, setCapturedSamples] = useState<string[]>([]);

  const enrollMutation = useEnroll(
    (data) => {
      notification.success({ message: "Enrollment succeeded", description: `User ${data.user_id} enrolled.` });
      setResult(JSON.stringify(data, null, 2));
      form.resetFields(["samples"]);
      setCapturedSamples([]);
    },
    (error) => {
      notification.error({ message: "Enrollment failed", description: error.message });
    },
  );

  const onFinish = (values: EnrollFormValues) => {
    const manualSamples = values.samples?.filter(Boolean) ?? [];
    const combinedSamples = [...manualSamples, ...capturedSamples];

    if (combinedSamples.length === 0) {
      notification.error({ message: "Enrollment failed", description: "Please provide at least one sample." });
      return;
    }

    enrollMutation.mutate({
      modality: values.modality,
      userId: values.userId,
      samples: combinedSamples,
    });
  };

  useEffect(() => {
    if (modalitiesError && modalitiesErrorObj) {
      notification.error({
        message: "Failed to load modalities",
        description: modalitiesErrorObj.message,
      });
    }
  }, [modalitiesError, modalitiesErrorObj]);

  const modalities = modalitiesData?.modalities?.length ? modalitiesData.modalities : ["face"];

  useEffect(() => {
    if (!form.getFieldValue("modality") && modalities.length > 0) {
      form.setFieldsValue({ modality: modalities[0] });
    }
  }, [modalities, form]);

  const handleToggleCamera = () => {
    setCameraEnabled((prev) => !prev);
  };

  const handleCapture = () => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      setCapturedSamples((prev) => [...prev, imageSrc]);
      notification.success({ message: "Captured", description: "Photo captured successfully." });
    } else {
      notification.error({ message: "Capture failed", description: "Unable to capture from camera." });
    }
  };

  const handleRemoveCaptured = (index: number) => {
    setCapturedSamples((prev) => prev.filter((_, i) => i !== index));
  };

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

          <Form.List
            name="samples"
            rules={[
              {
                validator: async (_, samples) => {
              const hasManual = samples && samples.some((sample: string) => Boolean(sample));
              if (!hasManual && capturedSamples.length === 0) {
                return Promise.reject(new Error("Please provide at least one sample or capture a photo"));
              }
                  return Promise.resolve();
                },
              },
            ]}
          >
            {(fields, { add, remove }, { errors }) => (
              <>
                {fields.map(({ key, name, ...restField }, index) => (
                  <Form.Item key={key} label={index === 0 ? "Samples" : ""} required={false}>
                    <Space align="baseline">
                      <Form.Item
                        {...restField}
                        name={name}
                        noStyle
                        rules={[{ required: true, whitespace: true, message: "Sample cannot be empty" }]}
                      >
                        <Input placeholder="sample_frame_1" style={{ width: 300 }} />
                      </Form.Item>
                      {fields.length > 1 ? <MinusCircleOutlined onClick={() => remove(name)} /> : null}
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

          <Divider />

          <Space direction="vertical" style={{ width: "100%" }}>
            <Space>
              <Button icon={<CameraOutlined />} onClick={handleToggleCamera}>
                {cameraEnabled ? "Disable Camera" : "Enable Camera"}
              </Button>
              {cameraEnabled && (
                <Button type="primary" onClick={handleCapture}>
                  Capture Photo
                </Button>
              )}
            </Space>

            {cameraEnabled && (
              <div style={{ maxWidth: 480 }}>
                <ReactWebcam
                  ref={webcamRef}
                  audio={false}
                  screenshotFormat="image/jpeg"
                  videoConstraints={{ facingMode: "user", width: 480 }}
                  style={{ width: "100%", borderRadius: 8, border: "1px solid #d9d9d9" }}
                />
              </div>
            )}

            {capturedSamples.length > 0 && (
              <Card type="inner" title="Captured Photos">
                <List
                  grid={{ gutter: 16, column: 3 }}
                  dataSource={capturedSamples}
                  renderItem={(item, index) => (
                    <List.Item>
                      <Space direction="vertical">
                        <Image
                          src={item}
                          width={140}
                          style={{ borderRadius: 8 }}
                          alt={`captured-${index}`}
                        />
                        <Button
                          icon={<DeleteOutlined />}
                          size="small"
                          onClick={() => handleRemoveCaptured(index)}
                        >
                          Remove
                        </Button>
                      </Space>
                    </List.Item>
                  )}
                />
              </Card>
            )}
          </Space>

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

