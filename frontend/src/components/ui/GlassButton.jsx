import React from 'react';
import { cn } from '../../lib/utils'; // Assuming cn exists

export const GlassButton = React.forwardRef(({ className, variant = 'primary', size = 'default', children, ...props }, ref) => {
  return (
    <button
      ref={ref}
      className={cn(
        "relative inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-300",
        "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
        "glass-glare backdrop-blur-md border",
        "hover:-translate-y-[2px] active:scale-[0.97]",
        {
          "bg-indigo-500/20 text-indigo-100 border-indigo-500/30 hover:bg-indigo-500/30 hover:shadow-[0_0_20px_rgba(99,102,241,0.25)]": variant === 'primary',
          "bg-white/5 text-slate-200 border-white/10 hover:bg-white/10 hover:shadow-[0_0_20px_rgba(255,255,255,0.1)]": variant === 'secondary',
          "bg-transparent border-transparent text-slate-300 hover:bg-white/5 hover:text-white": variant === 'ghost',
          "h-9 px-4 py-2": size === 'default',
          "h-8 rounded-md px-3 text-xs": size === 'sm',
          "h-10 rounded-md px-8": size === 'lg',
          "px-6 py-3 text-base": size === 'xl', // Used for landing page buttons
        },
        className
      )}
      {...props}
    >
      <span className="relative z-10 flex items-center justify-center gap-2">
        {children}
      </span>
    </button>
  );
});

GlassButton.displayName = "GlassButton";
