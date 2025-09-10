import Image from "next/image";
import CesiumViewer from "./components/cesiumViewer";
import Link from "next/link";

export default function Home() {
  return (
    <div className="parent">
      <nav className="navbar">
        <Link href="" className="nav_link active">Dashboard</Link>
        <Link href="" className="nav_link">Trajectory</Link>
        <Link href="" className="nav_link">Statistics</Link>
      </nav>
      <CesiumViewer />
    </div>
  );
}
