'use client';




export default function SettingsPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-white mb-6">Branch Settings</h1>

      <div className="flex flex-col gap-6">
        {/* Card 1 — Branch Location */}
        <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Branch Location</h2>

          {/* Map embed */}
          {/* TODO: GET /api/v1/branches/{branch_id} — branch_id comes from GET /api/v1/auth/me after login */}
          <div className="w-full h-64 rounded-lg overflow-hidden mb-4 bg-[#2E2E2E]">
            <iframe
              src="about:blank"
              className="w-full h-full"
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              title="Branch Location Map"
            />
          </div>

          {/* Address */}
          <p className="text-[#A1A1A1] text-sm mb-5">
            No. 42, Baseline Road, Colombo 09
          </p>

          {/* TODO: Wire to PATCH /api/v1/branches/{branch_id} when available */}
          <button className="w-full border border-blue-600 text-blue-600 rounded-lg py-2.5 font-medium hover:bg-blue-600 hover:text-white transition-colors">
            Edit Location
          </button>
        </div>

        {/* Card 2 — Driver Commission Rate */}
        <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Driver Commission Rate</h2>

          {/* TODO: Replace with dynamic value from branch.default_commission_rate */}
          {/* GET /api/v1/branches/{branch_id} returns default_commission_rate — not hardcoded */}
          <p className="text-5xl font-bold text-white mb-3">10%</p>

          <p className="text-[#6B7280] text-sm">
            Automatically calculated on trip completion. 10% of total COD collected per trip.
          </p>
        </div>
      </div>
    </div>
  );
}
