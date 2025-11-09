import { Layout, Menu, Typography } from "antd";
import { Link, Outlet, useLocation } from "react-router-dom";
import { useMemo } from "react";

const { Header, Content, Footer, Sider } = Layout;

const menuItems = [
  { key: "/", label: <Link to="/">Dashboard</Link> },
  { key: "/enroll", label: <Link to="/enroll">Enroll</Link> },
  { key: "/verify", label: <Link to="/verify">Verify</Link> },
  { key: "/user", label: <Link to="/user">User Detail</Link> },
];

export function MainLayout() {
  const location = useLocation();

  const selectedKeys = useMemo(() => {
    const match = menuItems.find((item) => location.pathname.startsWith(item.key));
    return match ? [match.key] : [];
  }, [location.pathname]);

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider collapsible>
        <div style={{ padding: "16px", textAlign: "center" }}>
          <Typography.Title level={4} style={{ color: "white", margin: 0 }}>
            Biometric Console
          </Typography.Title>
        </div>
        <Menu theme="dark" mode="inline" selectedKeys={selectedKeys} items={menuItems} />
      </Sider>
      <Layout>
        <Header style={{ background: "white", padding: "0 24px" }}>
          <Typography.Title level={3} style={{ margin: 0 }}>
            Biometric Verification Platform
          </Typography.Title>
        </Header>
        <Content style={{ margin: "24px" }}>
          <div style={{ padding: 24, background: "white", minHeight: 360 }}>
            <Outlet />
          </div>
        </Content>
        <Footer style={{ textAlign: "center" }}>Biometric Platform © {new Date().getFullYear()}</Footer>
      </Layout>
    </Layout>
  );
}

