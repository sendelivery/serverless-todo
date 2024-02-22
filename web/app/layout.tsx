import type { Metadata } from "next";
import Image from "next/image";
import { Inter } from "next/font/google";
import styles from "@/styles/root-layout.css";
import utilStyles from "@/styles/utilities.css";

const inter = Inter({ subsets: ["latin"], weight: "variable" });

export const metadata: Metadata = {
  title: "Serverless Todo",
  description:
    "A simple web app for keeping track of the things you have... to do.",
  icons: "/icon.svg",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className={styles.header}>
          <Image src="/icon.svg" alt="Todo Logo" width={108} height={108} />
          <h1 className={utilStyles.heading2Xl}>Serverless Todo</h1>
        </div>
        <div className={styles.container}>{children}</div>
      </body>
    </html>
  );
}
