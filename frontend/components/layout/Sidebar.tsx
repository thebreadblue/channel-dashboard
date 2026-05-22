"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", label: "대시보드", icon: LayoutDashboard },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex flex-col w-56 shrink-0 border-r border-slate-200 bg-white h-screen sticky top-0">
      <div className="flex items-center gap-2 px-5 h-16 border-b border-slate-200">
        <div className="w-7 h-7 rounded-md bg-slate-900 flex items-center justify-center">
          <span className="text-white text-xs font-bold">B</span>
        </div>
        <span className="font-bold text-sm text-slate-800 leading-tight">
          더브레드블루<br />
          <span className="text-xs font-normal text-slate-400">OMS</span>
        </span>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname === "/";
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                active
                  ? "bg-slate-900 text-white"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              )}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
