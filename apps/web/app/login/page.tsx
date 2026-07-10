import { Suspense } from "react";
import LoginForm from "@/components/auth/LoginForm";

export const dynamic = "force-dynamic";

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gradient-to-b from-night-950 to-night-900 flex items-center justify-center">Loading...</div>}>
      <LoginForm />
    </Suspense>
  );
}
