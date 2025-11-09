import { useEffect, useState } from "react";
import { App as AntdApp, Button, Card, Form, Input, Select, Space, Typography, List } from "antd";
import { useModalities } from "../hooks/useModalities";
import { useUserDetail } from "../hooks/useUserDetail";
import { useDeleteUser } from "../hooks/useDeleteUser";

interface UserFormValues {
  modality: string;
  userId: string;
}

export function UserDetailPage() {
  const [form] = Form.useForm<UserFormValues>();
  const { notification } = AntdApp.useApp();
  const [selectedModality, setSelectedModality] = useState<string>();
  const [selectedUser, setSelectedUser] = useState<string>();
  const {
    data: modalitiesData,
    isLoading: loadingModalities,
    isError: modalitiesError,
    error: modalitiesErrorObj,
  } = useModalities();

  const { data: userData, isFetching } = useUserDetail(
    selectedModality,
    selectedUser,
    Boolean(selectedModality && selectedUser),
  );

  const deleteMutation = useDeleteUser(
    selectedModality ?? "",
    () => {
      notification.success({ message: "User deleted" });
      setSelectedUser(undefined);
      form.resetFields(["userId"]);
    },
    (error) => notification.error({ message: "Delete failed", description: error.message }),
  );

  const onFinish = (values: UserFormValues) => {
    setSelectedModality(values.modality);
    setSelectedUser(values.userId);
  };

  const handleDelete = () => {
    if (selectedUser && selectedModality) {
      deleteMutation.mutate(selectedUser);
    }
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

  return (
    <Space direction="vertical" style={{ width: "100%" }} size="large">
      <Typography.Title level={4}>User Detail</Typography.Title>
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
            name="userId"
            label="User ID"
            rules={[{ required: true, message: "Please input user ID" }]}
          >
            <Input placeholder="demo_user" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={isFetching}>
                Load
              </Button>
              <Button danger onClick={handleDelete} loading={deleteMutation.isPending} disabled={!selectedUser}>
                Delete
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {isFetching && <Typography.Text>Loading user data...</Typography.Text>}

      {userData && (
        <Card title={`User: ${userData.user_id}`}>
          <Space direction="vertical" style={{ width: "100%" }}>
            <Typography.Text>Modality: {userData.modality}</Typography.Text>
            <Typography.Title level={5}>Stored Samples</Typography.Title>
            <List
              dataSource={userData.samples ?? []}
              bordered
              locale={{ emptyText: "No samples stored" }}
              renderItem={(item) => <List.Item>{item}</List.Item>}
            />
          </Space>
        </Card>
      )}
    </Space>
  );
}

