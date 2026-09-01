"use client";

import Link from "next/link";
import { DesignForm } from "@/components/design/design-form";
import { useI18n } from "@/components/i18n-provider";
import { PageShell } from "@/components/page-shell";

export default function Home() {
  const { t } = useI18n();

  return (
    <PageShell
      footerLeft={t("footerDesign")}
      footerRight={
        <Link href="/results" className="hover:text-slate-600">
          {t("viewSampleResults")}
        </Link>
      }
    >
      <DesignForm />
    </PageShell>
  );
}
