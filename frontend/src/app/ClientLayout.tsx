// ClientLayout.tsx (componente cliente)
"use client";

import { useEffect, useState } from "react";

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Aquí puedes usar hooks de React
  const [isLoaded, setIsLoaded] = useState(false);
  
  useEffect(() => {
    // Tu lógica de efecto aquí
    setIsLoaded(true);
    console.log("Componente cliente montado");
  }, []);

  return (
    <div className={`app-container ${isLoaded ? "loaded" : ""}`}>
      {children}
    </div>
  );
}