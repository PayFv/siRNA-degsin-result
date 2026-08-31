import { ResultsView } from "@/components/results/results-view";
import { resultData } from "@/lib/result-data";

export default function Home() {
  return (
    <main className="min-h-screen">
      <div className="mx-auto w-full max-w-[1280px] sm:px-6 sm:py-8 lg:px-10 lg:py-12">
        <div className="bg-white px-4 py-6 sm:rounded-2xl sm:px-8 sm:py-7 sm:shadow-[0_1px_2px_rgba(15,23,42,0.04)] lg:px-10">
          <ResultsView result={resultData} />
        </div>
        <footer className="mt-4 flex flex-col gap-1 px-4 pb-5 text-[11px] text-slate-400 sm:mt-5 sm:flex-row sm:items-center sm:justify-between sm:px-1 sm:pb-0">
          <span>Mock result · no design algorithm is executed</span>
          <span>siRNA candidate visualization</span>
        </footer>
      </div>
    </main>
  );
}
