import { redirect } from "next/navigation";

export default function NotFound() {
   const token = typeof window !== "undefined" ? window.localStorage.getItem("nixai_token") : null;
    if (!token) {
      redirect("/auth/login");
    }
  redirect("/documents");
}
