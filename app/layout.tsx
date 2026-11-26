import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Website Voice Assistant",
  description: "A simple voice assistant for the websites you use.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
