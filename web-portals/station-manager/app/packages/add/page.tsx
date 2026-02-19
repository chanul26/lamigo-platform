"use client"
import { useRouter } from "next/navigation"

export default function AddPackagePage() {
  {/* Created a constant router to enable navigation back to the packages page when the "Cancel" button is clicked */}
  const router = useRouter()

  return (
    <div className="p-8">{/* Main container that holds the page content with padding */}

      {/* Page title */}
      <h1 className="text-2xl font-semibold mb-6" style={{ color: "var(--text-primary)" }}>
        Add New Package
      </h1>

      {/* Tab container that holds the buttons to switch between manual entry and bulk upload */}
      <div className="flex gap-2 mb-6">
        <button className="btn-primary" style={{ borderRadius: "var(--border-radius-sm)", padding: "8px 20px" }}>
          Manual Entry
        </button>
        <button style={{ backgroundColor: "transparent", color: "var(--text-muted)", border: "none", padding: "8px 20px", cursor: "pointer" }}>
          Bulk Upload
        </button>
      </div>

      {/* Form card that contains all the input fields for adding a new package */}
      <div className="card p-8">

        {/* Form group for the package number input field */}
        <div className="mb-5">
          <label className="block mb-2 text-sm font-medium" style={{ color: "var(--text-primary)" }}>Package Number</label>
          <input className="w-full p-3 text-sm rounded-lg" placeholder="e.g. PKG-2024-00123"
            style={{ backgroundColor: "var(--card-bg-hover)", border: "1px solid var(--border-color)", color: "var(--text-primary)" }} />
        </div>

        {/* Two column layout for receiver name and phone number fields */}
        <div className="grid grid-cols-2 gap-4 mb-5">
          <div>
            <label className="block mb-2 text-sm font-medium" style={{ color: "var(--text-primary)" }}>Receiver Name</label>
            <input className="w-full p-3 text-sm rounded-lg" placeholder="Saman Perera"
              style={{ backgroundColor: "var(--card-bg-hover)", border: "1px solid var(--border-color)", color: "var(--text-primary)" }} />
          </div>
          <div>
            <label className="block mb-2 text-sm font-medium" style={{ color: "var(--text-primary)" }}>Phone Number</label>
            <input className="w-full p-3 text-sm rounded-lg" placeholder="07x-xxx-xxxx"
              style={{ backgroundColor: "var(--card-bg-hover)", border: "1px solid var(--border-color)", color: "var(--text-primary)" }} />
          </div>
        </div>

        {/* Form group for the address input field */}
        <div className="mb-5">
          <label className="block mb-2 text-sm font-medium" style={{ color: "var(--text-primary)" }}>Address</label>
          <input className="w-full p-3 text-sm rounded-lg" placeholder="House No, Street Name"
            style={{ backgroundColor: "var(--card-bg-hover)", border: "1px solid var(--border-color)", color: "var(--text-primary)" }} />
        </div>

        {/* Two column layout for city/area and COD amount fields */}
        <div className="grid grid-cols-2 gap-4 mb-5">
          <div>
            <label className="block mb-2 text-sm font-medium" style={{ color: "var(--text-primary)" }}>City/Area</label>
            <input className="w-full p-3 text-sm rounded-lg"
              style={{ backgroundColor: "var(--card-bg-hover)", border: "1px solid var(--border-color)", color: "var(--text-primary)" }} />
          </div>
          <div>
            <label className="block mb-2 text-sm font-medium" style={{ color: "var(--text-primary)" }}>COD Amount (LKR)</label>
            <input className="w-full p-3 text-sm rounded-lg" placeholder="0.00"
              style={{ backgroundColor: "var(--card-bg-hover)", border: "1px solid var(--border-color)", color: "var(--text-primary)" }} />
          </div>
        </div>

        {/* Form group for the note/description input field */}
        <div className="mb-6">
          <label className="block mb-2 text-sm font-medium" style={{ color: "var(--text-primary)" }}>Note / Description</label>
          <input className="w-full p-3 text-sm rounded-lg" placeholder="e.g. Fragile"
            style={{ backgroundColor: "var(--card-bg-hover)", border: "1px solid var(--border-color)", color: "var(--text-primary)" }} />
        </div>

        {/* Helper text to inform the user about the package submission process */}
        <p className="text-sm mb-6" style={{ color: "var(--text-muted)" }}>
          Package will be added to inventory and assigned to a driver.
        </p>

        {/* Action buttons - Cancel navigates back to packages page, Add to Inventory submits the form */}
        <div className="flex gap-3">
          <button onClick={() => router.push("/packages")}
            style={{ padding: "12px 24px", borderRadius: "var(--border-radius-sm)", border: "1px solid var(--border-color)", backgroundColor: "transparent", color: "var(--text-primary)", cursor: "pointer" }}>
            Cancel
          </button>
          <button className="btn-primary" style={{ flex: 1 }}
            onClick={() => console.log("Add to inventory clicked")}>
            Add to Inventory
          </button>
        </div>

      </div>
    </div>
  )
}