'use client';

export default function TrackingPage() {
    return (
        <div className="min-h-screen bg-[#FFF8F0] p-4">

            {/* Header */}
            <div className="max-w-md mx-auto">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Hi, Customer!</h1>
                        <p className="text-gray-500 text-sm">You have 1 shipment arriving soon</p>
                    </div>
                    <div className="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center">
                        👤
                    </div>
                </div>

                {/* Order Info Card */}
                <div className="bg-[#FFE8D6] rounded-2xl p-4 mb-4">

                    {/* Order header */}
                    <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-xl bg-white/50 flex items-center justify-center">
                            📦
                        </div>
                        <div>
                            <p className="font-semibold text-gray-900">Order ID : 212090</p>
                            <p className="text-sm text-gray-600">Cash on Delivery Rs.500.00</p>
                        </div>
                    </div>

                    {/* Delivery estimate */}
                    <p className="text-sm text-gray-700 mb-4">
                        Your order will be delivered <strong>tomorrow between 11:00 am - 11:15 am</strong>
                    </p>

                    {/* Member C adds buttons here */}

                </div>

            </div>
        </div>
    );
}