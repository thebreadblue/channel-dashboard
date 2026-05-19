import { Bell, UserCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface HeaderProps {
  title: string;
  newOrderCount?: number;
}

export function Header({ title, newOrderCount = 0 }: HeaderProps) {
  return (
    <header className="h-16 border-b border-slate-200 bg-white flex items-center justify-between px-6 shrink-0">
      <h1 className="text-base font-semibold text-slate-800">{title}</h1>

      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" className="relative text-slate-500 hover:text-slate-800">
          <Bell className="w-5 h-5" />
          {newOrderCount > 0 && (
            <Badge className="absolute -top-1 -right-1 h-4 min-w-4 px-1 text-[10px] bg-rose-500 border-0">
              {newOrderCount}
            </Badge>
          )}
        </Button>
        <Button variant="ghost" size="icon" className="text-slate-500 hover:text-slate-800">
          <UserCircle className="w-5 h-5" />
        </Button>
      </div>
    </header>
  );
}
