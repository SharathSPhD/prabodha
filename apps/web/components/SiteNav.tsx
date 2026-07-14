"use client";

/**
 * Shared top navigation for all app pages.
 *
 * Previously only the landing page had a nav; Studio/Theatre/Labs/Results/Glossary
 * were dead ends with no way back. This gives every page a consistent, on-brand
 * header with active-route highlighting.
 */
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/studio", label: "Studio" },
  { href: "/theatre", label: "Theatre" },
  { href: "/labs", label: "Labs" },
  { href: "/results", label: "Results" },
  { href: "/glossary", label: "Glossary" },
];

export function SiteNav() {
  const pathname = usePathname();

  return (
    <nav className="sticky top-0 z-50 border-b border-night-600 bg-night-900/70 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3.5">
        <Link
          href="/"
          className="font-serif text-xl font-bold text-gradient transition-opacity hover:opacity-80"
        >
          prabodha
        </Link>

        <div className="flex items-center gap-1 sm:gap-2">
          {LINKS.map((l) => {
            const active = pathname === l.href || pathname?.startsWith(l.href + "/");
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
                  active
                    ? "bg-indigo-500/15 text-indigo-300"
                    : "text-slate-400 hover:text-indigo-300"
                }`}
              >
                {l.label}
              </Link>
            );
          })}
          <a
            href="https://sharathsphd.github.io/prabodha/"
            className="ml-1 hidden rounded-full border border-night-500 px-3 py-1.5 text-sm font-medium text-slate-300 transition-colors hover:border-teal-400/60 hover:text-teal-300 sm:inline-block"
          >
            The essay ↗
          </a>
        </div>
      </div>
    </nav>
  );
}

export default SiteNav;
