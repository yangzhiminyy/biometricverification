import { type ComponentRef, useEffect, useRef, useState } from "react";
import {
  App as AntdApp,
  Button,
  Card,
  Divider,
  Form,
  Image,
  Input,
  InputNumber,
  Select,
  Space,
  Typography,
} from "antd";
import { CameraOutlined, DeleteOutlined } from "@ant-design/icons";
import { useModalities } from "../hooks/useModalities";
import { useVerify } from "../hooks/useVerify";
import { MatchResultsTable } from "../components/MatchResultsTable";
import type { VerificationResponse } from "../types/biometric";
import ReactWebcam from "react-webcam";

interface VerifyFormValues {
  modality: string;
  sample: string;
  topK?: number;
}

export function VerifyPage() {
  const [form] = Form.useForm<VerifyFormValues>();
  const { notification } = AntdApp.useApp();
  const [result, setResult] = useState<VerificationResponse | null>(null);
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const webcamRef = useRef<ComponentRef<typeof ReactWebcam>>(null);
  const [capturedSample, setCapturedSample] = useState<string | null>(null);
  const {
    data: modalitiesData,
    isLoading: loadingModalities,
    isError: modalitiesError,
    error: modalitiesErrorObj,
  } = useModalities();

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
    const sampleToSend = capturedSample ?? values.sample;
    if (!sampleToSend) {
      notification.error({ message: "Verification failed", description: "Please input a sample or capture a photo." });
      return;
    }
    verifyMutation.mutate({
      modality: values.modality,
      sample: sampleToSend,
      topK: values.topK,
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
      setCapturedSample(imageSrc);
      form.setFieldsValue({ sample: "" });
      notification.success({ message: "Captured", description: "Photo captured successfully." });
    } else {
      notification.error({ message: "Capture failed", description: "Unable to capture from camera." });
    }
  };

  const handleRemoveCaptured = () => {
    setCapturedSample(null);
  };

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
            rules={[
              {
                validator: async (_, value) => {
                  if (!value && !capturedSample) {
                    throw new Error("Please input sample or capture a photo");
                  }
                  return Promise.resolve();
                },
              },
            ]}
          >
            <Input.TextArea placeholder="sample_frame_1" rows={4} />
          </Form.Item>

          <Form.Item name="topK" label="Top K">
            <InputNumber min={1} max={10} style={{ width: 120 }} placeholder="5" />
          </Form.Item>

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

            {capturedSample && (
              <Card type="inner" title="Captured Photo">
                <Space direction="vertical">
                  <Image src={capturedSample} width={200} style={{ borderRadius: 8 }} alt="captured-sample" />
                  <Button icon={<DeleteOutlined />} size="small" onClick={handleRemoveCaptured}>
                    Remove
                  </Button>
                </Space>
              </Card>
            )}
          </Space>

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

