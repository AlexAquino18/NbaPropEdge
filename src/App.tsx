import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Analytics } from "@vercel/analytics/react";
import Home from "./pages/Home";
import GameDetail from "./pages/GameDetail";
import BestProps from "./pages/BestProps";
import HowItWorks from "./pages/HowItWorks";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import About from "./pages/About";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,
      refetchOnWindowFocus: false,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner position="top-center" />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/props" element={<BestProps />} />
          <Route path="/how-it-works" element={<HowItWorks />} />
          <Route path="/game/:gameId" element={<GameDetail />} />
          <Route path="/privacy-policy" element={<PrivacyPolicy />} />
          <Route path="/about" element={<About />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
      <Analytics />
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
