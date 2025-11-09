import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ConfigProvider, App as AntdApp } from "antd";
import "antd/dist/reset.css";
import "./index.css";
import App from "./App.tsx";

const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ConfigProvider
          theme={{
            token: {
              colorPrimary: "#1677ff",
            },
          }}
        >
          <AntdApp>
            <App />
          </AntdApp>
        </ConfigProvider>
      </QueryClientProvider>
    </BrowserRouter>
  </StrictMode>,
);
