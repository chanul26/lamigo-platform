"use client"
import { useRouter } from "next/navigation"
import { PACKAGES } from "./data"

function formatStatus(status: string) {
  return status.replace(/_/g, " ")
}

function getStatusClass(status: string) {
  switch (status) {
    case "TO_BE_DELIVERED": return "status-badge status-pending"
    case "ASSIGNED": return "status-badge status-in-transit"
    case "ONGOING": return "status-badge status-in-transit"
    case "COMPLETED": return "status-badge status-delivered"
    case "FAILED": return "status-badge status-failed"
    default: return "status-badge status-pending"
  }
}

export default function PackagesPage() {
  const router = useRouter()

  return (
    <div className="p-8">

      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-semibold" style={{ color: "var(--text-primary)" }}>
          Packages
        </h1>
        <button
          className="btn-primary"
          onClick={() => router.push("/packages/add")}
        >
          + Add New Package
        </button>
      </div>

      {/* Table */}
      <div className="card">
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border-color)" }}>
              <th className="p-4 text-left text-sm font-semibold" style={{ color: "var(--text-secondary)" }}>Package ID</th>
              <th className="p-4 text-left text-sm font-semibold" style={{ color: "var(--text-secondary)" }}>Status</th>
              <th className="p-4 text-left text-sm font-semibold" style={{ color: "var(--text-secondary)" }}>Location</th>
              <th className="p-4 text-left text-sm font-semibold" style={{ color: "var(--text-secondary)" }}>Phone Number</th>
              <th className="p-4 text-left text-sm font-semibold" style={{ color: "var(--text-secondary)" }}>Address</th>
            </tr>
          </thead>
          <tbody>
            {PACKAGES.map((pkg) => (
              <tr key={pkg.id} className="card-hover" style={{ borderBottom: "1px solid var(--border-color)" }}>
                <td className="p-4 font-semibold" style={{ color: "var(--text-primary)" }}>#{pkg.id}</td>
                <td className="p-4">
                  <span className={getStatusClass(pkg.status)}>
                    {formatStatus(pkg.status)}
                  </span>
                </td>
                <td className="p-4">
                  <img
                    src={pkg.location === "verified" ? "Icons/Location_Available.svg" : "Icons/Location_Unavailable.svg"}
                    alt={pkg.location}
                    style={{ width: "60px", height: "60px", verticalAlign: "middle" }}
                  />
                </td>
                <td className="p-4" style={{ color: "var(--text-secondary)", whiteSpace: "nowrap" }}>{pkg.phone}</td>
                <td className="p-4" style={{ color: "var(--text-secondary)" }}>{pkg.address}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  )
}