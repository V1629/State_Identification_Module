import React from 'react';
import { cn } from '../../lib/utils'; // Assuming cn exists in shadcn setup

export function GlassCard({ className, children, ...props }) {
  return (
    <div
      className={cn(
        "glass-panel p-6 transition-all duration-300 hover:bg-white/20 dark:hover:bg-[#121214]/60",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
