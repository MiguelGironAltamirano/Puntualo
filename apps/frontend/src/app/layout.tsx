import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://puntualo.app";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Puntualo — Elige al docente ideal con datos",
    template: "%s · Puntualo",
  },
  description:
    "Decisiones académicas respaldadas por datos. Encuentra perfiles detallados, comparativas estructuradas y el consenso real de los estudiantes, con síntesis potenciada por IA.",
  applicationName: "Puntualo",
  keywords: [
    "elegir docente",
    "reseñas de profesores",
    "universidad",
    "comparar docentes",
    "Puntualo",
    "evaluación docente",
  ],
  authors: [{ name: "Puntualo EdTech" }],
  openGraph: {
    type: "website",
    locale: "es_ES",
    url: siteUrl,
    siteName: "Puntualo",
    title: "Puntualo — Elige al docente ideal con datos",
    description:
      "Reseñas, métricas y síntesis por IA para elegir profesor con confianza, no de oído.",
    images: [{ url: "/puntualo_logo.png", width: 110, height: 30, alt: "Puntualo" }],
  },
  twitter: {
    card: "summary",
    title: "Puntualo — Elige al docente ideal con datos",
    description:
      "Reseñas, métricas y síntesis por IA para elegir profesor con confianza, no de oído.",
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0284c7",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased bg-white text-slate-900`}
    >
      <body className="min-h-full text-slate-900 overflow-x-hidden">
        {children}
      </body>
    </html>
  );
}
