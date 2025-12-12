"use client";

import Script from "next/script";
import { usePathname } from "next/navigation";

const TEMPLATE_PAGES = ["/custom-template", "/template-preview"];

export function ReactGrabProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isDev = process.env.NODE_ENV === "development";

  // Only load on template pages in development
  const shouldLoad = isDev && TEMPLATE_PAGES.some(p => pathname?.startsWith(p));

  return (
    <>
      {children}
      {shouldLoad && (
        <>
          <Script
            src="https://unpkg.com/react-grab/dist/index.global.js"
            strategy="afterInteractive"
          />
          <Script
            src="https://unpkg.com/@react-grab/claude-code/dist/client.global.js"
            strategy="afterInteractive"
          />
        </>
      )}
    </>
  );
}
