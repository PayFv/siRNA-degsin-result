"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useI18n } from "@/components/i18n-provider";
import { PageShell } from "@/components/page-shell";
import { ResultsView } from "@/components/results/results-view";
import { DESIGN_RESULT_STORAGE_KEY } from "@/lib/design-input";
import { resultData } from "@/lib/result-data";
import type { SirnaResult } from "@/lib/sirna-types";

export function ResultsPageClient() {
  const { t } = useI18n();
  const [result, setResult] = useState<SirnaResult | null>(null);
  const [source, setSource] = useState<"live" | "mock">("mock");

  useEffect(() => {
    const stored = window.sessionStorage.getItem(DESIGN_RESULT_STORAGE_KEY);
    if (!stored) {
      setResult(resultData);
      setSource("mock");
      return;
    }

    try {
      setResult(JSON.parse(stored) as SirnaResult);
      setSource("live");
    } catch {
      setResult(resultData);
      setSource("mock");
    }
  }, []);

  if (!result) {
    return (
      <PageShell
        footerLeft={t("footerLoading")}
        footerRight={
          <Link href="/" className="hover:text-slate-600">
            {t("newDesign")}
          </Link>
        }
      >
        <p className="py-16 text-sm text-slate-500">{t("loadingResults")}</p>
      </PageShell>
    );
  }

  return (
    <PageShell
      footerLeft={
        source === "live" ? t("footerLive") : t("footerMock")
      }
      footerRight={
        <Link href="/" className="hover:text-slate-600">
          {t("newDesign")}
        </Link>
      }
    >
      <ResultsView result={result} />
    </PageShell>
  );
}
