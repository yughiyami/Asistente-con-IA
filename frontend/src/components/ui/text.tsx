import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const textVariants = cva(
  "",
  {
    variants: {
      variant: {
        h1: "",
        h2: "",
        h3: "",
        span: "",
        default: "text-md font-medium",
      },
      size: {
        default: "",
        sm: "",
        md: "",
        lg: "",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Text({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"p"> &
  VariantProps<typeof textVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "p"

  return (
    <Comp
      data-slot="p"
      className={cn(textVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Text, textVariants }
